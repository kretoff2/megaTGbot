from telebot import types, TeleBot
import requests
bot:TeleBot
def gdz_s_7(call):
    subject = call.data.split(":")[2]
    message = call.message
    if subject == "Русский язык":
        bot.send_message(message.chat.id, "Введите номер упражнения")
        bot.register_next_step_handler(message, gdz_rus_7)
    elif subject == "Белорусский язык":
        bot.send_message(message.chat.id, "Введите номер упражнения")
        bot.register_next_step_handler(message, gdz_bel_7)
    elif subject == "Геометрия":
        bot.send_message(message.chat.id, "Введите номер задания")
        bot.register_next_step_handler(message, gdz_geom_7)
    elif subject == "Алгебра":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Глава 1", callback_data="gdz_0:7:alg:0")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 2", callback_data="gdz_0:7:alg:1")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 3", callback_data="gdz_0:7:alg:3")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 4", callback_data="gdz_0:7:alg:4")
        markup.add(btn)
        bot.send_message(message.chat.id, "Выбери главу", reply_markup=markup)
    elif subject == "Английский":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Стандартный", callback_data="gdz_0:7-angl")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Повышенный", callback_data="gdz_0:7-angl-profi")
        markup.add(btn)
        bot.send_message(message.chat.id, "Выбери уровень", reply_markup=markup)
    elif subject == "Физика":
        bot.send_message(message.chat.id, "Введите номер упражнения (от 1 до 22)")
        bot.register_next_step_handler(message, gdz_fiz_7_0)
    elif subject == "Химия":
        bot.send_message(message.chat.id, "Введите номер параграфа")
        bot.register_next_step_handler(message, gdz_xim_7_0)
    else: bot.send_message(message.chat.id, "Извините но этот предмет не доступен для вашего класса")
def route_gdz_0(callback):
    if callback.data.startswith('gdz_0:7-angl'): gdz_angl_7_0(callback)
    elif callback.data.startswith('gdz_0:7:alg:'): gdz_alg_7_0(callback)
def gdz_fiz_7_0(message):
    try:
        upr = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не число, введите число")
        bot.register_next_step_handler(message, gdz_fiz_7_0)
        return
    bot.send_message(message.chat.id, "Введите номер задания")
    bot.register_next_step_handler(message, gdz_fiz_7, upr)
def gdz_fiz_7(message, upr):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_fiz_7, upr)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/7-fizika-new/{upr-1}/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return

def gdz_xim_7_0(message):
    try:
        upr = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не число, введите число")
        bot.register_next_step_handler(message, gdz_xim_7_0)
        return
    bot.send_message(message.chat.id, "Введите номер задания")
    bot.register_next_step_handler(message, gdz_xim_7, upr)
def gdz_xim_7(message, upr):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_xim_7, upr)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/7-himiya-2017/par-{upr}/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_rus_7(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_rus_7)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/7-rus-2020/1/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_bel_7(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_bel_7)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/7-bel-2020/1/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_angl_7_0(call):
    val = call.data.split(":")
    if val[1] == "7-angl":
        bot.send_message(call.message.chat.id, "Введите номер страницы")
        bot.register_next_step_handler(call.message, gdz_angl_7, val[1])
    elif val[1] == "7-angl-profi":
        if len(val) == 2:
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("Часть 1", callback_data="gdz_0:7-angl-profi:chast-1")
            markup.add(btn)
            btn = types.InlineKeyboardButton("Часть 2", callback_data="gdz_0:7-angl-profi:chast-2")
            markup.add(btn)
            bot.send_message(call.message.chat.id, "Выбери часть", reply_markup=markup)
        elif len(val) == 3:
            bot.send_message(call.message.chat.id, "Введите номер страницы")
            bot.register_next_step_handler(call.message, gdz_angl_7, val[1], val[2])
def gdz_angl_7(message, book, part = None):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_angl_7, book, part)
        return
    try:
        URL = f'https://resheba.top/GDZ/{book}'
        if part is not None: URL+=f"/{part}"
        else: URL+="/str"
        URL+=f"/{nomer}.png"
        response = requests.get(URL)
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_alg_7_0(call):
    val0 = call.data.split(":")[3]
    bot.send_message(call.message.chat.id, "Введите номер")
    bot.register_next_step_handler(call.message, gdz_alg_7, val0)
def gdz_alg_7(message, val0):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_alg_7, val0)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/7-alg-2017/{val0}/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_geom_7(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_geom_7)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/7-geom-2017-4/nomera/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return