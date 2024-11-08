from telebot import types

classes = [5, 6, 7, 8, 9, 10, 11]

my_markup_m = types.ReplyKeyboardMarkup()
btn1 = types.KeyboardButton("Личный кабинет 🪪")
btn2 = types.KeyboardButton("Настройки ⚙️")
my_markup_m.row(btn1, btn2)
btn = types.KeyboardButton("Обучение 📖")
my_markup_m.add(btn)
btn = types.KeyboardButton("Школа 🏫")
my_markup_m.add(btn)
btn = types.KeyboardButton("Школа kretoffer'a 💻")
btn = types.KeyboardButton("Другое")
my_markup_m.add(btn)

other_markup = types.ReplyKeyboardMarkup()
btn = types.KeyboardButton("kretofferGPT 🤖")
other_markup.add(btn)
btn = types.KeyboardButton("Магазин 🛍️")
other_markup.add(btn)
btn = types.KeyboardButton("⬅️ Назад")
other_markup.add(btn)

kretofferGPT_variants_markup = types.InlineKeyboardMarkup()
kretofferGPT_variants_markup.add(types.InlineKeyboardButton("micro", callback_data="GPT_v:micro"))
kretofferGPT_variants_markup.add(types.InlineKeyboardButton("mini", callback_data="GPT_v:mini"))
kretofferGPT_variants_markup.add(types.InlineKeyboardButton("lite", callback_data="GPT_v:lite"))
kretofferGPT_variants_markup.add(types.InlineKeyboardButton("standart", callback_data="GPT_v:standart"))
kretofferGPT_variants_markup.add(types.InlineKeyboardButton("bigModel", callback_data="GPT_v:bigModel"))
kretofferGPT_variants_markup.add(types.InlineKeyboardButton("kretofferGPT pro", callback_data="GPT_v:kretofferGPT_pro"))
kretofferGPT_variants_markup.add(types.InlineKeyboardButton("kretofferGPT pro+", callback_data="GPT_v:kretofferGPT_pro_p"))

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

rep_markup = types.InlineKeyboardMarkup()
rep_markup.add(types.InlineKeyboardButton("Одноклассники", callback_data="rep_classmates"))
#rep_markup.add(types.InlineKeyboardButton("Другие", callback_data="rep_other"))

yes_or_no_markup = types.ReplyKeyboardMarkup(row_width=1)
btn0 = types.KeyboardButton("Да")
btn1 = types.KeyboardButton("Нет")
yes_or_no_markup.row(btn0, btn1)

class report_repli_markup(types.InlineKeyboardMarkup):
    def __init__(self, userID):
        super().__init__()
        self.add(types.InlineKeyboardButton("Ответить", callback_data=f"reply_report:{userID}"))
        self.add(types.InlineKeyboardButton("Снять кулдаун", callback_data=f"good_report:{userID}"))
        self.add(types.InlineKeyboardButton("Спам", callback_data=f"bad_report:{userID}"))

add_admin_markup = types.InlineKeyboardMarkup()
add_admin_markup.add(types.InlineKeyboardButton("Урок", callback_data="adm_add:l"))
add_admin_markup.add(types.InlineKeyboardButton("Тест", callback_data="adm_add:t"))
add_admin_markup.add(types.InlineKeyboardButton("Шпаргалка", callback_data="adm_add:cs"))
add_admin_markup.add(types.InlineKeyboardButton("Экзамен", callback_data="adm_add:e"))

class classes_markup(types.InlineKeyboardMarkup):
    def __init__(self, data, classes = classes):
        super().__init__()
        for el in classes:
            self.add(types.InlineKeyboardButton(str(el), callback_data=f"{data}:{el}"))
class dictToMarkupI(types.InlineKeyboardMarkup):
    def __init__(self, data,  dict: dict = {"1": "hello"}):
        super().__init__()
        for el in dict:
            self.add(types.InlineKeyboardButton(dict[el], callback_data=f"{data}:{el}"))
class listToMarkupI(types.InlineKeyboardMarkup):
    def __init__(self, data,  list: list = []):
        super().__init__()
        for el in list:
            self.add(types.InlineKeyboardButton(el, callback_data=f"{data}:{el}"))