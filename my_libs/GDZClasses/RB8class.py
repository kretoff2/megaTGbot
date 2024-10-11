from telebot import types, TeleBot
import requests
bot:TeleBot

def gdz_s_8(call):
    subject = call.data.split(":")[2]
    message = call.message
    if subject == "Русский язык":
        bot.send_message(message.chat.id, "Введите номер упражнения")
        bot.register_next_step_handler(message, gdz_rus_8)
    elif subject == "Белорусский язык":
        bot.send_message(message.chat.id, "Введите номер упражнения")
        bot.register_next_step_handler(message, gdz_bel_8)
    elif subject == "Биология":
        bot.send_message(message.chat.id, "Введите номер параграфа")
        bot.register_next_step_handler(message, gdz_bio_8)
    elif subject == "География":
        bot.send_message(message.chat.id, "Введите номер параграфа")
        bot.register_next_step_handler(message, gdz_geo_8)
    elif subject == "Геометрия":
        bot.send_message(message.chat.id, "Введите номер задания")
        bot.register_next_step_handler(message, gdz_geom_8)
    elif subject == "Алгебра":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Повторение 7 класса", callback_data="gdz_alg_8:10")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 1", callback_data="gdz_0:8:alg:0")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 2", callback_data="gdz_0:8:alg:2")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 3", callback_data="gdz_0:8:alg:7")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 4", callback_data="gdz_0:8:alg:9")
        markup.add(btn)
        bot.send_message(message.chat.id, "Выбери главу", reply_markup=markup)
    elif subject == "Английский":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Стандартный", callback_data="gdz_0:8-angl-2021")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Повышенный", callback_data="gdz_0:8-angl-profi")
        markup.add(btn)
        bot.send_message(message.chat.id, "Выбери уровень", reply_markup=markup)
    elif subject == "Физика":
        bot.send_message(message.chat.id, "Введите номер упражнения (от 1 до 26)")
        bot.register_next_step_handler(message, gdz_fiz_8_0)
    elif subject == "Химия":
        bot.send_message(message.chat.id, "Введите номер параграфа")
        bot.register_next_step_handler(message, gdz_xim_8_0)
    else: bot.send_message(message.chat.id, "Извините но этот предмет не доступен для вашего класса")

def route_gdz_0(callback):
    if callback.data.startswith('gdz_0:8-angl-'): gdz_angl_8_0(callback)
    elif callback.data.startswith('gdz_0:8:alg:'): gdz_alg_8_0(callback)

def gdz_fiz_8_0(message):
    try:
        upr = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не число, введите число")
        bot.register_next_step_handler(message, gdz_fiz_8_0)
        return
    bot.send_message(message.chat.id, "Введите номер задания")
    bot.register_next_step_handler(message, gdz_fiz_8, upr)
def gdz_fiz_8(message, upr):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_fiz_8, upr)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/8-fizika-2018/{upr-1}/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return

def gdz_xim_8_0(message):
    try:
        upr = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не число, введите число")
        bot.register_next_step_handler(message, gdz_xim_8_0)
        return
    bot.send_message(message.chat.id, "Введите номер задания")
    bot.register_next_step_handler(message, gdz_xim_8, upr)
def gdz_xim_8(message, upr):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_xim_8, upr)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/8-him-2018/{upr-1}/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_rus_8(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_rus_8)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/8-russk-2018/0/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_bel_8(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_bel_8)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/8-bel-2020/1/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_bio_8(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_bio_8)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/8-biol-2023/par/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_geo_8(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_geo_8)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/8-geograf/1/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_angl_8_0(call):
    val = call.data.split(":")
    if val[1] == "8-angl-2021":
        bot.send_message(call.message.chat.id, "Введите номер страницы")
        bot.register_next_step_handler(call.message, gdz_angl_8, val[1])
    elif val[1] == "8-angl-profi":
        if len(val) == 2:
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("Часть 1", callback_data="gdz_0:8-angl-profi:chast-1")
            markup.add(btn)
            btn = types.InlineKeyboardButton("Часть 2", callback_data="gdz_0:8-angl-profi:chast-2")
            markup.add(btn)
            bot.send_message(call.message.chat.id, "Выбери часть", reply_markup=markup)
        elif len(val) == 3:
            bot.send_message(call.message.chat.id, "Введите номер страницы")
            bot.register_next_step_handler(call.message, gdz_angl_8, val[1], val[2])
def gdz_angl_8(message, book, part = None):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_angl_8, book, part)
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
def gdz_alg_8_0(call):
    val0 = call.data.split(":")[3]
    bot.send_message(call.message.chat.id, "Введите номер")
    bot.register_next_step_handler(call.message, gdz_alg_8, val0)
def gdz_alg_8(message, val0):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_alg_8, val0)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/8-alg-2018/{val0}/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_geom_8(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_geom_8)
        return
    if nomer <= 153:
        val0 = 1
    elif nomer <= 260:
        val0 = 3
    elif nomer <= 350:
        val0 = 4
    elif nomer <= 422:
        val0 = 6
    try:
        response = requests.get(f'https://resheba.top/GDZ/8-geom-2018/{val0}/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return