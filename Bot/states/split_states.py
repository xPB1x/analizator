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

    get_count_persons = State()
    get_names_for_comparing = State()
