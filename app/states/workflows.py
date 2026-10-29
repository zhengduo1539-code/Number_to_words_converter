from aiogram.fsm.state import State, StatesGroup


class WelcomeMessageStates(StatesGroup):
    waiting_text = State()


class RichWelcomeStates(StatesGroup):
    waiting_field = State()


class LanguageMessageStates(StatesGroup):
    waiting_menu = State()
    waiting_changed = State()
    waiting_request_prompt = State()
    waiting_request_sent = State()


class LanguageButtonStates(StatesGroup):
    waiting_icon = State()


class LoadingMessageStates(StatesGroup):
    waiting_text = State()


class RequestLanguageStates(StatesGroup):
    waiting_text = State()


class WelcomeButtonStates(StatesGroup):
    waiting_label = State()
    waiting_action = State()
    waiting_target = State()
    waiting_icon = State()
    waiting_style = State()


class AdminButtonStates(StatesGroup):
    waiting_label = State()
    waiting_icon = State()
    waiting_style = State()


class BroadcastStates(StatesGroup):
    waiting_target = State()
    waiting_message = State()
    waiting_confirmation = State()
