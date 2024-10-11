from telebot import types, TeleBot
import requests
bot:TeleBot
'''
    ФИЗИКА НЕ ДОДЕЛАНА
    
    Химия не сделана
    Английский не сделан
'''
def gdz_s_10(call):
    subject = call.data.split(":")[2]
    message = call.message
    if subject == "Русский язык":
        bot.send_message(message.chat.id, "Введите номер упражнения")
        bot.register_next_step_handler(message, gdz_rus)
    elif subject == "Белорусский язык":
        bot.send_message(message.chat.id, "Введите номер упражнения")
        bot.register_next_step_handler(message, gdz_bel)
    elif subject == "Геометрия":
        bot.send_message(message.chat.id, "Введите номер задания")
        bot.register_next_step_handler(message, gdz_geom)
    elif subject == "Алгебра":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Повторение", callback_data="gdz_0:10:alg:povt")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 1", callback_data="gdz_0:10:alg:glava1")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 2", callback_data="gdz_0:10:alg:glava2")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 3", callback_data="gdz_0:10:alg:glava3")
        markup.add(btn)
        bot.send_message(message.chat.id, "Выбери главу", reply_markup=markup)
    elif subject == "Английский":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Стандартный", callback_data="gdz_0:9-angl")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Повышенный", callback_data="gdz_0:9-angl-profi")
        markup.add(btn)
        bot.send_message(message.chat.id, "Выбери уровень", reply_markup=markup)
    elif subject == "Физика":
        bot.send_message(message.chat.id, "Введите номер параграфа")
        bot.register_next_step_handler(message, gdz_fiz__0)
    elif subject == "Химия":
        bot.send_message(message.chat.id, "Введите номер параграфа")
        bot.register_next_step_handler(message, gdz_xim_9_0)
    else: bot.send_message(message.chat.id, "Извините но этот предмет не доступен для вашего класса")

def route_gdz_0(callback):
    if callback.data.startswith('gdz_0:9-angl'): gdz_angl_9_0(callback)
    elif callback.data.startswith('gdz_0:9:alg:'): gdz_alg__0(callback)

def gdz_fiz__0(message):
    try:
        upr = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не число, введите число")
        bot.register_next_step_handler(message, gdz_fiz__0)
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("От теории к практике"))
    bot.send_message(message.chat.id, "Выберите что вам надо")
    bot.register_next_step_handler(message, gdz_fiz_upr, upr)
def gdz_fiz_upr(message, upr):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_fiz_upr, upr)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/9-fiz-2019-2/{upr}/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return

def gdz_xim_9_0(message):
    try:
        upr = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не число, введите число")
        bot.register_next_step_handler(message, gdz_xim_9_0)
        return
    bot.send_message(message.chat.id, "Введите номер задания")
    bot.register_next_step_handler(message, gdz_xim_9, upr)
def gdz_xim_9(message, upr):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_xim_9, upr)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/9-him-2019/{upr-1}/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_rus(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_rus)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/10-rus-2020/1/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_bel(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_bel)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/10-bel-2020/1/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_bio_9(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_bio_9)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/9-biol-borisov/paragraf/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_angl_9_0(call):
    val = call.data.split(":")
    if val[1] == "9-angl":
        bot.send_message(call.message.chat.id, "Введите номер страницы")
        bot.register_next_step_handler(call.message, gdz_angl_9, val[1])
    elif val[1] == "9-angl-profi":
        if len(val) == 2:
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("Часть 1", callback_data="gdz_0:8-angl-profi:str")
            markup.add(btn)
            btn = types.InlineKeyboardButton("Часть 2", callback_data="gdz_0:8-angl-profi:chast-2")
            markup.add(btn)
            bot.send_message(call.message.chat.id, "Выбери часть", reply_markup=markup)
        elif len(val) == 3:
            bot.send_message(call.message.chat.id, "Введите номер страницы")
            bot.register_next_step_handler(call.message, gdz_angl_9, val[1], val[2])
def gdz_angl_9(message, book, part = None):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_angl_9, book, part)
        return
    try:
        URL = f'https://resheba.top/GDZ/{book}'
        if part is not None: URL+=f"/{part}"
        else: URL+="/0"
        URL+=f"/{nomer}.png"
        response = requests.get(URL)
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_alg__0(call):
    val0 = call.data.split(":")[3]
    bot.send_message(call.message.chat.id, "Введите номер")
    bot.register_next_step_handler(call.message, gdz_alg, val0)
def gdz_alg(message, val0):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_alg, val0)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/10-algebra-2020/{val0}/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_geom(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_geom)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/10-geom-2020/nomera/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return