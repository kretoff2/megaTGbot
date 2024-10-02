from telebot import types
class handbook_markup(types.InlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self.add(types.InlineKeyboardButton("Назад", callback_data="about_bot"))