from aiogram.fsm.state import State, StatesGroup

class SplitStates(StatesGroup):
    waiting_for_url = State()
    waiting_for_program = State()

    waiting_for_type_distance = State()

    winorient_splits = State()
    winorient_analiz = State()
    winorient_group = State()
    winorient_name = State()

    sportorg_splits = State()
    sportorg_analiz = State()
    group_name = State()
    person_name = State()

    sfr_splits = State()
    sfr_analiz = State()
    sfr_group = State()
    sfr_name = State()

    texts = {
        'SplitStates:waiting_for_url': 'Отправьте ссылку на сплиты',
        'SplitStates:waiting_for_program': 'Выберите программу',
        'SplitStates:waiting_for_type_distance': 'Выберите тип дистанции',
        'SplitStates:winorient_splits': 'Выберите группу',
        'SplitStates:winorient_analiz': 'Выберите тип дистанции',
        'SplitStates:winorient_group': 'Выберите группу',
        'SplitStates:winorient_name': 'Выберите участника',
        'SplitStates:sportorg_splits': 'Выберите группу',
        'SplitStates:sportorg_analiz': '<UNK> <UNK> <UNK> <UNK> <UNK>',
        'SplitStates:group_name': 'Выберите участника',
        'SplitStates:person_name': 'Для выбора другого участника нажмите назад ещё раз',
        'SplitStates:sfr_splits': '<UNK> <UNK> <UNK> <UNK> <UNK>',
        'SplitStates:sfr_analiz': '<UNK> <UNK> <UNK> <UNK> <UNK>',
    }

