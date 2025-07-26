from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f, StateFilter
from aiogram.fsm.context import FSMContext

from selenium import webdriver
from selenium.webdriver.common.by import By

from Bot.kbds import reply
from Bot.states.split_states import SplitStates


back_router = Router()
@back_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()

    if current_state is None:
        await message.answer('Ниже некуда')

    previous_state = None
    for step in SplitStates.__all_states__:
        print(step)
        if step.state == current_state:
            await state.set_state(previous_state)
            break
        previous_state = step
    if previous_state == SplitStates.waiting_for_url:
        await message.answer('Салам алейкум', reply_markup=reply.start_kb)

    elif previous_state == SplitStates.waiting_for_program:
        await message.answer('Выберите программу сплитов', reply_markup=reply.analiz_kb)
        await state.set_state(SplitStates.waiting_for_program)

    elif data['program'] == 'winorient':
        if current_state == SplitStates.winorient_analiz:
            data = await state.get_data()
            splits = data['splits']
            group = data['group']
            persons = [person for person in splits.get_persons_by_group(group)]
            await state.update_data(group=group)
            await message.answer('Выберите участника', reply_markup=reply.make_group_keyboard(persons))
            await state.set_state(SplitStates.winorient_name)

        elif current_state == SplitStates.winorient_group:
            await state.set_state(SplitStates.waiting_for_type_distance)
            await message.answer('Выберите тип дистанции', reply_markup=reply.types_kb)

        else:
            data = await state.get_data()
            splits = data['splits']
            await state.set_state(SplitStates.winorient_group)
            groups = [group_name for group_name in splits.groups.keys()]
            await message.answer('Введите одну из предложенных групп', reply_markup=reply.make_group_keyboard(groups))

    elif data['program'] == 'sportorg':
        pass

    elif data['program'] == 'sfr':
        pass