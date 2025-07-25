from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.context import FSMContext

from Bot.kbds import reply
from splits.splits_winorient import SplitsWinOrient
from splits.masstart_winorient import MasStartWinOrient
from splits.relay_winorient import RelayWinOrient
from Bot.states.split_states import SplitStates


winorient_router = Router()

@winorient_router.message(SplitStates.winorient_splits)
async def get_group(message: types.Message, state: FSMContext):
    f = True
    data = await state.get_data()
    response = data['response']
    response.encoding = 'utf-8'

    type_distance = data['type_distance']

    if type_distance.lower() == 'заданное направление':
        splits = SplitsWinOrient(response.text)

    elif type_distance.lower() == 'общий старт':
        splits = MasStartWinOrient(response.text)

    elif type_distance.lower() == 'эстафета':
        splits = RelayWinOrient(response.text)

    else:
        f = False

    if f:
        keys = [x for x in splits.groups.keys()]
        for key in keys:
            if not key.isalpha():
                response.encoding = 'windows-1251'
                splits = SplitsWinOrient(response.text)
                break
        await state.update_data(splits=splits)

        groups = [group_name for group_name in splits.groups.keys()]
        await message.answer('Введите одну из предложенных групп', reply_markup=reply.make_group_keyboard(groups))
        await state.set_state(SplitStates.winorient_group)


@winorient_router.message(SplitStates.winorient_group)
async def get_person(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = message.text.strip()
    splits = data['splits']
    if group in splits.groups.keys():
        persons = [person for person in splits.get_persons_by_group(group)]
        await state.update_data(group=group)

        await message.answer('Выберите участника', reply_markup=reply.make_group_keyboard(persons))

        await state.set_state(SplitStates.winorient_name)
    else:
        await message.answer('Такой группы не существует')


@winorient_router.message(SplitStates.winorient_name)
async def sportorg_splits(message: types.Message, state: FSMContext):
    name = message.text.strip()
    data = await state.get_data()
    splits = data['splits']
    group = data['group']
    if name in splits.get_persons_by_group(group):
        await state.update_data(name=name)

        await message.answer('Выберете действие', reply_markup=reply.func_kb)
        await state.set_state(SplitStates.winorient_analiz)
    else:
        await message.answer('Такого участника нет в выбранной группе')



@winorient_router.message(SplitStates.winorient_analiz, F.text.contains('по'))
async def winorient_analiz1(message: types.Message, state: FSMContext):
    data = await state.get_data()

    splits = data['splits']
    group = data['group']
    person = data['name']
    msg = splits.make_person_report(group, person)
    await message.answer(msg)
    await message.answer('Выберете действие', reply_markup=reply.func_kb)


@winorient_router.message(SplitStates.winorient_analiz, F.text.contains('группе'))
async def winorient_analiz2(message: types.Message, state: FSMContext):
    data = await state.get_data()

    data = await state.get_data()
    splits = data['splits']

    group = data['group']
    group_legs = splits.get_group_splits(group)
    for leg in group_legs:
        await message.answer(splits.get_top10_on_leg_in_group(group, leg))

    await message.answer('Выберете действие', reply_markup=reply.func_kb)


@winorient_router.message(SplitStates.winorient_analiz, F.text.contains('всех'))
async def winorient_analiz3(message: types.Message, state: FSMContext):
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


@winorient_router.message(SplitStates.winorient_analiz, F.text.contains('конкретном'))
async def winorient_analiz4_1(message: types.Message, state: FSMContext):
    data = await state.get_data()
    splits = data['splits']
    legs = splits.get_legs()

    await message.answer('Выберите перегон из предложенного списка', reply_markup=reply.make_group_keyboard(legs))


@winorient_router.message(SplitStates.winorient_analiz, F.text.contains('->'))
async def winorient_analiz4_2(message: types.Message, state: FSMContext):
    leg = message.text.strip()

    data = await state.get_data()
    splits = data['splits']

    splits_leg = splits.get_top10_on_leg(leg)

    await message.answer(splits_leg)

@winorient_router.message(SplitStates.winorient_analiz)
async def winorient_analiz(message: types.Message):
    await message.answer('Такой функции не существует.\nВыберите одно из предложенных действий')