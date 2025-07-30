from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.context import FSMContext

from Bot.kbds import reply
from Bot.states.split_states import SplitStates


sportorg_router = Router()

@sportorg_router.message(SplitStates.sportorg_splits)
async def get_group(message: types.Message, state: FSMContext):
    data = await state.get_data()
    splits = data['splits']
    groups = [group_name for group_name in splits.groups.keys()]

    await message.answer('👇Введите одну из предложенных групп♂️♀️', reply_markup=reply.make_group_keyboard(groups))

    await state.set_state(SplitStates.group_name)


@sportorg_router.message(SplitStates.group_name, or_f(F.text.contains('М'), F.text.contains('Ж')))
async def get_person(message: types.Message, state: FSMContext):
    data = await state.get_data()

    group = message.text.strip()
    splits = data['splits']
    if group in splits.groups.keys():
        persons = splits.get_persons_by_group(group)
        await state.update_data(group=group)

        await message.answer('👇Выберите участника️🧍‍♂️🧍‍♀️', reply_markup=reply.make_group_keyboard(persons))
        await state.set_state(SplitStates.person_name)
    else:
        await message.answer('🕵️‍♂️Такой группы не существует🕵️‍♂️')

@sportorg_router.message(SplitStates.person_name)
async def sportorg_splits(message: types.Message, state: FSMContext):
    name = message.text.strip()
    data = await state.get_data()
    splits = data['splits']
    group = data['group']
    if name in splits.get_persons_by_group(group):
        await state.update_data(name=name)
        await message.answer('👾Выберете действие👾', reply_markup=reply.func_kb)
        await state.set_state(SplitStates.sportorg_analiz)

    else:
        await message.answer('🦸‍♂️Такого участника нет в выбранной группе🦸‍♂️')


@sportorg_router.message(SplitStates.sportorg_analiz, F.text.contains('по'))
async def sportorg_analiz1(message: types.Message, state: FSMContext):
    data = await state.get_data()
    splits = data['splits']
    group = data['group']
    person = data['name']
    msg = splits.make_person_report(group, person)
    await message.answer(msg)
    await message.answer('👾Выберете действие👾', reply_markup=reply.func_kb)


@sportorg_router.message(SplitStates.sportorg_analiz, F.text.contains('группе'))
async def sportorg_analiz2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    splits = data['splits']
    group = data['group']
    group_legs = splits.get_group_splits(group)
    for leg in group_legs:
        await message.answer(splits.get_top10_on_leg_in_group(group, leg))

    await message.answer('👾Выберете действие👾', reply_markup=reply.func_kb)


@sportorg_router.message(SplitStates.sportorg_analiz, F.text.contains('всех'))
async def sportorg_analiz3(message: types.Message, state: FSMContext):
    data = await state.get_data()
    splits = data['splits']
    group = data['group']
    group_legs = splits.get_group_splits(group)
    for leg in group_legs:
        await message.answer(splits.get_top10_on_leg(leg))
    await message.answer('Выберете действие', reply_markup=reply.func_kb)


@sportorg_router.message(SplitStates.sportorg_analiz, F.text.contains('конкретном'))
async def spororg_analiz4_1(message: types.Message, state: FSMContext):
    data = await state.get_data()
    splits = data['splits']
    legs = splits.get_legs()

    await message.answer('Выберите перегон из предложенного списка📃', reply_markup=reply.make_group_keyboard(legs))


@sportorg_router.message(SplitStates.sportorg_analiz, F.text.contains('->'))
async def sportorg_analiz4_2(message: types.Message, state: FSMContext):
    leg = message.text.strip()
    data = await state.get_data()
    splits = data['splits']

    splits_leg = splits.get_top10_on_leg(leg)
    await message.answer(splits_leg)


@sportorg_router.message(SplitStates.sportorg_analiz)
async def sportorg_analiz(message: types.Message):
    await message.answer('🥱Такой функции не существует.🥱\n👇Выберите одно из предложенных действий👇')