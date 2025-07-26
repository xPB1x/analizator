from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.context import FSMContext

from Bot.kbds import reply
from splits.sfr_splits import SFRSplits
from splits.sfr_masstart import SFRMasStart
from Bot.states.split_states import SplitStates


sfr_router = Router()

@sfr_router.message(SplitStates.sfr_splits)
async def get_group(message: types.Message, state: FSMContext):
    f = True
    data = await state.get_data()
    response = data['response']
    response.encoding = 'utf-8'

    type_distance = data['type_distance']
    if type_distance.lower() == 'заданное направление':
        splits = SFRSplits(response.text)
        key = [x for x in splits.groups.keys()][0]
        if not key[0].isalpha():
            response.encoding = 'windows-1251'
            splits = SFRSplits(response.text)

    elif type_distance.lower() == 'общий старт':
        splits = SFRMasStart(response.text)
        key = [x for x in splits.groups.keys()][0]
        if not key[0].isalpha():
            response.encoding = 'windows-1251'
            splits = SFRMasStart(response.text)

    else:
        f = False

    if f:

        await state.update_data(splits=splits)

        groups = [group_name for group_name in splits.groups.keys()]
        await message.answer('Введите одну из предложенных групп', reply_markup=reply.make_group_keyboard(groups))
        await state.set_state(SplitStates.sfr_group)
    else:
        await message.answer('На данный момент, выбранный тип дистанции недостпен для анализа SFR сплитов')
        await state.set_state(SplitStates.waiting_for_type_distance)
        await message.answer('Выберите тип дистанции', reply_markup=reply.types_kb)


@sfr_router.message(SplitStates.sfr_group)
async def get_person(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = message.text.strip()
    splits = data['splits']
    if group in splits.groups.keys():
        persons = [person for person in splits.get_persons_by_group(group)]
        await state.update_data(group=group)

        await message.answer('Выберите участника', reply_markup=reply.make_group_keyboard(persons))

        await state.set_state(SplitStates.sfr_name)
    else:
        await message.answer('Такой группы не существует')


@sfr_router.message(SplitStates.sfr_name)
async def sportorg_splits(message: types.Message, state: FSMContext):
    name = message.text.strip()
    data = await state.get_data()
    splits = data['splits']
    group = data['group']
    if name in splits.get_persons_by_group(group):
        await state.update_data(name=name)

        await message.answer('Выберете действие', reply_markup=reply.func_kb)
        await state.set_state(SplitStates.sfr_analiz)
    else:
        await message.answer('Такого участника нет в выбранной группе')


@sfr_router.message(SplitStates.sfr_analiz, F.text.contains('по'))
async def sfr_analiz1(message: types.Message, state: FSMContext):
    data = await state.get_data()

    splits = data['splits']
    group = data['group']
    person = data['name']
    msg = splits.make_person_report(group, person)
    await message.answer(msg)
    await message.answer('Выберете действие', reply_markup=reply.func_kb)


@sfr_router.message(SplitStates.sfr_analiz, F.text.contains('группе'))
async def sfr_analiz2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    splits = data['splits']

    group = data['group']
    group_legs = splits.get_group_splits(group)
    for leg in group_legs:
        await message.answer(splits.get_top10_on_leg_in_group(group, leg))

    await message.answer('Выберете действие', reply_markup=reply.func_kb)


@sfr_router.message(SplitStates.sfr_analiz, F.text.contains('всех'))
async def sfr_analiz3(message: types.Message, state: FSMContext):
    data = await state.get_data()
    splits = data['splits']
    group = data['group']
    group_legs = splits.get_group_splits(group)
    if len(group_legs) == 2:
        group_legs = group_legs[0]
    for leg in group_legs:
        top = splits.get_top10_on_leg(leg)
        if top:
            await message.answer(top)

    await message.answer('Выберете действие', reply_markup=reply.func_kb)


@sfr_router.message(SplitStates.sfr_analiz, F.text.contains('конкретном'))
async def sfr_analiz4_1(message: types.Message, state: FSMContext):
    data = await state.get_data()
    splits = data['splits']
    legs = splits.get_legs()

    await message.answer('Выберите перегон из предложенного списка', reply_markup=reply.make_group_keyboard(legs))


@sfr_router.message(SplitStates.sfr_analiz, F.text.contains('->'))
async def sfr_analiz4_2(message: types.Message, state: FSMContext):
    leg = message.text.strip()

    data = await state.get_data()
    splits = data['splits']

    splits_leg = splits.get_top10_on_leg(leg)

    await message.answer(splits_leg)

@sfr_router.message(SplitStates.winorient_analiz)
async def winorient_analiz(message: types.Message):
    await message.answer('Такой функции не существует.\nВыберите одно из предложенных действий')
