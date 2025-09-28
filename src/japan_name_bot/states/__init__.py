from aiogram.fsm.state import State, StatesGroup


class NameStates(StatesGroup):
    waiting_name = State()


__all__ = ["NameStates"]
