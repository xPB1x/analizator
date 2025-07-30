from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f, StateFilter
from aiogram.fsm.context import FSMContext

import requests
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from splits.splits_sportorg import SplitSportorg
from splits.splits_winorient import SplitsWinOrient

from Bot.kbds import reply
from Bot.states.split_states import SplitStates

user_private_router = Router()


@user_private_router.message(or_f(CommandStart(), F.text.lower() == 'старт'))
async def start_cmd(message: types.Message, state: FSMContext):
    await message.answer('Приветствую👋\nНачнём анализ?)', reply_markup=reply.start_kb)
    await state.clear()


@user_private_router.message(or_f(Command('help'), (F.text.lower() == 'помощь')))
async def help(message: types.Message):
    await message.answer('На данный момент помощь нужна мне')


@user_private_router.message(F.text.lower().contains('анализ'))
async def analiz(message: types.Message, state: FSMContext):
    await message.answer('Пришлите ссылку на сплиты🏃‍♂️📊🔗', reply_markup=reply.del_kb)
    await state.set_state(SplitStates.waiting_for_url)

@user_private_router.message(SplitStates.waiting_for_url)
async def choose_program(message: types.Message, state: FSMContext):
    url = message.text.strip()
    await state.update_data(url=url)
    await message.answer('👇Выберите программу сплитов📊📂🏃‍♀️', reply_markup=reply.analiz_kb)
    await state.set_state(SplitStates.waiting_for_program)


@user_private_router.message(SplitStates.waiting_for_program, F.text.lower().contains('winorient'))
async def winorient(message: types.Message, state: FSMContext):
    await message.answer('Ожидайте загрузки сплитов WinOrient🔄📦', reply_markup=reply.del_kb)

    data = await state.get_data()
    url = data['url']
    try:
        response = requests.get(url)
        await state.set_state(SplitStates.waiting_for_type_distance)
        await state.update_data(program='winorient')
        await state.update_data(response=response)

        await message.answer('✅Сплиты загружены✅')
        await message.answer('👇Выберите тип дистанции', reply_markup=reply.types_kb)
    except Exception:
        await message.answer('❌Неверный url адресс❌')


@user_private_router.message(SplitStates.waiting_for_program, F.text.lower().contains('sportorg'))
async def sportorg(message: types.Message, state: FSMContext):
    await message.answer('Ожидайте загрузки сплитов SportOrg🔄📦\n(Время загрузки может занимать до 1 минуты)', reply_markup=reply.del_kb)
    await state.set_state(SplitStates.waiting_for_type_distance)
    await state.update_data(program='sportorg')

    data = await state.get_data()
    url = data['url']
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    try:
        with webdriver.Chrome(options=options) as browser:
            browser.get(url)

            await asyncio.sleep(1)

            browser.find_element(By.CSS_SELECTOR, 'div.sportorg-settings-row > button').click()
            labels = browser.find_elements(By.CSS_SELECTOR, 'div.sportorg-settings-row')
            for label in labels:
                if label.text.strip() == 'Сплиты (все отметки)':
                    label.click()
                    break

            html = browser.page_source
            splits = SplitSportorg(html)
            await state.update_data(splits=splits)

            await message.answer('✅Сплиты загружены✅', reply_markup=reply.types_kb)
            await message.answer('👇Выберите тип дистанции', reply_markup=reply.types_kb)

    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer('❌Неверный URL или ошибка при загрузке❌')



@user_private_router.message(SplitStates.waiting_for_program, F.text.lower().contains('sfr'))
async def sfr(message: types.Message, state: FSMContext):
    await message.answer('Ожидайте загрузки сплитов SFR', reply_markup=reply.del_kb)

    data = await state.get_data()
    url = data['url']
    try:
        response = requests.get(url)
        await state.set_state(SplitStates.waiting_for_type_distance)
        await state.update_data(program='sfr')
        await state.update_data(response=response)

        await message.answer('✅Сплиты загружены✅')
        await message.answer('👇Выберите тип дистанции', reply_markup=reply.types_kb)
    except Exception:
        await message.answer('❌Неверный url адресс❌')


@user_private_router.message(SplitStates.waiting_for_program)
async def unknown_program(message: types.Message):
    await message.answer('😤Такая программа сплитов недоступна для анализа😤\n👇Выберите одну из предложенных👇')


@user_private_router.message(SplitStates.waiting_for_type_distance)
async def type_distance(message: types.Message, state: FSMContext):
    type_distance = message.text
    if type_distance not in {'Заданное направление', 'Общий старт', 'Эстафета', 'Выбор'}:
        await state.set_state(SplitStates.waiting_for_program)
        await message.answer('Недоступный для анализа тип дистанции😑\nВыберите программу для анализа из предложенных❗❗❗', reply_markup=reply.analiz_kb)
    else:
        await state.update_data(type_distance=type_distance)
        data = await state.get_data()
        program = data['program']
        if program == 'winorient':
            await state.set_state(SplitStates.winorient_splits)
            await message.answer('Отправьте любое сообщение, чтобы продолжить👀', reply_markup=reply.del_kb)
        elif program == 'sportorg':
            await state.set_state(SplitStates.sportorg_splits)
            await message.answer('Отправьте любое сообщение, чтобы продолжить👀', reply_markup=reply.del_kb)
        elif program == 'sfr':
            await state.set_state(SplitStates.sfr_splits)
            await message.answer('Отправьте любое сообщение, чтобы продолжить👀', reply_markup=reply.del_kb)