from telebot import types, TeleBot
import requests
bot:TeleBot
def gdz_s_6(call):
    subject = call.data.split(":")[2]
    message = call.message
    if subject == "Русский язык":
        bot.send_message(message.chat.id, "Введите номер упражнения")
        bot.register_next_step_handler(message, gdz_rus_6)
    elif subject == "Белорусский язык":
        bot.send_message(message.chat.id, "Введите номер упражнения")
        bot.register_next_step_handler(message, gdz_bel_6)
    elif subject == "Биология":
        bot.send_message(message.chat.id, "Введите номер параграфа")
        bot.register_next_step_handler(message, gdz_bio_6)
    elif subject == "География":
        bot.send_message(message.chat.id, "Введите номер параграфа")
        bot.register_next_step_handler(message, gdz_geo_6)
    elif subject == "История":
        bot.send_message(message.chat.id, "Введите номер параграфа")
        bot.register_next_step_handler(message, gdz_hist_6)
    elif subject == "_commented":#"Математика":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Глава 1", callback_data="gdz_0:6:alg:0")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 2", callback_data="gdz_0:6:alg:1")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 3", callback_data="gdz_0:6:alg:3")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 4", callback_data="gdz_0:6:alg:4")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 5", callback_data="gdz_0:6:alg:5")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 6", callback_data="gdz_0:6:alg:6")
        markup.add(btn)
        bot.send_message(message.chat.id, "Выбери главу", reply_markup=markup)
    elif subject == "Английский":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Стандартный", callback_data="gdz_0:6-angl")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Повышенный", callback_data="gdz_0:6-angl-profi")
        markup.add(btn)
        bot.send_message(message.chat.id, "Выбери уровень", reply_markup=markup)
    else: bot.send_message(message.chat.id, "Извините но этот предмет не доступен для вашего класса")
def route_gdz_0(callback):
    if callback.data.startswith('gdz_0:6-angl'): gdz_angl_6_0(callback)
    elif callback.data.startswith('gdz_0:6:alg:'): gdz_alg_6_0(callback)
def gdz_bio_6(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_bio_6)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/6-biol/str/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_geo_6(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_geo_6)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/6-geograf/par/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_hist_6(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_hist_6)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/6-istorija-sred/par/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_rus_6(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_rus_6)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/6-rus-2020/1/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_bel_6(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_bel_6)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/6-bel-2020/1/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_angl_6_0(call):
    val = call.data.split(":")
    if val[1] == "6-angl":
        bot.send_message(call.message.chat.id, "Введите номер страницы")
        bot.register_next_step_handler(call.message, gdz_angl_6, val[1])
    elif val[1] == "6-angl-profi":
        if len(val) == 2:
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("Часть 1", callback_data="gdz_0:6-angl-profi:chast-1")
            markup.add(btn)
            btn = types.InlineKeyboardButton("Часть 2", callback_data="gdz_0:6-angl-profi:chast-2")
            markup.add(btn)
            bot.send_message(call.message.chat.id, "Выбери часть", reply_markup=markup)
        elif len(val) == 3:
            bot.send_message(call.message.chat.id, "Введите номер страницы")
            bot.register_next_step_handler(call.message, gdz_angl_6, val[1], val[2])
def gdz_angl_6(message, book, part = None):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_angl_6, book, part)
        return
    try:
        URL = f'https://resheba.top/GDZ/{book}'
        if part is not None: URL+=f"/{part}"
        else: URL+="/2021"
        URL+=f"/{nomer}.png"
        response = requests.get(URL)
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_alg_6_0(call):
    val0 = call.data.split(":")[3]
    bot.send_message(call.message.chat.id, "Введите номер")
    bot.register_next_step_handler(call.message, gdz_alg_6, val0)
def gdz_alg_6(message, val0):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_alg_6, val0)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/7-alg-2017/{val0}/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return