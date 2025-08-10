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
        keys = [x for x in splits.groups.keys()]
        for key in keys:
            for char in key:
                if not (char.isalpha() or char.isdigit() or char in {' ', '-'}):
                    response.encoding = 'windows-1251'
                    splits = SplitsWinOrient(response.text)
                    break

    elif type_distance.lower() == 'общий старт':
        splits = MasStartWinOrient(response.text)
        keys = [x for x in splits.groups.keys()]
        for key in keys:
            for char in key:
                if not (char.isalpha() or char.isdigit() or char in {' ', '-'}):
                    response.encoding = 'windows-1251'
                    splits = SplitsWinOrient(response.text)
                    break

    elif type_distance.lower() == 'эстафета':
        splits = RelayWinOrient(response.text)
        keys = [x for x in splits.groups.keys()]
        for key in keys:
            for char in key:
                if not (char.isalpha() or char.isdigit() or char in {' ', '-'}):
                    response.encoding = 'windows-1251'
                    splits = SplitsWinOrient(response.text)
                    break

    else:
        f = False

    if f:
        await state.update_data(splits=splits)
        groups = [group_name for group_name in splits.groups.keys()]
        await message.answer('👇Введите одну из предложенных групп♂️♀️', reply_markup=reply.make_group_keyboard(groups))
        await state.set_state(SplitStates.winorient_group)
    else:
        await message.answer('На данный момент, выбранный тип дистанции недостпен для анализа SFR сплитов')
        await state.set_state(SplitStates.waiting_for_type_distance)
        await message.answer('Выберите тип дистанции', reply_markup=reply.types_kb)


@winorient_router.message(SplitStates.winorient_group)
async def get_person(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = message.text.strip()
    splits = data['splits']
    if group in splits.groups.keys():
        persons = splits.get_persons_by_group(group)
        await state.update_data(group=group)

        await message.answer('👇Выберите участника️🧍‍♂️🧍‍', reply_markup=reply.make_group_keyboard(persons))

        await state.set_state(SplitStates.winorient_name)
    else:
        await message.answer('🕵️‍♂️Такой группы не существует🕵️‍♂️')


@winorient_router.message(SplitStates.winorient_name)
async def sportorg_splits(message: types.Message, state: FSMContext):
    name = message.text.strip()
    data = await state.get_data()
    splits = data['splits']
    group = data['group']
    if name in splits.get_persons_by_group(group):
        await state.update_data(name=name)
        await message.answer('👾Выберете действие👾', reply_markup=reply.func_kb)
        await state.set_state(SplitStates.winorient_analiz)

    else:
        await message.answer('🦸‍♂️Такого участника нет в выбранной группе🦸‍♂️')


@winorient_router.message(SplitStates.winorient_analiz, F.text.contains('перегонам'))
async def winorient_analiz1(message: types.Message, state: FSMContext):
    data = await state.get_data()

    splits = data['splits']
    group = data['group']
    person = data['name']
    msg = splits.make_person_report(group, person)
    await message.answer(msg)
    await message.answer('👾Выберете действие👾', reply_markup=reply.func_kb)


@winorient_router.message(SplitStates.winorient_analiz, F.text.contains('группе'))
async def winorient_analiz2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    splits = data['splits']
    group = data['group']
    group_legs = splits.get_group_splits(group)
    for leg in group_legs:
        await message.answer(splits.get_top10_on_leg_in_group(group, leg))

    await message.answer('👾Выберете действие👾', reply_markup=reply.func_kb)


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

    await message.answer('👾Выберете действие👾', reply_markup=reply.func_kb)


@winorient_router.message(SplitStates.winorient_analiz, F.text.contains('конкретном'))
async def winorient_analiz4_1(message: types.Message, state: FSMContext):
    data = await state.get_data()
    splits = data['splits']
    legs = splits.get_legs()

    await message.answer('Выберите перегон из предложенного списка📃', reply_markup=reply.make_group_keyboard(legs))


@winorient_router.message(SplitStates.winorient_analiz, F.text.contains('->'))
async def winorient_analiz4_2(message: types.Message, state: FSMContext):
    leg = message.text.strip()

    data = await state.get_data()
    splits = data['splits']

    splits_leg = splits.get_top10_on_leg(leg)

    await message.answer(splits_leg)


@winorient_router.message(SplitStates.winorient_analiz, F.text.contains('Сравнить'))
async def winorient_analiz(message: types.Message, state: FSMContext):
    await state.set_state(SplitStates.get_count_persons)
    await message.answer('Введите кол-во человек для сравнения', reply_markup=reply.del_kb)

@winorient_router.message(SplitStates.get_count_persons)
async def winorient_get_count_persons(message:types.Message, state:FSMContext):
    count = message.text.strip()
    if count.isdigit() and int(count) >= 0:
        count = int(count)
        data = await state.get_data()
        splits = data['splits']
        group = data['group']
        persons = splits.get_persons_by_group(group)

        await state.update_data(count=count)
        await state.update_data(persons=[])
        await state.set_state(SplitStates.get_names_for_comparing)

        await message.answer('👇Выберите участника️🧍‍♂️🧍‍', reply_markup=reply.make_group_keyboard(persons))
    else:
        await message.answer("Введите ПОЛОЖИТЕЛЬНОЕ ЧИСЛО")

@winorient_router.message(SplitStates.get_names_for_comparing)
async def choose_persons(message:types.Message, state:FSMContext):
    person = message.text.strip()
    data = await state.get_data()
    count = data['count']
    choosen_persons = data['persons']
    group = data['group']
    splits: SplitsWinOrient = data['splits']

    if person in splits.get_persons_by_group(group):
        count -= 1
        choosen_persons.append(person)
        if count > 0:
            persons = splits.get_persons_by_group(group)
            await message.answer(f'Осталось выбрать {count} спортсменов', reply_markup=reply.make_group_keyboard(persons))
            await state.update_data(count=count)
            await state.update_data(persons=choosen_persons)
        else:
            group_legs = splits.get_group_splits(group)
            await message.answer(splits.comparing_peoples(group, choosen_persons))
            await state.set_state(SplitStates.winorient_analiz)
            await message.answer('👾Выберете действие👾', reply_markup=reply.func_kb)
    else:
        await message.answer("Выбран неопознанный спортсмен")
        persons = splits.get_persons_by_group(group)
        await message.answer(f'Осталось выбрать {count} спортсменов', reply_markup=reply.make_group_keyboard(persons))

@winorient_router.message(SplitStates.winorient_analiz)
async def winorient_analiz(message: types.Message):
    await message.answer('🥱Такой функции не существует.🥱\n👇Выберите одно из предложенных действий👇')
