from telebot import types

my_markup = types.ReplyKeyboardMarkup()
btn1 = types.KeyboardButton("Личный кабинет 🪪")
btn2 = types.KeyboardButton("Настройки ⚙️")
my_markup.row(btn1, btn2)
btn = types.KeyboardButton("Обучение 📖")
my_markup.add(btn)
btn = types.KeyboardButton("Школа 🏫")
my_markup.add(btn)
btn = types.KeyboardButton("Школа kretoffer'a 💻")
btn = types.KeyboardButton("Магазин 🛍️")
my_markup.add(btn)

settings_markup = types.InlineKeyboardMarkup()
btn = types.InlineKeyboardButton("Баги и предложения", callback_data="report_btn")
settings_markup.add(btn)
btn = types.InlineKeyboardButton("Тех. поддержка", url="https://t.me/kretoffik")
settings_markup.add(btn)
btn = types.InlineKeyboardButton("О боте", callback_data="about_bot")
settings_markup.add(btn)

cancel_markup = types.ReplyKeyboardMarkup(row_width=1)
btn = types.KeyboardButton("Отмена")
cancel_markup.add(btn)

class report_repli_markup(types.InlineKeyboardMarkup):
    def __init__(self, userID):
        super().__init__()
        self.add(types.InlineKeyboardButton("Ответить", callback_data=f"reply_report:{userID}"))
        self.add(types.InlineKeyboardButton("Снять кулдаун", callback_data=f"good_report:{userID}"))
        self.add(types.InlineKeyboardButton("Спам", callback_data=f"bad_report:{userID}"))