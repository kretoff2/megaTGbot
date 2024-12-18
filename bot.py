import gigachat
import telebot
from telebot import types
import sqlite3 as sql
import datetime
from datetime import *
import random
import os
import json
import config
from pathlib import Path
import requests

from my_libs.markups import *
import my_libs.handbook
import my_libs.ExLevel
import my_libs.sql_commands
from my_libs.sql_commands import SQL_connection, SQL_one_command
from my_libs import GDZ
from gigachat import ask_question
from my_libs.markups.adm_markups import *

#from PIL import Image
#import io

bot = telebot.TeleBot(config.bot)
GDZ.init(bot)

tempData = {
    "usersData": {

    }
}

def sql_conn():
    return my_libs.sql_commands.sql_conn()

conn = sql_conn()
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, first_name varchar(50), last_name varchar(50), chatID int, bagsTimeOut float, schoolID int, autorizationStep int, teacher bit, experience int, level int, coins int, diamonds int, tickets int, class varchar(6), rating int)')
cur.execute('CREATE TABLE IF NOT EXISTS schools(id int auto_increment primary key, schoolID int, contry varchar(20), obl varchar(50), sity varchar(50), school varchar(50), rating int)')
cur.execute('CREATE TABLE IF NOT EXISTS bags (id int auto_increment primary key, date varchar(50), user varchar(100), bag varchar(5000), bagId int)')
cur.execute('CREATE TABLE IF NOT EXISTS admins (id int auto_increment primary key, name varchar(50), chatID int)')
cur.execute('CREATE TABLE IF NOT EXISTS news (id int auto_increment primary key, date varchar(50), news varchar(5000), NewsId int)')
cur.execute('CREATE TABLE IF NOT EXISTS timeOuts (chatID int primary key, report int, selectClass int, selectSchool int, rep int)')
#cur.execute('INSERT INTO schools (contry) VALUES ("%s")' % ("Беларусь"))
#cur.execute('INSERT INTO schools (contry) VALUES ("%s")' % ("Россия"))
#cur.execute("UPDATE users SET coins = 100000 WHERE chatID = ?", (config.ADMIN_ID,))

conn.commit()

cur.execute('SELECT chatID FROM users')
usersIds = cur.fetchall()
for el in usersIds:
    tempData['usersData'][str(el[0])]={}

cur.close()
conn.close()
data = {
    "usersData":{

    },
    "education":{

    },
    "schoolsData":{

    },
    "examsData":{

    },
    "reviews":{

    }
}

lessonsData = {}
if not os.path.exists('./data.json'):
    with open('data.json', 'w') as f:
        json.dump(data, f)
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
with open('lessons.json', 'r', encoding='utf-8') as f:
    lessonsData = json.load(f)
def getLessonsData():
    with open('lessons.json', 'r', encoding='utf-8') as f:
        lessonsData = json.load(f)
    return lessonsData
def save_lessonsData(lessonsData = lessonsData):
    with open('lessons.json', 'w') as f:
        json.dump(lessonsData, f)

def my_markup():
    markup = my_markup_m
    return markup

def format_message_text(message:telebot.types.Message):
    text = message.text
    entities = message.entities

    if entities is None:
        return text

    entities = sorted(entities, key=lambda e: e.offset)
    html_text = ""
    last_offset = 0

    tag_map = {
        'bold': 'b',
        'italic': 'i',
        'underline': 'u',
        'strikethrough': 's',
        'code': 'code',
        'pre': 'pre',
        'text_link': 'a',
        'blockquote': 'blockquote',
        'spoiler': 'tg-spoiler'
    }

    open_tags = []

    ent = 0
    for entity in entities:
        start = entity.offset
        end = start + entity.length

        # Добавляем текст до текущей entity
        html_text += text[last_offset:start]

        # Закрываем все открытые теги, если нужно
        while open_tags and open_tags[-1][0] <= start:
            tag = open_tags.pop()[1]
            if tag != "\n":
                html_text += f'</{tag}>'
            else:
                html_text += "\n"

        # Открываем новый тег
        if entity.type in tag_map:
            tag = tag_map[entity.type]
            if entity.type == 'text_link':
                html_text += f'<{tag} href="{entity.url}">'
            else:
                html_text += f'<{tag}>'
            open_tags.append((end, tag))

        # Добавляем текст текущей entity
        if ent+1 >= len(entities) or entities[ent+1].offset >= end:
            html_text += text[start:end]
        last_offset = end
        ent += 1

    # Добавляем оставшийся текст
    html_text += text[last_offset:]

    # Закрываем все оставшиеся теги
    while open_tags:
        tag = open_tags.pop()[1]
        html_text += f'</{tag}>'

    return html_text


#admin bot

@bot.message_handler(commands=['info', 'messageInfo'])
def main(message):
    if message.chat.id != config.ADMIN_ID:
        return
    bot.send_message(message.chat.id, str(message)[:int(len(str(message))/2)])
    bot.send_message(message.chat.id, str(message)[int(len(str(message))/2):])
@bot.message_handler(commands=['repiat', 'repiatIt'])
def main(message):
    bot.send_message(message.chat.id, message.text)
@bot.message_handler(commands=['getHTML'])
def main(message):
    text = format_message_text(message)
    text = text[8:len(text)]
    bot.send_message(message.chat.id, text)
    bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.message_handler(commands=['new', 'add'])
def main(message):
    name = SQL_one_command('SELECT name FROM admins WHERE chatID = ?', (message.chat.id,), fetchMode='one').data
    if name is None:
        bot.send_message(message.chat.id, "Недостаточно прав")
        return
    bot.send_message(message.chat.id, f"Что вы хотите добавить, {name[0]}?", reply_markup=add_admin_markup)


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('adm_add:'))
def main(call):
    type = call.data.split(":")[1]
    bot.send_message(call.message.chat.id, "Выбери класс", reply_markup=classes_markup(f"adm_add2:{type}"))
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('adm_add2:'))
def main(call):
    type, userClass = tuple(call.data.split(":")[1:3])
    markup = dictToMarkupI(f"adm_add3:{type}:{userClass}", lessonsData["subjects"])
    bot.send_message(call.message.chat.id, "Выберите предмет", reply_markup=markup)
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('adm_add3:l'))
def main(call):
    type, userClass, subject = call.data.split(":")[1:4]
    markup = types.ReplyKeyboardMarkup()
    for key, value in lessonsData["lessons"]["themes"][f"{userClass}classThemes"].items():
        if value["subject"] == subject:
            markup.add(types.KeyboardButton(key[:64]))
    bot.send_message(call.message.chat.id, "Выберите тему", reply_markup=markup)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.register_next_step_handler(call.message, adm_add4L, type, userClass, subject)

def adm_add4L(message, type, userClass, subject):
    if len(message.text) > 64:
        markup = types.ReplyKeyboardMarkup()
        markup.add(types.KeyboardButton(message.text[:61]+"..."))
        bot.send_message(message.chat.id, "Название темы должно включать не более 64 символов. Можешь назвать тему так:")
        bot.register_next_step_handler(message, adm_add4L, type, userClass, subject)
        return
    if message.text in lessonsData["lessons"]["themes"][f"{userClass}classThemes"] and lessonsData["lessons"]["themes"][f"{userClass}classThemes"][message.text]["subject"] != subject:
        bot.send_message(message.chat.id, "Тема с таким названием уже есть в другом предмете, выберите другую")
        bot.register_next_step_handler(message, adm_add4T, type, userClass, subject)
        return
    bot.send_message(message.chat.id, "Впишите название урока")
    bot.register_next_step_handler(message, adm_add5L, type, int(userClass), subject, message.text)
def adm_add5L(message, type, userClass, subject, theme):
    if len(message.text) > 64:
        markup = types.ReplyKeyboardMarkup()
        markup.add(types.KeyboardButton(message.text[:61]+"..."))
        bot.send_message(message.chat.id, "Название урока должно включать не более 64 символов. Можешь назвать тему так:")
        bot.register_next_step_handler(message, adm_add5L, type, userClass, subject, theme)
        return
    if message.text in lessonsData["lessons"]["themes"][f"{userClass}classThemes"]:
        bot.send_message(message.chat.id, "Урок с таким названием уже есть, выберите другое")
        bot.register_next_step_handler(message, adm_add5L, type, userClass, subject, theme)
        return
    index = len(lessonsData["lessons"])
    name = message.text
    if theme in lessonsData["lessons"]["themes"][f"{userClass}classThemes"]:
        lessonsData["lessons"]["themes"][f"{userClass}classThemes"][theme]["list"].append(str(index))
    else:
        themeID = len(lessonsData["lessons"]["themes"][f"{userClass}classThemes"]) + 1
        lessonsData["lessons"]["themes"][f"{userClass}classThemes"][theme] = {"subject": subject, "list": [str(index)], "id": themeID}

    lessonsData["lessons"][str(index)] = {
      "name": name,
      "subtitle": " ",
      "class": userClass,
      "subject": subject,
      "theme": theme,
      "text": {},
      "media":{},
      "test": None,
      "videoLesson": None
    }
    save_lessonsData()
    bot.send_message(message.chat.id, "Урок успешно создан, можете начать его редактировать с помощью /edit", reply_markup=my_markup())

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('adm_add3:t'))
def main(call):
    type, userClass, subject = call.data.split(":")[1:4]
    markup = types.ReplyKeyboardMarkup()
    for key, value in lessonsData["tests"]["themes"][f"{userClass}classThemes"].items():
        if value["subject"] == subject:
            markup.add(types.KeyboardButton(key[:64]))
    bot.send_message(call.message.chat.id, "Выберите тему", reply_markup=markup)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.register_next_step_handler(call.message, adm_add4T, type, userClass, subject)

def adm_add4T(message, type, userClass, subject):
    if len(message.text) > 64:
        markup = types.ReplyKeyboardMarkup()
        markup.add(types.KeyboardButton(message.text[:61]+"..."))
        bot.send_message(message.chat.id, "Название темы должно включать не более 64 символов. Можешь назвать тему так:")
        bot.register_next_step_handler(message, adm_add4T, type, userClass, subject)
        return
    if message.text in lessonsData["tests"]["themes"][f"{userClass}classThemes"] and lessonsData["tests"]["themes"][f"{userClass}classThemes"][message.text]["subject"] != subject:
        bot.send_message(message.chat.id, "Тема с таким названием уже есть в другом предмете, выберите другую")
        bot.register_next_step_handler(message, adm_add4T, type, userClass, subject)
        return
    bot.send_message(message.chat.id, "Впишите название теста")
    bot.register_next_step_handler(message, adm_add5T, type, int(userClass), subject, message.text)
def adm_add5T(message, type, userClass, subject, theme):
    if len(message.text) > 64:
        markup = types.ReplyKeyboardMarkup()
        markup.add(types.KeyboardButton(message.text[:61]+"..."))
        bot.send_message(message.chat.id, "Название теста должно включать не более 64 символов. Можешь назвать тему так:")
        bot.register_next_step_handler(message, adm_add5T, type, userClass, subject, theme)
        return
    if message.text in lessonsData["tests"]["themes"][f"{userClass}classThemes"]:
        bot.send_message(message.chat.id, "Тест с таким названием уже есть, выберите другое")
        bot.register_next_step_handler(message, adm_add5T, type, userClass, subject, theme)
        return
    index = len(lessonsData["tests"])
    name = message.text
    if theme in lessonsData["tests"]["themes"][f"{userClass}classThemes"]:
        lessonsData["tests"]["themes"][f"{userClass}classThemes"][theme]["list"].append(str(index))
    else:
        themeID = len(lessonsData["tests"]["themes"][f"{userClass}classThemes"]) + 1
        lessonsData["tests"]["themes"][f"{userClass}classThemes"][theme] = {"subject": subject, "list": [str(index)], "id": themeID}

    lessonsData["tests"][str(index)] = {
      "name": name,
      "subtitle": " ",
      "subject": subject,
      "class": userClass,
      "theme": theme,
      "questions": {}
    }
    save_lessonsData()
    bot.send_message(message.chat.id, "Тест успешно создан, можете начать его редактировать с помощью /edit", reply_markup=my_markup())

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('adm_add3:cs'))
def main(call):
    type, userClass, subject = call.data.split(":")[1:4]
    markup = types.ReplyKeyboardMarkup()
    for key, value in lessonsData["cheat_sheets"][f"{userClass}class"].items():
        if value["subject"] == subject:
            markup.add(types.KeyboardButton(key[:64]))
    bot.send_message(call.message.chat.id, "Выберите тему", reply_markup=markup)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.register_next_step_handler(call.message, adm_add4CS, type, userClass, subject)

def adm_add4CS(message, type, userClass, subject):
    if len(message.text) > 64:
        markup = types.ReplyKeyboardMarkup()
        markup.add(types.KeyboardButton(message.text[:61]+"..."))
        bot.send_message(message.chat.id, "Название темы должно включать не более 64 символов. Можешь назвать тему так:")
        bot.register_next_step_handler(message, adm_add4CS, type, userClass, subject)
        return
    bot.send_message(message.chat.id, "Впишите название шпаргалки")
    bot.register_next_step_handler(message, adm_add5CS, type, int(userClass), subject, message.text)
def adm_add5CS(message, type, userClass, subject, theme):
    if len(message.text) > 64:
        markup = types.ReplyKeyboardMarkup()
        markup.add(types.KeyboardButton(message.text[:61]+"..."))
        bot.send_message(message.chat.id, "Название шпаргалки должно включать не более 64 символов. Можешь назвать тему так:")
        bot.register_next_step_handler(message, adm_add5CS, type, userClass, subject, theme)
        return
    if theme not in lessonsData["cheat_sheets"][f"{userClass}class"]:
        lessonsData["cheat_sheets"][f"{userClass}class"][theme] = {"subject":subject, "id":len(lessonsData["cheat_sheets"][f"{userClass}class"])+1}
    for el in lessonsData["cheat_sheets"][f"{userClass}class"][theme]:
        if el not in ["subject", "id"] and lessonsData["cheat_sheets"][f"{userClass}class"][theme][el]["name"] == message.text:
            bot.send_message(message.chat.id, "Тест с таким названием уже есть, выберите другое")
            bot.register_next_step_handler(message, adm_add5CS, type, userClass, subject, theme)
            return
    index = len(lessonsData["cheat_sheets"][f"{userClass}class"][theme])-1
    name = message.text

    save_lessonsData()
    bot.send_message(message.chat.id, "Введите шпаргалку")
    bot.register_next_step_handler(message, adm_add6CS, userClass, theme, index, name)

def adm_add6CS(message, userClass, theme, index, name):
    lessonsData["cheat_sheets"][f"{userClass}class"][theme][str(index)] = {
        "name": name,
        "text": format_message_text(message),
        "lesson": None
    }
    save_lessonsData()
    bot.send_message(message.chat.id, "Шпаргалка добавлена успешно", reply_markup=my_markup())


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('adm_add3:e'))
def main(call):
    type, userClass, subject = call.data.split(":")[1:4]
    bot.send_message(call.message.chat.id, "Впишите название экзамена")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.register_next_step_handler(call.message, adm_add4E, type, userClass, subject)

def adm_add4E(message, type, userClass, subject):
    dictionary = lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["exams"]
    if any(item.get("name") == message.text for item in dictionary.values()):
        bot.send_message(message.chat.id, "Экзамен с таким названием уже есть, хотите его редактировать? /edit exam")
        return
    dictionary[len(dictionary)+1] = {
              "name": message.text,
              "subtitle": " ",
              "types": {}
            }


@bot.message_handler(commands=['edit'])
def main(message):
    bot.send_message(message.chat.id, "С чем вы хотите работать?", reply_markup=dictToMarkupI("adm_edit", {"l":"Уроки", "t":"Тесты", "cs":"Шпаргалки", "e":"Экзамены"}))

@bot.callback_query_handler(func=lambda callback: callback.data.startswith("adm_edit:"))
def main(call):
    type = call.data.split(":")[1]
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Выберите класс", reply_markup=classes_markup(f"adm_edit3:{type}"))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith("adm_edit2:"))
def main(call):
    type, userClass = call.data.split(":")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Выберите предмет", reply_markup=dictToMarkupI(f"adm_edit3:{type}:{userClass}", lessonsData["subjects"]))

@bot.callback_query_handler(func=lambda callback: callback.data.startswith("adm_edit3:l"))
def main(call):
    userClass, subject = call.data.split(":")[2:4]
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "С чем хотите работать?", reply_markup=dictToMarkupI(f"adm_edit4:l:{userClass}:{subject}", {"t": "Темы", "l":"Уроки"}))

@bot.callback_query_handler(func=lambda callback: callback.data.startswith("adm_edit4:l:") and callback.data[-1] == "t")
def main(call):
    userClass, subject = call.data.split(":")[2:4]
    bot.delete_message(call.message.chat.id, call.message.message_id)
    text = f"Темы по предмету {lessonsData['subjects'][subject]}:\n\n"
    data = lessonsData["lessons"]["themes"][f"{userClass}classThemes"]
    for el in data:
        text += f"{el}\nУроки: {data[el]['list']}\tid: {data[el]['id']}"
    bot.send_message(call.message.chat.id, text, reply_markup=adm_edit_l_t_markup)





#bot
@bot.message_handler(commands=['class'])
def main(message):
    info = "Твой класс:\n\n"
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute("SELECT schoolID, class FROM users WHERE chatID = ?", (message.chat.id,))
    schoolID, userClass = cur.fetchone()
    cur.execute("SELECT first_name, last_name, rating FROM users WHERE schoolID = ? AND class = ?", (schoolID, userClass))
    users = cur.fetchall()
    cur.close()
    conn.close()
    for el in users:
        info += el[0] + " "
        if el[1] != "None":
            info += el[1]
        info += "— " + str(el[2])+ " очков рейтинга\n\n"
    bot.send_message(message.chat.id, info)
@bot.message_handler(commands=['r', 'rep', 'rating'])
def main(message):
    bot.send_message(message.chat.id, "С помощью команд /r /rep /rating вы можете менять рейтинг другим людям (путем 👍 и 👎). Если вы хотите оставить отзыв о человека выберите его", reply_markup=rep_markup)

@bot.callback_query_handler(func=lambda callback: callback.data == "rep_classmates")
def rep_classmates(call):
    conn = SQL_connection()
    user = conn.SQL_fetchone("SELECT schoolID, class FROM users WHERE chatID = ?", (call.message.chat.id,))
    users = conn.SQL_fetchall("SELECT chatID, first_name, last_name FROM users WHERE schoolID = ? AND class = ? AND chatID <> ?", (user[0], user[1], call.message.chat.id))
    conn.sql_close()
    markup = types.InlineKeyboardMarkup()
    for el in users:
        name = el[1]
        if el[2] != "None":
            name += " " + el[2]
        markup.add(types.InlineKeyboardButton(name, callback_data=f"rep_cm:{el[0]}"))
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('rep_cm:'))
def rep_cm(call):
    chatID = int(call.data.split(":")[1])
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.row(types.KeyboardButton("👍"), types.KeyboardButton("👎"))
    markup.add(types.KeyboardButton("Отмена"))
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    userName = SQL_one_command("SELECT first_name FROM users WHERE chatID = ?", (chatID,), fetchMode="one").data[0]
    botMessageID = bot.send_message(call.message.chat.id, f"Поставьте отметку для {userName}", reply_markup=markup).message_id
    bot.register_next_step_handler(call.message, rep_cm_step2, chatID, botMessageID)

def rep_cm_step2(message, chatID, bot_message_id):
    bot.delete_message(message.chat.id, bot_message_id)
    bot.delete_message(message.chat.id, message_id=message.message_id)
    if message.text == "Отмена":
        return
    conn = SQL_connection()
    x = conn.SQL_fetchone("SELECT rep FROM timeOuts WHERE chatID = ?", (message.chat.id,))
    conn.sql_close()
    if x[0] > datetime.now().timestamp():
        bot.send_message(message.chat.id,
                         "Вам пока что нельзя пользоваться командой /rep. Ей можно пользоваться 1 раз в 1 час. Или раз в 10 минут с <b>kretoffer school premium</b>",
                         parse_mode="HTML", reply_markup=my_markup())
        return
    conn = SQL_connection()
    if message.text == "👍":
        conn.sql_command("UPDATE users SET rating = rating + 1 WHERE chatID = ?", (chatID,))
    elif message.text == "👎":
        conn.sql_command("UPDATE users SET rating = rating - 1 WHERE chatID = ?", (chatID,))
    conn.sql_command("UPDATE timeOuts SET rep = ? WHERE chatID = ?", (datetime.now().timestamp() + 3600, message.chat.id))
    conn.sql_save()
    user = conn.SQL_fetchone("SELECT first_name, rating FROM users WHERE chatID = ?", (chatID,))
    conn.sql_close()
    bot.send_message(message.chat.id, f"Ваш отзыв отправлен, теперь рейтинг {user[0]} равен {user[1]}", reply_markup=my_markup())
@bot.message_handler(commands=['delOldDz'])
def main(message):
    if message.chat.id != config.ADMIN_ID:
        bot.send_message(message.chat.id, "Недостаточнго прав")
    delOldDz(message)
def delTempSchools():
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM schools WHERE school = null')
    conn.commit()
    cur.close()
    conn.close()
    print("Временные школы удалены")
def delOldDz(message=None):
    folder_name = "sqls"
    folder = Path(folder_name)
    col = sum(1 for x in folder.iterdir())
    i = 0
    yesterday = datetime.today().date()
    yesterdaySPL = str(yesterday).split('-')
    for i in range(0, col):
        conn = sql.connect(f'./sqls/{i}.sql')
        cur = conn.cursor()
        j = 0
        v = int(yesterdaySPL[2]) - 1
        for j in range(0, 10):
            if v == 0:
                v = 31
            date = f'{v}.{yesterdaySPL[1]}.{yesterdaySPL[0]}'
            try:
                cur.execute('DELETE FROM dz WHERE date = ?', (date,))
            except sql.OperationalError:
                pass
            j += 1
            v -= 1
        conn.commit()
        conn.commit()
        cur.close()
        conn.close()
        i += 1
    for schoolID in data["schoolsData"]:
        for my_class in data["schoolsData"][schoolID]:
            array = []
            for el in data["schoolsData"][schoolID][my_class]["add_dz"]:
                date_string = data["schoolsData"][schoolID][my_class]["add_dz"][el]["date"]
                date_object = datetime.strptime(date_string, "%d.%m.%Y")
                timestamp = int(date_object.timestamp())
                if timestamp + 86400 < datetime.now().timestamp():
                    array.append(el)
            for ell in array:
                del data["schoolsData"][schoolID][my_class]["add_dz"][ell]
    save_data()
    if message is not None: bot.send_message(message.chat.id, "Старое дз на 10 дней назад удалено")
    else: print("Старое дз за последние 10 дней удалено")
@bot.message_handler(commands=['allMessage'])
def main(message):
  if (message.chat.id != config.ADMIN_ID):
    bot.send_message(message.chat.id, "Вам не доступна эта команда")
    return
  markup = types.ReplyKeyboardMarkup(row_width=1)
  btn = types.KeyboardButton("Отмена")
  markup.add(btn)
  bot.send_message(message.chat.id,'Введите сообщение которое отправится всем пользователям бота, для отмены напишите "отмена"', reply_markup=markup)
  bot.register_next_step_handler(message, allMesage)

def allMesage(message):
  if message.content_type == "text" and message.text.strip().lower() == "отмена":
    bot.send_message(message.chat.id, "отмена прошла успешно")
    return
  conn = sql_conn()
  cur = conn.cursor()

  cur.execute('SELECT chatID FROM users')
  users = cur.fetchall()

  cur.close()
  conn.close()

  for el in users:
    bot.forward_message(el[0], message.chat.id, message.message_id, disable_notification=True)
  bot.send_message(message.chat.id, "Все готово", reply_markup=my_markup())
@bot.message_handler(commands=['friends', 'друзья'])
def main(message):
    conn = sql_conn()
    cur = conn.cursor()
    info = ""
    if data["usersData"][str(message.chat.id)]["inviter"] is not None:
        cur.execute("SELECT first_name, last_name FROM users WHERE chatID = ?", (data["usersData"][str(message.chat.id)]["inviter"],))
        inviter = cur.fetchone()
        info += f"Вас пригалисл {inviter[0]} "
        if inviter[1] is not None and inviter[1] != "None": info += inviter[1]
    info += "\n\n Ваш друг — заработано с них алмазов\n\n"
    info += "Друзья:\n\n"
    for el in data["usersData"][str(message.chat.id)]["invited"]:
        cur.execute("SELECT first_name, last_name FROM users WHERE chatID = ?", (int(el),))
        friend = cur.fetchone()
        info += f"{friend[0]} "
        if friend[1] is not None and friend[1] != "None": info += friend[1]
        info += f" — {data['usersData'][str(message.chat.id)]['invited'][el]}\n"
    bot.send_message(message.chat.id, info)
@bot.message_handler(commands=['help', 'помощь'])
def main(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    btn = types.KeyboardButton("/start")
    markup.add(btn)
    info = "Чтобы начать пользоваться ботом пропишите /start, если вы пользуетесь ботом впервые, то вам нужно зарегестрироваться /start"
    bot.send_message(message.chat.id, info, reply_markup=markup)
@bot.message_handler(commands=['start', 'go'])
def main(message):
    if str(message.chat.id) not in data["usersData"]:
        data["usersData"][str(message.chat.id)] = {}
        data["usersData"][str(message.chat.id)]["invited"] = {}
        data["usersData"][str(message.chat.id)]["invitedCol"] = 0
        data["usersData"][str(message.chat.id)]["inviter"] = None
        data["education"][str(message.chat.id)] = {}
        save_data()
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE chatID = ?', (message.chat.id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user is None:
        conn = sql_conn()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO users (first_name, last_name, chatID, bagsTimeOut, autorizationStep, experience, level, coins, diamonds, tickets, rating) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (
            message.from_user.first_name, message.from_user.last_name, message.chat.id, 0, 0, 0, 0, 0, 0, 0, 0))
        tempData['usersData'][str(message.chat.id)] = {}
        start_command = message.text
        refer_id = str(start_command[7:])
        if refer_id != "" and refer_id != str(message.chat.id):
            data["usersData"][str(message.chat.id)]["inviter"] = int(refer_id)
            data["usersData"][str(refer_id)]["invitedCol"] += 1
            data["usersData"][str(refer_id)]["invited"][str(message.chat.id)] = 10
            save_data()
            cur.execute("UPDATE users SET diamonds = diamonds+10 WHERE chatID = ? OR chatID = ?",
                        (refer_id, message.chat.id))
            bot.send_message(refer_id, f"По вашей ссылке зарегестрировался пользователь @{message.from_user.username}")
        conn.commit()
        cur.execute("SELECT count(*) FROM users WHERE autorizationStep != 0")
        colUsers = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM schools")
        colSchools = cur.fetchone()[0]
        cur.close()
        conn.close()
        bot.send_message(message.chat.id,
                         f"Все данные которые вы предоставляете полностью конфиденциальны и не распространяются не каким образом. Нам нужны данные чтобы мы могли предоставить для вас ваше расписаниеи, д/з и т.п.\n\nУже зарегестрировались {colUsers} человек из {colSchools} школ")
        markup = types.InlineKeyboardMarkup()
        btnBel = types.InlineKeyboardButton("Беларусь", callback_data="first_register_step:Беларусь")
        btnRus = types.InlineKeyboardButton("Россия", callback_data="first_register_step:Россия")
        markup.row(btnBel)
        markup.row(btnRus)
        bot.send_message(message.chat.id, "Выбери страну", reply_markup=markup)
    elif user[6] == 0:
        conn = sql_conn()
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM users WHERE autorizationStep != 0")
        col = cur.fetchone()[0]
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, f"Все данные которые вы предоставляете полностью конфиденциальны и не распространяются не каким образом. Нам нужны данные чтобы мы могли предоставить для вас ваше расписаниеи, д/з и т.п.\n\nУже зарегестрировались {col}")
        markup = types.InlineKeyboardMarkup()
        btnBel = types.InlineKeyboardButton("Беларусь", callback_data="first_register_step:Беларусь")
        btnRus = types.InlineKeyboardButton("Россия", callback_data="first_register_step:Россия")
        markup.row(btnBel)
        markup.row(btnRus)
        bot.send_message(message.chat.id,"Выбери страну", reply_markup=markup)
    else:
        Go_start(message)
    if message.chat.id == config.ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("SQL", callback_data="adminSQL")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Terminal", callback_data="adminTerminal")
        markup.add(btn)
        bot.send_message(message.chat.id, "Функции админа", reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data.startswith("adminSQL"))
def adminSQL(call):
    bot.send_message(call.message.chat.id, "Введите SQL запрос")
    bot.register_next_step_handler(call.message, adminSQL_go)
def adminSQL_go(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("SQL", callback_data="adminSQL")
    markup.add(btn)
    try:
        conn = sql_conn()
        cur = conn.cursor()
        cur.execute(message.text)
        conn.commit()
        t = cur.fetchall()
        cur.close()
        conn.close()
        info = ""
        for el in t:
            info += f"\n{el}\n"
        bot.send_message(message.chat.id, f"Запрос выполнен\n\n{info}", reply_markup=markup)
    except Exception as _ex:
        bot.send_message(message.chat.id, f"Произошла ошибка {_ex}", reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data.startswith("adminTerminal"))
def adminTerminal(call):
    bot.send_message(call.message.chat.id, "Введите python запрос")
    bot.register_next_step_handler(call.message, adminTerminal_go)
def adminTerminal_go(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Terminal", callback_data="adminTerminal")
    markup.add(btn)
    global print
    oldPrint = print
    info = ""
    def pr(message):
        nonlocal info
        oldPrint(message)
        info += message + "\n\n"
    try:
        print = pr
        exec(message.text)
        print = oldPrint
        bot.send_message(message.chat.id, f"Команда выполнена\n\n{info}", reply_markup=markup)
    except Exception as _ex:
        bot.send_message(message.chat.id, f"Произошла ошибка {_ex}", reply_markup=markup)
def openShop(message):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE chatID = ?", (message.chat.id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Алмазы за монеты", callback_data="buy_diamonds_1")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Монеты за алмазы", callback_data="buy_coins_1")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Подарить монеты", callback_data="give_coins")
    markup.add(btn)
    bot.send_message(message.chat.id, f"<b>Баланс:</b>\nМонеты:{user[10]}\nАлмазы:{user[11]}\n\n<b>Магазин:</b>", reply_markup=markup, parse_mode='HTML')
@bot.callback_query_handler(func=lambda callback: callback.data == "give_coins")
def give_coins_s1(call):
    bot.send_message(call.message.chat.id, "Напишите ID человека которому вы хотите подарить монеты", reply_markup=cancel_markup)
    bot.register_next_step_handler(call.message, give_coins_s2)
def give_coins_s2(message):
    if message.text == "Отмена":
        bot.send_message(message.chat.id, "Отменено", reply_markup=my_markup())
        return
    try:
        chatID = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Кажется вы вписали не chatID, попробуйте ввести его снова")
        bot.register_next_step_handler(message, give_coins_s2)
        return
    chatID = SQL_one_command("SELECT chatID FROM users WHERE chatID = ?", (chatID,), fetchMode="one").data[0]
    if chatID == None:
        bot.send_message(message.chat.id, "Кажется вы вписали недействительный chatID, попробуйте ввести его снова")
        bot.register_next_step_handler(message, give_coins_s2)
        return
    bot.send_message(message.chat.id, "Впишите количество монет которое вы хотите подарить")
    bot.register_next_step_handler(message, give_coins_s3, chatID)
def give_coins_s3(message, chatID):
    if message.text == "Отмена":
        bot.send_message(message.chat.id, "Отменено", reply_markup=my_markup())
        return
    try:
        coins = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Кажется вы вписали не число, попробуйте ввести его снова")
        bot.register_next_step_handler(message, give_coins_s3, chatID)
        return
    commision = int(coins)*0.03
    userName = SQL_one_command("SELECT first_name FROM users WHERE chatID = ?", (chatID,), fetchMode="one").data[0]
    bot.send_message(message.chat.id, f"Вы точно хотите подарить {coins} монет {userName}. В качестве комисии с вас спишут {commision} монет. Всего спишут {coins+commision}", reply_markup=yes_or_no_markup)
    bot.register_next_step_handler(message, give_coins_s4, chatID, coins, commision)
def give_coins_s4(message, chatID, coins, commision):
    if message.text == "Нет":
        bot.send_message(message.chat.id, "Подарок отменен", reply_markup=my_markup())
        return
    elif message.text == "Да":
        userCoins = SQL_one_command("SELECT coins FROM users WHERE chatID = ?", (message.chat.id,), fetchMode="one").data[0]
        if userCoins < coins:
            bot.send_message(message.chat.id, "У вас недостаточно монет", reply_markup=my_markup())
            return
        conn = SQL_connection()
        conn.sql_command("UPDATE users SET coins = coins - ? WHERE chatID = ?", (coins+commision, message.chat.id))
        conn.sql_command("UPDATE users SET coins = coins + ? WHERE chatID = ?", (coins, chatID))
        conn.sql_save()
        conn.sql_close()
        bot.send_message(message.chat.id, f"Вы подарили {coins} монет", reply_markup=my_markup())
        bot.send_message(chatID, f"{message.from_user.first_name} подарил(а) вам {coins} монет")
    else:
        bot.send_message(message.chat.id, 'Я вас не понимаю, скажите нормально "Да" или "Нет"')
        bot.register_next_step_handler(message, give_coins_s4, chatID, coins, commision)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith("buy_diamonds_1"))
def buy_diamonds_1(call):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("1", callback_data="buy:diamonds:1")
    btn2 = types.InlineKeyboardButton("10", callback_data="buy:diamonds:10")
    btn3 = types.InlineKeyboardButton("100", callback_data="buy:diamonds:100")
    markup.row(btn1, btn2, btn3)
    bot.send_message(call.message.chat.id, "1 алмаз стоит 100 монет, выберите количество алмазов", reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith("buy_coins_1"))
def buy_coins_1(call):
    bot_message_id = bot.send_message(call.message.chat.id, "75 монет стоят 1 алмаз, впишите количество алмазов которые вы хотите обменять").message_id
    bot.register_next_step_handler(call.message, buy_coins_2, bot_message_id)
def buy_coins_2(message, bot_message_id):
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, bot_message_id)
    try:
        diamonds = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не число, попробуйте еще раз")
        bot.register_next_step_handler(message, buy_coins_2, bot_message_id)
        return
    userDiamonds = SQL_one_command("SELECT diamonds FROM users WHERE chatID = ?", (message.chat.id,), fetchMode="one").data[0]
    if userDiamonds < diamonds:
        bot.send_message(message.chat.id, "У вас нет столько алмазов")
        return
    SQL_one_command("UPDATE users SET diamonds = diamonds - ?, coins = coins + ? WHERE chatID = ?", (diamonds, diamonds*75, message.chat.id), commit=True)
    bot.send_message(message.chat.id, "Успешно")
@bot.callback_query_handler(func=lambda callback: callback.data.startswith("buy:diamonds:"))
def buy_diamonds(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    col = int(call.data.split(":")[2])
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute("SELECT coins FROM users WHERE chatID = ?", (call.message.chat.id,))
    coins = cur.fetchone()[0]
    cur.close()
    conn.close()
    price = col*100
    info = "Подтвердите покупку"
    if col >= 100:
        price = col*75
        info = "Для вас действует скидка 25%, подтвердите покупку"
    if price > coins:
        bot.send_message(call.message.chat.id, f"У вас недостаточно монет, вам нужно {price}")
        return
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Купить", callback_data=f"buy_diamonds:{col}:{price}")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Отмена", callback_data="cancel_buy")
    markup.add(btn)
    bot.send_message(call.message.chat.id, info, reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data.startswith("cancel_buy"))
def cancel(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Покупка отменена")
@bot.callback_query_handler(func=lambda callback: callback.data.startswith("buy_diamonds:"))
def buy_diamonds_2(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    message, colStr, priseStr = call.data.split(":")
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET diamonds = diamonds + ? WHERE chatID = ?", (colStr, call.message.chat.id))
    cur.execute("UPDATE users SET coins = coins - ? WHERE chatID = ?", (priseStr, call.message.chat.id))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(call.message.chat.id, "Покупка успешно совершена")
def gdz(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="school_infoo")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Попросить ответ у одноклассников", callback_data="help_classmates")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Спросить у всех", callback_data="help_classmates")
    markup.add(btn)
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute("SELECT class FROM users WHERE chatID = ?", (message.chat.id,))
    userClass = cur.fetchone()[0]
    cur.close()
    conn.close()
    for el in lessonsData["GDZ"]["by"]:
        btn = types.InlineKeyboardButton(el, callback_data=f"GDZ_s:{userClass[0]}:{el}")
        markup.add(btn)
    bot.send_message(message.chat.id, "Выбери предмет", reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('GDZ_s:'))
def main(call):
    print(call.message.chat.id)
    if "contry" not in data["usersData"][str(call.message.chat.id)]:
        bot.send_message(call.message.chat.id, "Что-то не так с вашим регионом, извините за неудобства")
        bot.send_message(config.ADMIN_ID, f"ЭТО СНОВА ПРОИЗОШЛО (строка 540, {call.message.chat.id})")
    if data["usersData"][str(call.message.chat.id)]["contry"] == "Беларусь":
        gos = "RB"
    elif data["usersData"][str(call.message.chat.id)]["contry"] == "Россия":
        gos = "RF"
    GDZ.route_gdz_s(call)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('gdz_0:'))
def main(call):
    GDZ.route_gdz_0(call)

def go_education(message):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute("SELECT class FROM users WHERE chatID = ?", (message.chat.id,))
    userClass = cur.fetchone()[0]
    cur.close()
    conn.close()
    if userClass is None:
        bot.send_message(message.chat.id, "Для начала укажите в каком вы классе в личном кабинете. Класс можно менять только раз в месяц")
        return
    if str(message.chat.id) not in data["education"] or data['education'][str(message.chat.id)] == {}:
        data['education'][str(message.chat.id)]['completed_lesson'] = 0
        data['education'][str(message.chat.id)]['completed_tests'] = 0
        data['education'][str(message.chat.id)]['my_courses'] = {}
        data['education'][str(message.chat.id)]['complet_lessons'] = {}
        data['education'][str(message.chat.id)]['complet_tests'] = {}
        data['education'][str(message.chat.id)]['completed_courses'] = 0
        data['education'][str(message.chat.id)]['completed_exams'] = {}
        data['education'][str(message.chat.id)]['complet_exams'] = 0
        data['education'][str(message.chat.id)]['GPA'] = 0
        data['education'][str(message.chat.id)]['exams_GPA'] = 0
        data['education'][str(message.chat.id)]['problems_solved'] = 0
        data['education'][str(message.chat.id)]['decided_correctly'] = 0
        save_data()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Мои курсы", callback_data="my_courses")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Уроки", callback_data="lessons_list")
    btn1 = types.InlineKeyboardButton("Курсы", callback_data="courses_list")
    markup.add(btn, btn1)
    btn = types.InlineKeyboardButton("Тесты", callback_data="tests_list")
    btn1 = types.InlineKeyboardButton("Шпаргалки", callback_data="cheat_sheets_list")
    markup.add(btn, btn1)
    btn = types.InlineKeyboardButton("Экзамены", callback_data="exams_list")
    markup.add(btn)
    text = f"Давай начнем обучение.\n\nТы прошел(а):\n{data['education'][str(message.chat.id)]['completed_lesson']} уроков" \
           f"\n{data['education'][str(message.chat.id)]['completed_courses']} учебных курсов\n{data['education'][str(message.chat.id)]['completed_tests']} тестов\n" \
           f"\nСредний балл: {data['education'][str(message.chat.id)]['GPA']}\n\nРешено задач: {data['education'][str(message.chat.id)]['problems_solved']}" \
           f"\nРешено правильно: {data['education'][str(message.chat.id)]['decided_correctly']}\n\nПройдено экзаменов: {len(data['education'][str(message.chat.id)]['completed_exams'])}\n" \
           f"Средний балл за экзамены: {data['education'][str(message.chat.id)]['exams_GPA']}"
    bot.send_message(message.chat.id, text, reply_markup=markup)
def my_courses(message):
    info = f"Вы прошли {data['education'][str(message.chat.id)]['completed_courses']} учебных курсов"
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Пройденные курсы", callback_data="completed_courses")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    for el in data['education'][str(message.chat.id)]['my_courses']:
        if not data['education'][str(message.chat.id)]['my_courses'][el]['completed']:
            btn = types.InlineKeyboardButton(lessonsData['courses'][el]['name'], callback_data=f"course:{el}")
            markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
def completed_courses(message):
    markup = types.InlineKeyboardMarkup()
    info = "Пройденныйе курсы:\n"
    for el in data['education'][str(message.chat.id)]['my_courses']:
        if data['education'][str(message.chat.id)]['my_courses'][el]["completed"]:
            i = lessonsData["courses"][str(el)]['name']
            btn = types.InlineKeyboardButton(i, callback_data=f"course:{el}")
            markup.add(btn)
    btn = types.InlineKeyboardButton("Назад", callback_data="my_courses")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
def courses_list(message):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT class FROM users WHERE chatID = ?', (message.chat.id,))
    userClass = int(cur.fetchone()[0][0])
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Другие классы", callback_data="courses_list_else")
    markup.add(btn)
    for el in lessonsData["subjects"]:
        btn = types.InlineKeyboardButton(lessonsData['subjects'][el], callback_data=f"courses_subject_list:{el}:{userClass}")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери предмет", reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('courses_list_else'))
def courses_list_else(call):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    classes = config.classes
    for el in classes:
        btn = types.InlineKeyboardButton(str(el), callback_data=f"courses_subject_list_else:{el}")
        markup.add(btn)
    bot.edit_message_text(message_id=call.message.message_id,chat_id=call.message.chat.id, text="Выбери класс", reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('courses_subject_list_else:'))
def courses_subject_list_else(call):
    userClass = call.data.split(":")[1]
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    for el in lessonsData["subjects"]:
        btn = types.InlineKeyboardButton(lessonsData['subjects'][el], callback_data=f"courses_subject_list:{el}:{userClass}")
        markup.add(btn)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбери предмет", reply_markup=markup)
def courses_subject_list(message, subject, userClass):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="courses_list")
    markup.add(btn)
    for el in lessonsData['courses']:
        if el != "_comment":
            if lessonsData["courses"][el]["subject"] == subject and lessonsData["courses"][el]["class"] == userClass:
                if el not in data['education'][str(message.chat.id)]['my_courses'] or not data['education'][str(message.chat.id)]['my_courses'][el]['completed']:
                    btn = types.InlineKeyboardButton(lessonsData['courses'][el]['name'], callback_data=f"course:{el}")
                    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери курс",reply_markup=markup)
def start_course(message, courseID):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Начать урок", callback_data=f"go_course_lesson:{courseID}")
    markup.add(btn)
    info = f"Курс {lessonsData['courses'][str(courseID)]['name']}:\n{lessonsData['courses'][str(courseID)]['subtitle']}\n\nКласс: {lessonsData['courses'][str(courseID)]['class']}\nУроков: {len(lessonsData['courses'][str(courseID)]['lessons'])}\n\nРекомендации к курсу: {lessonsData['courses'][str(courseID)]['recommendations']}\n"
    if str(courseID) in data['education'][str(message.chat.id)]['my_courses']:
        info += f"Пройдено уроков: {data['education'][str(message.chat.id)]['my_courses'][str(courseID)]['completed_lessons']}"
        if data['education'][str(message.chat.id)]['my_courses'][str(courseID)]['completed']:
            btn = types.InlineKeyboardButton("Обнулить курс", callback_data=f"course_back:{courseID}")
            markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
def go_course_lesson(message, courseID):
    if str(courseID) in data['education'][str(message.chat.id)]['my_courses']:
        pass
    else:
        data['education'][str(message.chat.id)]['my_courses'][str(courseID)]={"completed_lessons":0, "completed":False}
    data['education'][str(message.chat.id)]['my_courses'][str(courseID)]['completed_lessons']+=1
    i = data['education'][str(message.chat.id)]['my_courses'][str(courseID)]['completed_lessons']
    if i >= len(lessonsData['courses'][str(courseID)]['lessons']):
        if not data['education'][str(message.chat.id)]['my_courses'][str(courseID)]['completed']:
            data['education'][str(message.chat.id)]['completed_courses']+=1
            data['education'][str(message.chat.id)]['my_courses'][str(courseID)]['completed'] = True
            SQL_one_command("UPDATE users SET experience = experience + 3 WHERE chatID = ?", (message.chat.id,), commit=True)
        else:
            SQL_one_command("UPDATE users SET experience = experience + 1 WHERE chatID = ?", (message.chat.id,), commit=True)
        data['education'][str(message.chat.id)]['my_courses'][str(courseID)]['completed_lessons'] = len(lessonsData['courses'][str(courseID)]['lessons'])
        i = len(lessonsData['courses'][str(courseID)]['lessons'])
    save_data()
    start_lesson(message, lessonsData['courses'][str(courseID)]['lessons'][str(i)], 1)

@bot.callback_query_handler(func=lambda callback: callback.data == 'exams_list')
def exams_list(call):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT class FROM users WHERE chatID = ?', (call.message.chat.id,))
    userClass = int(cur.fetchone()[0][0])
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Другие классы", callback_data="exams_list_else")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Пройденные экзамены", callback_data="completed_exams_list")
    #markup.add(btn)
    for el in lessonsData["exams"][f"{userClass}class"]["subjects"]:
        btn = types.InlineKeyboardButton(lessonsData["subjects"][el], callback_data=f"exams_subject_list:{el}:{userClass}")
        markup.add(btn)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбери предмет", reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data == 'exams_list_else')
def exams_list_else(call):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    classes = config.classes
    for el in classes:
        btn = types.InlineKeyboardButton(str(el), callback_data=f"exams_subject_list_else:{el}")
        markup.add(btn)
    bot.edit_message_text(message_id=call.message.message_id,chat_id=call.message.chat.id, text="Выбери класс", reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('exams_subject_list_else:'))
def exams_subject_list_else(call):
    userClass = call.data.split(":")[1]
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    for el in lessonsData["exams"][f"{userClass}class"]["subjects"]:
        btn = types.InlineKeyboardButton(lessonsData['subjects'][el], callback_data=f"exams_subject_list:{el}:{userClass}")
        markup.add(btn)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбери предмет", reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('exams_subject_list:'))
def lessons_theme_list(call):
    message, subject, userClass = call.data.split(":")
    message = call.message
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"lessons_subject_list:{subject}:{userClass}")
    markup.add(btn)
    for el in lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["exams"]:
        btn = types.InlineKeyboardButton(lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["exams"][el]["name"], callback_data=f"exam:{userClass}:{subject}:{el}:1:0:0:N")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери экзамен",reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('exam_statistic'))
def exam_statistic(call):
    seeType:None
    if len(i := call.data.split(":")) >= 2:
        seeType = i[1]
    if seeType == "last":
        examID = data["examsData"][str(call.message.chat.id)]["last"]["examID"]
        userClass = data["examsData"][str(call.message.chat.id)]["last"]["class"]
        subject = data["examsData"][str(call.message.chat.id)]["last"]["subject"]
        examName = lessonsData['exams'][f'{userClass}class']['subjects'][subject]['exams'][examID]["name"]
        info = "Последний экзамен:\n\n" \
               f"{examName}\n{lessonsData['subjects'][subject]} {userClass} класс\n\n"\
                "Вопросы:\n"
        for el in data["examsData"][str(call.message.chat.id)]["last"]["questions"]:
            info += f"{el}. {data['examsData'][str(call.message.chat.id)]['last']['questions'][el]['question']}\n" \
                    f"Правильный ответ: {data['examsData'][str(call.message.chat.id)]['last']['questions'][el]['answer']}\n" \
                    f"Ответ пользователя: {data['examsData'][str(call.message.chat.id)]['last']['questions'][el]['userAnswer']}\n\n"
    bot.send_message(call.message.chat.id, info)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('exam:'))
def exam(call):
    message, userClass, subject, examID, examType, step, score, status = call.data.split(":")
    message = call.message
    markup = types.InlineKeyboardMarkup()
    text = ""
    if status == "0":
        score = int(score)+1
        text += "Верно\n\n"
    else:
        if status == "N":
            ...
        if step != "0":
            text += "Не верно\n\n"
    score = int(score)
    if str(message.chat.id) not in data["examsData"]:
        data["examsData"][str(message.chat.id)] = {"last":{}}
    if str(step) != "0":
        if status == "0":
            u = "Верный"
        else:
            u = "Не верный"
        data["examsData"][str(message.chat.id)]["last"]["questions"][str(step)]["userAnswer"] = u
    if int(step) >= 10:
        markup.add(types.InlineKeyboardButton("Назад", callback_data="education"))
        markup.add(types.InlineKeyboardButton("Характеристика", callback_data=f"exam_statistic:last"))
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"Экзамен из 10 вопросов завершен\n\nПравильных ответов: {score}", reply_markup=markup)
        data['education'][str(message.chat.id)]['exams_GPA'] = round((data['education'][str(message.chat.id)]['exams_GPA'] + int(score)) / 2, 2)
        data["examsData"][str(message.chat.id)]["last"]["endTime"] = int(datetime.now().timestamp())
        if len(data['education'][str(message.chat.id)]['completed_exams']) == 0:
            data['education'][str(message.chat.id)]['exams_GPA'] = int(score)
        if userClass not in data['education'][str(message.chat.id)]['completed_exams']:
            data['education'][str(message.chat.id)]['completed_exams'][userClass] = {
                subject: {}
            }
        elif subject not in data['education'][str(message.chat.id)]['completed_exams'][userClass]:
            data['education'][str(message.chat.id)]['completed_exams'][userClass][subject] = {}
        if examID not in data['education'][str(message.chat.id)]['completed_exams'][userClass][subject]:
            data['education'][str(message.chat.id)]['complet_exams'] += 1
            data['education'][str(message.chat.id)]['completed_exams'][userClass][subject][examID] = {
                "count": 1,
                "answers" : int(step),
                "correctAnswers": int(score)
            }
            mistacesAnswers = 10 - score
            addEx = (5 * score) - (5 * mistacesAnswers)
            SQL_one_command("UPDATE users SET experience = experience + ? WHERE chatID = ?", (addEx, message.chat.id), commit=True)
        else:
            data['education'][str(message.chat.id)]['completed_exams'][userClass][subject][examID]["count"] += 1
            data['education'][str(message.chat.id)]['completed_exams'][userClass][subject][examID]["answers"] += int(step)
            data['education'][str(message.chat.id)]['completed_exams'][userClass][subject][examID]["correctAnswers"] += int(score)
            mistacesAnswers = 10 - score
            addEx = (0.5 * score) - (0.5 * mistacesAnswers)
            if addEx < 0:
                addEx -= 0.5
            addEx = int(addEx)
            SQL_one_command("UPDATE users SET experience = experience + ? WHERE chatID = ?", (addEx, message.chat.id), commit=True)
        save_data()
        return
    questionGroupId = random.choice(lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["exams"][examID]["types"][examType])
    questionId = "info"
    while questionId == "info":
        questionId = str(random.randint(1, len(lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["questions"][questionGroupId])))
    examQType = lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["questions"][questionGroupId][questionId]["type"]
    if examQType == 3:
        examQType = random.randint(1, 2)
    if str(step) == "0":
        data["examsData"][str(message.chat.id)]["last"] = {
            "examID": examID,
            "questions":{"1":{
                "questionLevel": lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["questions"][questionGroupId][questionId]["level"],
                "question": lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["questions"][questionGroupId][questionId]["question"],
                "answer": lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["questions"][questionGroupId][questionId]["answers"][0]
            }},
            "class": userClass,
            "subject": subject,
            "startTime": int(datetime.now().timestamp()),
            "endTime" : None
        }
    else:
        data["examsData"][str(message.chat.id)]["last"]["questions"][str(int(step) + 1)] = {
            "questionLevel": lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["questions"][questionGroupId][questionId]["level"],
            "question": lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["questions"][questionGroupId][questionId]["question"],
            "answer": lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["questions"][questionGroupId][questionId]["answers"][0],
            "userAnswer": None
        }
    save_data()
    text += f'Уровень: <b>{lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["questions"][questionGroupId][questionId]["level"]}</b>\n\n{lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["questions"][questionGroupId][questionId]["question"]}'
    step = int(step) + 1
    match examQType:
        case 1:
            text+="\n\nВыберите правильный вариант ответа"
            btns = []
            btn = types.InlineKeyboardButton(
                lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["questions"][questionGroupId][questionId]["answers"][0],
                callback_data=f"exam:{userClass}:{subject}:{examID}:{examType}:{step}:{score}:0")
            btns.append(btn)
            i = 1
            for i in range(1, len(lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["questions"][questionGroupId][questionId]["answers"])):
                btn = types.InlineKeyboardButton(lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["questions"][questionGroupId][questionId]["answers"][i],
                                                 callback_data=f"exam:{userClass}:{subject}:{examID}:{examType}:{step}:{score}:{i}")
                btns.append(btn)
                i+=1
            random.shuffle(btns)
            for btn in btns:
                markup.add(btn)
        case 2:
            text+="\n\nНапишите правильный вариант"
            answer = lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["questions"][questionGroupId][questionId]["answers"][0]
            tempData["usersData"][str(message.chat.id)]["exam_question"] = lessonsData["exams"][f"{userClass}class"]["subjects"][subject]["questions"][questionGroupId][questionId]["question"]
            bot.register_next_step_handler(message, ansver_to_exam_question, userClass, subject, examID, examType, step, score, answer, message.message_id)
            markup = types.InlineKeyboardMarkup()
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=text, reply_markup=markup, parse_mode="HTML")

def ansver_to_exam_question(message, userClass, subject, examID, examType, step, score, answer, bot_message_id):
    markup = types.InlineKeyboardMarkup()
    #data["examsData"][str(message.chat.id)]["last"]["questions"][str(step)]["yourAnswer"] = message.text
    save_data()
    btn = types.InlineKeyboardButton("Подтвердить", callback_data=f"exam:{userClass}:{subject}:{examID}:{examType}:{step}:{score}:N")
    if message.text.lower() == answer.lower():
        btn = types.InlineKeyboardButton("Подтвердить", callback_data=f"exam:{userClass}:{subject}:{examID}:{examType}:{step}:{score}:0")
    markup.add(btn)
    tempData["usersData"][str(message.chat.id)]["exam_answer"] = answer
    btn = types.InlineKeyboardButton("Отмена", callback_data=f"c_q_exam:{userClass}:{subject}:{examID}:{examType}:{step}:{score}")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=bot_message_id, text=f'Вы уверены в ответе "{message.text}"?', reply_markup=markup)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('c_q_exam:'))
def cancel_questoin_exam(call):
    message, userClass, subject, examID, examType, step, score = call.data.split(":")
    message = call.message
    markup = types.InlineKeyboardMarkup()
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Ответьте на вопрос\n\n"+tempData["usersData"][str(message.chat.id)]["exam_question"], reply_markup=markup)
    bot.register_next_step_handler(message, ansver_to_exam_question, userClass, subject, examID, examType, step, score, tempData["usersData"][str(message.chat.id)]["exam_answer"], message.message_id)

def lessons_list(message):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT class FROM users WHERE chatID = ?', (message.chat.id,))
    userClass = int(cur.fetchone()[0][0])
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Пройденные уроки", callback_data="completed_lessons_list")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Другие классы", callback_data="lessons_list_else")
    markup.add(btn)
    for el in lessonsData["subjects"]:
        btn = types.InlineKeyboardButton(lessonsData["subjects"][el], callback_data=f"lessons_subject_list:{el}:{userClass}")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери предмет", reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('lessons_list_else'))
def courses_list_else(call):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    classes = config.classes
    for el in classes:
        btn = types.InlineKeyboardButton(str(el), callback_data=f"lessons_subject_list_else:{el}")
        markup.add(btn)
    bot.edit_message_text(message_id=call.message.message_id,chat_id=call.message.chat.id, text="Выбери класс", reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('lessons_subject_list_else:'))
def courses_subject_list_else(call):
    userClass = call.data.split(":")[1]
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    for el in lessonsData["subjects"]:
        btn = types.InlineKeyboardButton(lessonsData['subjects'][el], callback_data=f"lessons_subject_list:{el}:{userClass}")
        markup.add(btn)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбери предмет", reply_markup=markup)
def проверка_на_то_пройдены_ли_все_уроки_темы(userClass, chatID, theme):
    for elem in lessonsData["lessons"]["themes"][f"{userClass}classThemes"][theme]["list"]:
        if elem not in data['education'][str(chatID)]["complet_lessons"]:
            return True
    return False
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('lessons_subject_list:'))
def lessons_subject_list(callback):
    message, subject, userClass = callback.data.split(":")
    message = callback.message
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="lessons_list")
    markup.add(btn)
    for el in lessonsData["lessons"]["themes"][f"{userClass}classThemes"]:
        if lessonsData["lessons"]["themes"][f"{userClass}classThemes"][el]["subject"] == subject:
            if проверка_на_то_пройдены_ли_все_уроки_темы(userClass, message.chat.id, el):
                btn = types.InlineKeyboardButton(el, callback_data=f"lessons_theme_list:{subject}:{userClass}:{lessonsData['lessons']['themes'][f'{userClass}classThemes'][el]['id']}")
                markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери тему",reply_markup=markup)
def lessons_theme_list_p(userClass,id):
    for el in lessonsData["lessons"]["themes"][f"{userClass}classThemes"]:
        if lessonsData["lessons"]["themes"][f"{userClass}classThemes"][el]["id"] == id:
            return el
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('lessons_theme_list:'))
def lessons_theme_list(call):
    message, subject, userClass, theme = call.data.split(":")
    message = call.message
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"lessons_subject_list:{subject}:{userClass}")
    markup.add(btn)
    theme = lessons_theme_list_p(userClass, int(theme))
    for el in lessonsData["lessons"]["themes"][f"{userClass}classThemes"][theme]["list"]:
        if el not in data["education"][str(message.chat.id)]["complet_lessons"]:
            btn = types.InlineKeyboardButton(lessonsData["lessons"][el]["name"], callback_data=f"lesson:{el}:1")
            markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери урок",reply_markup=markup)
def completed_lessons_list(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="lessons_list")
    markup.add(btn)
    for el in lessonsData['lessons']:
        if el in data['education'][str(message.chat.id)]['complet_lessons']:
            btn = types.InlineKeyboardButton(lessonsData['lessons'][el]['name'], callback_data=f"lesson:{el}:1")
            markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Пройденные уроки:", reply_markup=markup)
def tests_list(message):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT class FROM users WHERE chatID = ?', (message.chat.id,))
    userClass = int(cur.fetchone()[0][0])
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Пройденные тесты", callback_data="completed_tests_list")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Другие классы", callback_data="tests_list_else")
    markup.add(btn)
    for el in lessonsData["subjects"]:
        btn = types.InlineKeyboardButton(lessonsData["subjects"][el],callback_data=f"tests_subject_list:{el}:{userClass}")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери предмет",reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('tests_list_else'))
def courses_list_else(call):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    classes = config.classes
    for el in classes:
        btn = types.InlineKeyboardButton(str(el), callback_data=f"tests_subject_list_else:{el}")
        markup.add(btn)
    bot.edit_message_text(message_id=call.message.message_id,chat_id=call.message.chat.id, text="Выбери класс", reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('tests_subject_list_else:'))
def courses_subject_list_else(call):
    userClass = call.data.split(":")[1]
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    for el in lessonsData["subjects"]:
        btn = types.InlineKeyboardButton(lessonsData['subjects'][el], callback_data=f"tests_subject_list:{el}:{userClass}")
        markup.add(btn)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбери предмет", reply_markup=markup)
def проверка_на_то_пройдены_ли_все_тесты_темы(userClass, chatID, theme):
    for elem in lessonsData["tests"]["themes"][f"{userClass}classThemes"][theme]["list"]:
        if elem not in data['education'][str(chatID)]["complet_tests"]:
            return True
    return False
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('tests_subject_list:'))
def tests_list_subject(call):
    message, subject, userClass = call.data.split(":")
    message = call.message
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="tests_list")
    markup.add(btn)
    for el in lessonsData["tests"]["themes"][f"{userClass}classThemes"]:
        if lessonsData["tests"]["themes"][f"{userClass}classThemes"][el]["subject"] == subject:
            if проверка_на_то_пройдены_ли_все_тесты_темы(userClass, message.chat.id, el):
                btn = types.InlineKeyboardButton(el, callback_data=f"tests_theme_list:{subject}:{userClass}:{lessonsData['tests']['themes'][f'{userClass}classThemes'][el]['id']}")
                markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери тему",reply_markup=markup)
def tests_theme_list_p(userClass,id):
    for el in lessonsData["tests"]["themes"][f"{userClass}classThemes"]:
        if lessonsData["tests"]["themes"][f"{userClass}classThemes"][el]["id"] == id:
            return el
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('tests_theme_list:'))
def tests_theme_list(call):
    message, subject, userClass, theme = call.data.split(":")
    message = call.message
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"tests_subject_list:{subject}:{userClass}")
    markup.add(btn)
    theme = tests_theme_list_p(userClass, int(theme))
    for el in lessonsData["tests"]["themes"][f"{userClass}classThemes"][theme]["list"]:
        if el not in data["education"][str(message.chat.id)]["complet_tests"]:
            btn = types.InlineKeyboardButton(lessonsData["tests"][el]["name"], callback_data=f"test:{el}:1:0:False")
            markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери тест",reply_markup=markup)
def completed_tests_list(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="tests_list")
    markup.add(btn)
    for el in lessonsData['tests']:
        if el in data['education'][str(message.chat.id)]['complet_tests']:
            btn = types.InlineKeyboardButton(lessonsData['tests'][el]['name'], callback_data=f"test:{el}:1:0:False")
            markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Пройденные тесты:", reply_markup=markup)
def cheat_sheets_list(message):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT class FROM users WHERE chatID = ?', (message.chat.id,))
    userClass = int(cur.fetchone()[0][0])
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Другие классы", callback_data="cs_list_else")
    markup.add(btn)
    for el in lessonsData["subjects"]:
        btn = types.InlineKeyboardButton(lessonsData["subjects"][el], callback_data=f"sen_cheat_sheets_list:{el}:{userClass}")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери предмет", reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('cs_list_else'))
def courses_list_else(call):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    classes = config.classes
    for el in classes:
        btn = types.InlineKeyboardButton(str(el), callback_data=f"cs_subject_list_else:{el}")
        markup.add(btn)
    bot.edit_message_text(message_id=call.message.message_id,chat_id=call.message.chat.id, text="Выбери класс", reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('cs_subject_list_else:'))
def courses_subject_list_else(call):
    userClass = call.data.split(":")[1]
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    for el in lessonsData["subjects"]:
        btn = types.InlineKeyboardButton(lessonsData['subjects'][el], callback_data=f"cs_subject_list:{el}:{userClass}")
        markup.add(btn)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбери предмет", reply_markup=markup)
def start_lesson(message, lessonID, index):
    markup = types.InlineKeyboardMarkup()
    if index == len(lessonsData["lessons"][lessonID]["text"]):
        if str(lessonID) in data['education'][str(message.chat.id)]['complet_lessons']:
            data['education'][str(message.chat.id)]['complet_lessons'][str(lessonID)]+=1
        else:
            data['education'][str(message.chat.id)]['completed_lesson']+=1
            data['education'][str(message.chat.id)]['complet_lessons'][str(lessonID)]=1
            SQL_one_command("UPDATE users SET experience = experience + 1 WHERE chatID = ?", (message.chat.id,), commit=True)
        save_data()
        if lessonsData["lessons"][lessonID]["test"] is not None:
            btn = types.InlineKeyboardButton("Пройти тест", callback_data=f'test:{lessonsData["lessons"][lessonID]["test"]}:1:0:False')
            markup.add(btn)
        if "videoLesson" in lessonsData["lessons"][lessonID] and lessonsData["lessons"][lessonID]["videoLesson"] is not None:
            btn = types.InlineKeyboardButton("Видеоурок", url=lessonsData["lessons"][lessonID]["videoLesson"])
            markup.add(btn)
    else:
        btn = types.InlineKeyboardButton("Дальше", callback_data=f'lesson:{lessonID}:{index+1}')
        markup.add(btn)
    btn = types.InlineKeyboardButton("Закончить", callback_data='lessons_list')
    markup.add(btn)
    info = lessonsData["lessons"][lessonID]["text"][str(index)]
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup, parse_mode='HTML')
def start_test(message, testID, index, score, true=False):
    markup = types.InlineKeyboardMarkup()
    question = ""
    if index != 1 and not true:
        question += "Не верно\nПравильный ответ: " + lessonsData["tests"][testID]["questions"][f"{index-1}variants"]["1"] + "\n\n"
    if true:
        question += "Верно\n\n"
        score+=1
    if index > len(lessonsData["tests"][testID]["questions"])/2:
        info = f"Результат теста\nВопросов: {index-1}\nПравильных ответов: {score}"
        if str(testID) in data['education'][str(message.chat.id)]['complet_tests']:
            data['education'][str(message.chat.id)]['complet_tests'][str(testID)]+=1
            mistacesAnswers = index - 1 - score
            addEx = (0.5 * score) - (2 * mistacesAnswers)
            if addEx < 0:
                addEx -= 0.5
            addEx = int(addEx)
            SQL_one_command("UPDATE users SET experience = experience + ? WHERE chatID = ?", (addEx, message.chat.id), commit=True)
        else:
            data['education'][str(message.chat.id)]['completed_tests']+=1
            i = 10/(index-1)*score
            t = data['education'][str(message.chat.id)]['GPA']
            if data['education'][str(message.chat.id)]["completed_tests"] == 1: t = i
            data['education'][str(message.chat.id)]['GPA'] = round((i+t)/2, 2)
            data['education'][str(message.chat.id)]['complet_tests'][str(testID)]=1
            mistacesAnswers = index - 1 - score
            addEx = (2 * score) - (3 * mistacesAnswers)
            SQL_one_command("UPDATE users SET experience = experience + ? WHERE chatID = ?", (addEx, message.chat.id), commit=True)
        data['education'][str(message.chat.id)]['problems_solved'] += index - 1
        data['education'][str(message.chat.id)]['decided_correctly'] += score
        save_data()
        btn = types.InlineKeyboardButton("Выйти", callback_data="education")
        markup.add(btn)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
    else:
        question += lessonsData["tests"][testID]["questions"][str(index)]
        method = [1,2,3,4]
        random.shuffle(method)
        for el in method:
            if el == 1:
                btn = types.InlineKeyboardButton(lessonsData["tests"][testID]["questions"][f"{index}variants"][str(el)], callback_data=f'test:{testID}:{index+1}:{score}:True')
            else:
                btn = types.InlineKeyboardButton(lessonsData["tests"][testID]["questions"][f"{index}variants"][str(el)],callback_data=f'test:{testID}:{index+1}:{score}:False')
            markup.add(btn)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=question, reply_markup=markup, parse_mode='HTML')
#Не используется, не получается отправить видео
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('videoLesson:'))
def videoLesson(call):
    lessonId = call.data.split(":")[1]
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Закончить", callback_data='lessons_list')
    markup.add(btn)
    bot.send_video(call.message.chat.id, lessonsData["lessons"][lessonId]["videoLesson"])
    bot.delete_message(call.message.chat.id, call.message.message_id)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('cs_subject_list:'))
def cs_subject_list(call):
    message, subject, userClass = call.data.split(":")
    sen_cheat_sheets_list(call.message, subject, userClass)
def sen_cheat_sheets_list(message, subject, userClass):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="cheat_sheets_list")
    markup.add(btn)
    for el in lessonsData["cheat_sheets"][f"{userClass}class"]:
        if lessonsData["cheat_sheets"][f"{userClass}class"][el]["subject"] == subject:
            btn = types.InlineKeyboardButton(el, callback_data=f"s_theme_list:{subject}:{userClass}:{lessonsData['cheat_sheets'][f'{userClass}class'][el]['id']}")
            markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери тему", reply_markup=markup)
def s_theme_list_p(userClass,id):
    for el in lessonsData["cheat_sheets"][f"{userClass}class"]:
        if lessonsData["cheat_sheets"][f"{userClass}class"][el]["id"] == id:
            return el
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('s_theme_list:'))
def s_theme_list(call):
    message, subject, userClass, theme = call.data.split(":")
    message = call.message
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"sen_cheat_sheets_list:{subject}:{userClass}")
    markup.add(btn)
    Otheme=theme
    theme = s_theme_list_p(userClass, int(theme))
    for el in lessonsData["cheat_sheets"][f"{userClass}class"][theme]:
        if el not in ["subject", "id"]:
            btn = types.InlineKeyboardButton(lessonsData["cheat_sheets"][f"{userClass}class"][theme][el]["name"], callback_data=f"sen_cheat_sheets:{userClass}:{Otheme}:{el}")
            markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери шпаргалку",reply_markup=markup)
def sen_cheat_sheets(message, userClass, Otheme, cheat_sheetsID):
    theme = s_theme_list_p(userClass, int(Otheme))
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"s_theme_list:{lessonsData['cheat_sheets'][f'{userClass}class'][theme]['subject']}:{userClass}:{Otheme}")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=lessonsData['cheat_sheets'][f'{userClass}class'][theme][cheat_sheetsID]["text"], reply_markup=markup, parse_mode='HTML')
def Go_start(message):
    bot.send_message(message.chat.id, "Привет, я твой телеграм бот помощник. Что ты хочешь узнать?", reply_markup=my_markup())
    if bot.get_chat_member(config.CHANEL_ID, message.chat.id).status not in ["member", "administrator", "creator"]:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Подписаться", url="https://t.me/kretoffer_school_chanel")
        markup.add(btn)
        bot.send_message(message.chat.id,"Вы еще не подписаны на наш канал, там вы можете найти что-то интересное", reply_markup=markup)
def save_data():
    with open('data.json', 'w') as f:
        json.dump(data, f)
def my_room(message):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE chatID = "%s"'%(message.chat.id))
    info = cur.fetchone()
    cur.close()
    conn.close()
    if info is None or info[6] == 0:
        bot.send_message(message.chat.id, "Что-то пошло не так, похоже вы не зарегестрировались, пропишите /start")
        return
    t = my_libs.ExLevel.levelCalculate(message.chat.id)
    if t:
        info = SQL_one_command("SELECT * FROM users WHERE chatID = ?", (message.chat.id,), fetchMode="one").data
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Школа", callback_data=f"school_info:{info[5]}")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Пригласить друга", callback_data="invite_frend")
    markup.add(btn)
    if (info[13] is None):
        btn = types.InlineKeyboardButton("Выбрать класс", callback_data="class_vibor")
    else:
        btn = types.InlineKeyboardButton("Изменить класс", callback_data="class_vibor")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Изменить имя", callback_data=f"new_name:{message.chat.id}")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Изменить фамилию", callback_data=f"new_last_name:{message.chat.id}")
    markup.add(btn)
    tempData["usersData"][str(message.chat.id)]["tempMessage"] = message
    infoText = f"ID: {info[3]}\n\nИмя: {info[1]}\nФамилия: {info[2]}\n\nКласс: {info[13]}\n\nОпыт: {info[8]}\nУровень: {info[9]}\nМонеты: {info[10]}\nАлмазы: {info[11]}\nБилеты: {info[12]}\n\nРейтинг: {info[14]}\n\nПриглашено друзей: {data['usersData'][str(message.chat.id)]['invitedCol']}"
    bot.send_message(message.chat.id, infoText, reply_markup=markup)

@bot.message_handler(commands=['op'])
def main(message):
  if (message.chat.id != config.ADMIN_ID):
    bot.send_message(message.chat.id, "Вам не доступна эта команда")
    return
  bot.send_message(message.chat.id, 'Введите имя администратора')
  bot.register_next_step_handler(message, addAdmin)

@bot.message_handler(commands=['deop'])
def main(message):
  if (message.chat.id != config.ADMIN_ID):
    bot.send_message(message.chat.id, "Вам не доступна эта команда")
    return
  bot.send_message(message.chat.id, 'Введите имя администратора')
  bot.register_next_step_handler(message, delAdmin)

def delAdmin(message):
  conn = sql_conn()
  cur = conn.cursor()
  cur.execute('SELECT * FROM admins')
  cur.execute('DELETE FROM admins WHERE name = "%s"' % (message.text.strip()))
  conn.commit()
  cur.close()
  conn.close()

def addAdmin(message):
  if (message.text.strip().lower() == 'отмена'):
    bot.send_message(message.chat.id, 'Отменено')
    return
  conn = sql_conn()
  cur = conn.cursor()

  cur.execute('SELECT * FROM users')
  users = cur.fetchall()

  chatID = None

  for el in users:
    if(message.text.strip() == el[1]):
      chatID = el[3]
  if chatID is None:
    bot.send_message(message.chat.id, "Такого пользователя не существует")
    cur.close()
    conn.close()
    return

  cur.execute('INSERT INTO admins (name, chatID) VALUES ("%s", "%s")' % (message.text.strip(), chatID))
  conn.commit()
  bot.send_message(message.chat.id, 'Администратор успешно добавлен')
  cur.close()
  conn.close()

def school_info(message):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT class FROM users WHERE chatID = ?', (message.chat.id,))
    if cur.fetchone()[0] is None:
        bot.send_message(message.chat.id, "Сначала укажите класс в личном кабинете")
        cur.close()
        conn.close()
        return
    cur.execute('SELECT schoolID FROM users WHERE chatID = ?', (message.chat.id,))
    temp = cur.fetchone()
    schoolID = temp[0]
    cur.execute('SELECT class FROM users WHERE chatID = ?', (message.chat.id,))
    temp = cur.fetchone()
    my_class = temp[0]
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Расписание на сегодня", callback_data=f"rasp:{schoolID}:{my_class}:0")
    btn2 = types.InlineKeyboardButton("Расписание на завтра", callback_data=f"rasp:{schoolID}:{my_class}:1")
    markup.add(btn1, btn2)
    btn = types.InlineKeyboardButton("Расписание на неделю", callback_data=f"rasp:{schoolID}:{my_class}:2")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Новости", callback_data=f"news:{schoolID}:{my_class}")
    #markup.add(btn)
    btn1 = types.InlineKeyboardButton("Дз", callback_data=f"homeTask:{schoolID}:{my_class}:0")
    btn2 = types.InlineKeyboardButton("ГДЗ", callback_data="GDZ")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Что ты хочешь узнать?", reply_markup=markup)
def rasp(message, schoolID, scholl_class, id):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="school_infoo")
    markup.add(btn)
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    v = 0
    if id == "0":
        v = datetime.today().weekday()
    elif id == "1":
        v = datetime.today().weekday()+1
        if v == 7:
            v = 0
    if id == "2":
        i = 0
        info = "Расписание:\n"
        t = ["Понедельник","Вторник","Среда","Четверг","Пятница","Суббота","Воскресение"]
        for i in range(0, 7):
            cur.execute("SELECT * FROM rasp WHERE class = ? AND day = ?", (scholl_class, i))
            rasp = cur.fetchone()
            if rasp is not None:
                info += "\n<b>"+t[i]+":</b>\n"
                j = 0
                for j in range(0, 10):
                    if rasp[j + 3] is not None:
                        info += str(j + 1) + ". " + rasp[j + 3] + "\n"
                    j += 1
            i += 1
        cur.close()
        conn.close()
        btn = types.InlineKeyboardButton("Изменить расписание", callback_data=f"add_rasp_list:{schoolID}:{scholl_class}")
        markup.add(btn)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup, parse_mode='HTML')
        return
    cur.execute("SELECT * FROM rasp WHERE class = ? AND day = ?", (scholl_class, v))
    rasp = cur.fetchone()
    cur.close()
    conn.close()
    if rasp is None:
        btn = types.InlineKeyboardButton("Добавить расписание", callback_data=f"add_rasp_list:{schoolID}:{scholl_class}")
        markup.add(btn)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Расписание не задано", reply_markup=markup)
    else:
        btn = types.InlineKeyboardButton("Изменить расписание", callback_data=f"add_rasp_list:{schoolID}:{scholl_class}:{v}:1")
        markup.add(btn)
        info = "Расписание:\n"
        i = 0
        for i in range(0,10):
            if rasp[i+3] is not None:
                info+=str(i+1) + ". " + rasp[i+3] + "\n"
            i+=1
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
def add_rasp_list(message, schoolID, school_class):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"rasp:{schoolID}:{school_class}:2")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Понедельник", callback_data=f"add_dz:{schoolID}:{school_class}:0:1")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Вторник", callback_data=f"add_dz:{schoolID}:{school_class}:1:1")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Среда", callback_data=f"add_dz:{schoolID}:{school_class}:2:1")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Четверг", callback_data=f"add_dz:{schoolID}:{school_class}:3:1")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Пятница", callback_data=f"add_dz:{schoolID}:{school_class}:4:1")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Суббота", callback_data=f"add_dz:{schoolID}:{school_class}:5:1")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Воскресение", callback_data=f"add_dz:{schoolID}:{school_class}:6:1")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="На какой день недели вы хотите ввести рассписание", reply_markup=markup)
def add_dz(message, schoolID, school_class, day = None, number = None, subject = None):
    subjects = {'Алгебра', 'Астрономия', 'Белорусская лит.', 'Белорусский язык', 'Биология', 'Всемирная истроия', 'География', 'Геометрия', 'Допризыв. под.', 'Иностранный язык', 'Информатика', 'Искусство', 'История Беларуси', 'История России', 'Математика', 'Мед. подготовка', 'Обществоведение', 'Русская лит.', 'Русский язык', 'Труды', 'Физ.культ./ЧЗС', 'Физика', 'Химия', 'Человек и мир', 'Черчение', 'Гультрест (ничего)'}
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Закончить", callback_data=f"rasp:{schoolID}:{school_class}:2")
    markup.add(btn)
    subjects = sorted(subjects)
    if subject is None:
        for el in subjects:
            btn = types.InlineKeyboardButton(el, callback_data=f"add_dz:{schoolID}:{school_class}:{day}:{number}:{el}")
            markup.add(btn)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"Выбери {number} урок", reply_markup=markup)
        return
    conn = sql.connect(f"./sqls/{schoolID}.sql")
    cur = conn.cursor()
    if int(number) == 1:
        cur.execute('DELETE FROM rasp WHERE class = ? AND day = ?', (school_class, day))
    cur.execute('SELECT * FROM rasp WHERE class = ? AND day = ?', (school_class, day))
    temp = cur.fetchone()
    if temp is None:
        cur.execute('INSERT INTO rasp (class, day, lesson1) VALUES (?, ?, ?)', (school_class, day, subject))
    else:
        cur.execute(f'UPDATE rasp SET lesson{number} = ? WHERE class = ? AND day = ?', (subject, school_class, day))
    conn.commit()
    cur.close()
    conn.close()
    if int(number) >= 10:
        rasp(message, schoolID, school_class, 2)
        return
    for el in subjects:
        btn = types.InlineKeyboardButton(el, callback_data=f"add_dz:{schoolID}:{school_class}:{day}:{int(number)+1}:{el}")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"Выбери {int(number)+1} урок", reply_markup=markup)
def see_news(message, schoolID, school_class):
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM news WHERE class = ?', (school_class,))
    news = cur.fetchall()
    cur.close()
    conn.close()
    info = "Новости:\n"
    for el in news:
        info+=el[1]+"\n"+el[2]+"\n\n"
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="school_infoo")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
def see_dz(message, schoolID, school_class, id):
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM dz WHERE class = ?',(school_class,))
    dzs = cur.fetchall()
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data='school_infoo')
    markup.add(btn)
    temp_array = []
    for el in dzs:
        temp_array.append(el[1])
    temp_set = list(set(temp_array))
    for el in temp_set:
        btn = types.InlineKeyboardButton(el, callback_data=f'see_dz_step_1:{schoolID}:{school_class}:{el}')
        markup.add(btn)
    btn = types.InlineKeyboardButton("Добавить дз", callback_data=f"add_homeTask:{schoolID}:{school_class}")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Удалить дз", callback_data=f"rem_homeTask:{schoolID}:{school_class}")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Спросить дз", callback_data=f'ask_dz:{schoolID}:{school_class}')
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери день",reply_markup=markup)
def see_dz_step_1(message, schoolID, school_class, date):
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM dz WHERE class = ? AND date = ?',(school_class, date))
    dzs = cur.fetchall()
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f'homeTask:{schoolID}:{school_class}:0')
    markup.add(btn)
    btn = types.InlineKeyboardButton("Спросить дз", callback_data=f"ask_dz_s1:{date}:{schoolID}:{school_class}")
    markup.add(btn)
    info = f"Дз на {date}\n\n"
    for el in dzs:
        info += f"<b>{el[2]}:</b> {el[3]}\n"
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup, parse_mode='HTML')
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('ask_dz:'))
def ask_dz(call):
    message, schoolID, schoolClass = call.data.split(":")
    message = call.message
    today = datetime.today().date()
    todaySPL = str(today).split('-')
    i = 0
    d = int(todaySPL[2])
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"homeTask:{schoolID}:{schoolClass}:0")
    markup.add(btn)
    for i in range(0, 10):
        btn = types.InlineKeyboardButton(f'{d}.{todaySPL[1]}.{todaySPL[0]}',callback_data=f"ask_dz_s1:{d}.{todaySPL[1]}.{todaySPL[0]}:{schoolID}:{schoolClass}")
        markup.add(btn)
        d += 1
        if d >= 32:
            d = 1
            todaySPL[1] = int(todaySPL[1])+1
            if todaySPL[1]>=13:
                todaySPL[1]=1
                todaySPL[0] = int(todaySPL[0]+1)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,text="Выбери дату (Обратите внимание на 31 число, его может не быть в месяце)",reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('ask_dz_s1:'))
def ask_dz_step_1(call):
    message, Odate, schoolID, my_class = call.data.split(":")
    date = datetime.strptime(Odate, '%d.%m.%Y')
    weekday = date.weekday()
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM rasp WHERE day = ? AND class = ?', (weekday, my_class))
    rasp = cur.fetchone()
    if rasp is None:
        bot.send_message(call.message.chat.id, "Расписание не задано")
        return
    cur.execute('SELECT predmet FROM dz WHERE date = ? AND class = ?', (Odate, my_class))
    dzs = cur.fetchall()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"homeTask:{schoolID}:{my_class}:0")
    markup.add(btn)
    i = 0
    for i in range(0,10):
        i += 1
        if rasp[i+2] is not None:
            b = True
            for el in dzs:
                if el[0] == rasp[i+2]:
                    b = False
            if b:
                btn = types.InlineKeyboardButton(rasp[i+2], callback_data=f"ask_dz_s2:{Odate}:{rasp[i+2]}:{schoolID}:{my_class}")
                markup.add(btn)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбери предмет\n\nЕсли нужного предмета нету, значит дз на него уже задано или его нет в расписании на это число", reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('ask_dz_s2:'))
def ask_dz_step_2(call):
    message, Odate, sub, schoolID, schoolClass = call.data.split(":")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Добавить награду", callback_data=f"ask_dz_s2_r:{Odate}:{sub}:{schoolID}:{schoolClass}"))
    markup.add(types.InlineKeyboardButton("Без награды", callback_data=f"ask_dz_s3:{Odate}:{sub}:{schoolID}:{schoolClass}:N"))
    bot.send_message(call.message.chat.id, "Чтобы вам ответили быстрее вы можете установить награду тому, кто вам ответит", reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('ask_dz_s2_r:'))
def ask_dz_step_2_r(call):
    message, Odate, sub, schoolID, schoolClass = call.data.split(":")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Без награды", callback_data=f"ask_dz_s3:{Odate}:{sub}:{schoolID}:{schoolClass}:N"))
    bot_message_id = bot.send_message(call.message.chat.id, "Введите количество монет которое вы дадите тому кто ответит на ваш вопрос", reply_markup=markup).message_id
    bot.register_next_step_handler(call.message, ask_dz_step_2_r_s2, Odate, sub, schoolID, schoolClass, bot_message_id)
def ask_dz_step_2_r_s2(message, Odate, sub, schoolID, schoolClass, bot_message_id):
    bot.delete_message(message.chat.id, message.message_id)
    try:
        reward = int(message.text)
    except ValueError:
        bot.edit_message_text("Вы ввели не число, попробуйте еще раз", message.chat.id, bot_message_id)
        bot.register_next_step_handler(message, ask_dz_step_2_r_s2, Odate, sub, schoolID, schoolClass, bot_message_id)
        return
    coins = SQL_one_command("SELECT coins From users WHERE chatID = ?", (message.chat.id,), fetchMode="one").data[0]
    if coins < reward:
        bot.edit_message_text('У вас недостаточно монет, введите число заново или нажмите "Без награды"', message.chat.id, bot_message_id)
        bot.register_next_step_handler(message, ask_dz_step_2_r_s2, Odate, sub, schoolID, schoolClass, bot_message_id)
        return
    markup = types.InlineKeyboardMarkup()
    btn0 = types.InlineKeyboardButton("Да", callback_data=f"ask_dz_s3:{Odate}:{sub}:{schoolID}:{schoolClass}:{reward}")
    markup.add(btn0)
    bot.edit_message_text(f"Вы уверены что хотите подарить {reward} монет тому кто ответит на вопрос?", message.chat.id, bot_message_id, reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('ask_dz_s3:'))
def ask_dz_step_3(call):
    message, Odate, sub, schoolID, schoolClass, reward = call.data.split(":")
    message = call.message
    bot.send_message(message.chat.id, "Если кто-то из твоих одноклассников ответит, то я тебе сообщу")
    conn =sql_conn()
    cur = conn.cursor()
    cur.execute("SELECT chatID FROM users WHERE schoolID = ? AND class = ? AND chatID <> ?", (int(schoolID), schoolClass, message.chat.id))
    users = cur.fetchall()
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Ответить", callback_data=f"repli_dz:{Odate}:{sub}:{message.chat.id}:{reward}")
    markup.add(btn)
    text = f"Твой одноклассник попросил скинуть ДЗ по предмету {sub} на {Odate}"
    if reward != "N":
        text += f"\n\nЗа это вы получите {reward} монет"
        print(reward, message.chat.id)
        SQL_one_command("UPDATE users SET coins = coins - ? WHERE chatID = ?", (reward, message.chat.id), commit=True)
    for el in users:
        bot.send_message(el[0], text, reply_markup=markup)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('repli_dz:'))
def reply_for_homeTask_ask(call):
    message, Odate, subject, id, reward = call.data.split(":")
    id = int(id)
    message = call.message
    tempData["usersData"][str(message.chat.id)]["tempDate"], tempData["usersData"][str(message.chat.id)]["tempSubject"] = Odate, subject
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="school_infoo")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,text=f"Впиши дз по {subject} на {Odate}", reply_markup=markup)
    try:
        reward = int(reward)
    except ValueError:
        reward = 0
    bot.register_next_step_handler(message, reply_for_homeTask_handler, id, reward)
def reply_for_homeTask_handler(message, id, reward):
    add_homeTask_step_3(message, "askDZ", id, reward)
def add_homeTask(message, schoolID, school_class):
    today = datetime.today().date()
    todaySPL = str(today).split('-')
    i = 0
    d = int(todaySPL[2])
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"homeTask:{schoolID}:{school_class}:0")
    markup.add(btn)
    for i in range(0, 10):
        btn = types.InlineKeyboardButton(f'{d}.{todaySPL[1]}.{todaySPL[0]}', callback_data=f"add_homeTask_step_1:{d}.{todaySPL[1]}.{todaySPL[0]}")
        markup.add(btn)
        d += 1
        if d >= 32:
            d = 1
            todaySPL[1] = int(todaySPL[1]) + 1
            if todaySPL[1] >= 13:
                todaySPL[1] = 1
                todaySPL[0] = int(todaySPL[0] + 1)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери дату (Обратите внимание на 31 число, его может не быть в месяце)", reply_markup=markup)
def add_homeTask_step_1(message):
    global tempData
    ttempData = tempData["usersData"][str(message.chat.id)]["tempDate"]
    date = datetime.strptime(ttempData, '%d.%m.%Y')
    weekday = date.weekday()
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT schoolID FROM users WHERE chatID = ?', (message.chat.id,))
    schoolID = cur.fetchone()
    cur.execute('SELECT class FROM users WHERE chatID = ?', (message.chat.id,))
    my_class = cur.fetchone()
    cur.close()
    conn.close()
    conn = sql.connect(f'./sqls/{schoolID[0]}.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM rasp WHERE day = ? AND class = ?', (weekday, my_class[0]))
    rasp = cur.fetchone()
    if rasp is None:
        bot.send_message(message.chat.id, "Расписание не задано")
        return
    cur.execute('SELECT predmet FROM dz WHERE date = ? AND class = ?', (ttempData, my_class[0]))
    dzs = cur.fetchall()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"homeTask:{schoolID[0]}:{my_class[0]}:0")
    markup.add(btn)
    i = 0
    for i in range(0,10):
        i += 1
        if rasp[i+2] is not None:
            b = True
            for el in dzs:
                if el[0] == rasp[i+2]:
                    b = False
            if b:
                btn = types.InlineKeyboardButton(rasp[i+2], callback_data=f"add_homeTask_step_2:{ttempData}:{rasp[i+2]}")
                markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери предмет\n\nЕсли нужного предмета нету, значит дз на него уже задано или его нет в расписании на это число", reply_markup=markup)

def add_homeTask_step_2(message, date, subject):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="school_infoo")
    markup.add(btn)
    tempData["usersData"][str(message.chat.id)]["tempSubject"] = subject
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"Впиши дз по {subject} на {date}", reply_markup=markup)
    bot.register_next_step_handler(message, add_homeTask_step_3)
def add_homeTask_step_3(message, dzType = "common", asker = None, reward = 0):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT schoolID FROM users WHERE chatID = ?', (message.chat.id,))
    t = cur.fetchone()
    schoolID = t[0]
    cur.execute('SELECT class FROM users WHERE chatID = ?', (message.chat.id,))
    t = cur.fetchone()
    my_class = t[0]
    cur.execute('SELECT chatID FROM users WHERE schoolID = ? AND class = ?', (schoolID, my_class))
    students = cur.fetchall()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, "Дз добавлено")
    school_info(message)
    add_dz_id = 0
    if my_class not in data["schoolsData"][str(schoolID)]:
        data["schoolsData"][str(schoolID)][my_class]={}
    if "add_dz" not in data["schoolsData"][str(schoolID)][my_class]:
        data["schoolsData"][str(schoolID)][my_class]["add_dz"] = {}
    if data["schoolsData"][str(schoolID)][my_class]["add_dz"] == {}:
        add_dz_id = 0
    else:
        add_dz_id = int(max(data["schoolsData"][str(schoolID)][my_class]["add_dz"])) + 1
    data["schoolsData"][str(schoolID)][my_class]["add_dz"][str(add_dz_id)] = {
        "date": tempData["usersData"][str(message.chat.id)]["tempDate"],
        "subject": tempData["usersData"][str(message.chat.id)]["tempSubject"],
        "dz": message.text,
        "writer": message.chat.id,
        "rating": 1,
        "answers":[message.chat.id],
        "type": dzType
    }
    if dzType == "askDZ":
        data["schoolsData"][str(schoolID)][my_class]["add_dz"][str(add_dz_id)]["asker"] = asker
        data["schoolsData"][str(schoolID)][my_class]["add_dz"][str(add_dz_id)]["reward"] = reward
    save_data()
    if len(students) <= 4:
        add_homeTask_step_4(schoolID, my_class, add_dz_id)
        return
    markup = types.InlineKeyboardMarkup()
    btn0 = types.InlineKeyboardButton("Да", callback_data=f"add_dz_rait:good:{schoolID}:{my_class}:{add_dz_id}")
    btn1 = types.InlineKeyboardButton("Нет", callback_data=f"add_dz_rait:bad:{schoolID}:{my_class}:{add_dz_id}")
    markup.add(btn0, btn1)
    for el in students:
        el = el[0]
        if el != message.chat.id:
            bot.send_message(el, f'Правильное ли это дз по {tempData["usersData"][str(message.chat.id)]["tempSubject"]} на {tempData["usersData"][str(message.chat.id)]["tempDate"]}:\n\n{message.text}', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('add_dz_rait:'))
def add_homeTask_step_3_rait(call):
    message, status, schoolID, my_class, add_dz_id = call.data.split(":")
    message = call.message
    if add_dz_id not in data["schoolsData"][schoolID][my_class]["add_dz"]:
        bot.send_message(message.chat.id, "Это дз уже добавлено или удалено")
        bot.delete_message(message.chat.id, message.message_id)
        return
    if message.chat.id in data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["answers"]:
        bot.send_message(message.chat.id, "Вы уже ответили")
    data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["answers"].append(message.chat.id)
    bot.send_message(message.chat.id, "Спасибо")
    bot.delete_message(message.chat.id, message.message_id)
    if status == "good": data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["rating"] += 1
    elif status == "bad": data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["rating"] -= 1
    if data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["rating"] not in range(0, 3): add_homeTask_step_4(schoolID, my_class, add_dz_id)
def add_homeTask_step_4(schoolID, my_class, add_dz_id):
    if data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["rating"] < 0:
        conn = sql_conn()
        cur = conn.cursor()
        cur.execute('UPDATE users SET rating = rating - 3 WHERE chatID = ?', (data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["writer"],))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["writer"], f'Добавленное вами дз по предмету {data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["subject"]} на {data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["date"]} помечено как неправильное, за это у вас снимают 2 очка рейтинга')
        del data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]
        save_data()
        return
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('UPDATE users SET rating = rating + 1 WHERE chatID = ?', (data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["writer"],))
    cur.execute('UPDATE users SET coins = coins + 5 WHERE chatID = ?', (data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["writer"],))
    conn.commit()
    cur.close()
    conn.close()
    if data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["type"] == "askDZ":
        SQL_one_command("UPDATE users SET coins = coins + ? WHERE chatID = ?", (data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["reward"], data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["writer"]), commit=True)
        bot.send_message(data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["asker"], "ДЗ которое вы просили добавлено")
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('INSERT INTO dz (date, predmet, dz, class) VALUES (?,?,?,?)', (data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["date"], data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["subject"], data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["dz"], my_class))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["writer"], f'Добавленное вами дз по предмету {data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["subject"]} на {data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["date"]} помечено как правильное, за это вам дают 1 очко рейтинга')
    for el in data["schoolsData"][schoolID][my_class]["add_dz"]:
        if data["schoolsData"][schoolID][my_class]["add_dz"][el]["subject"] == \
                data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["subject"] and \
                data["schoolsData"][schoolID][my_class]["add_dz"][el]["date"] == \
                data["schoolsData"][schoolID][my_class]["add_dz"][add_dz_id]["date"]:
            del data["schoolsData"][schoolID][my_class]["add_dz"][el]
    save_data()
def rem_homeTask(message, schoolID, school_class):
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM dz WHERE class = ?', (school_class,))
    dzs = cur.fetchall()
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"homeTask:{schoolID}:{school_class}:0")
    markup.add(btn)
    temp_array = []
    for el in dzs:
        temp_array.append(el[1])
    temp_set = list(set(temp_array))
    for el in temp_set:
        btn = types.InlineKeyboardButton(el, callback_data=f'rem_dz_step_1:{schoolID}:{school_class}:{el}')
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери день",reply_markup=markup)

def rem_dz_step_1(message, schoolID, school_class, date):
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM dz WHERE class = ? AND date = ?', (school_class, date))
    dzs = cur.fetchall()
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"homeTask:{schoolID}:{school_class}:0")
    markup.add(btn)
    temp_array = []
    for el in dzs:
        temp_array.append(el[2])
    temp_set = list(set(temp_array))
    for el in temp_set:
        btn = types.InlineKeyboardButton(el, callback_data=f'rem_dz_step_2:{schoolID}:{school_class}:{date}:{el}')
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери предмет и дз по нему сразу удалится",reply_markup=markup)
def rem_dz_step_2(message, schoolID, school_class, date, subject):
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('DELETE FROM dz WHERE class = ? AND predmet = ? AND date = ?', (school_class, subject, date))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, "Дз успешно удалено")
    see_dz(message, schoolID, school_class, 0)
def create_new_scholl_db(schoolID):
    bot.send_message(config.ADMIN_ID, f"Создана новая школа с ID: {schoolID}")
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS rasp (id int auto_increment primary key, class varchar(6), day int, lesson1 varchar(25), lesson2 varchar(25), lesson3 varchar(25), lesson4 varchar(25), lesson5 varchar(25), lesson6 varchar(25), lesson7 varchar(25), lesson8 varchar(25), lesson9 varchar(25), lesson10 varchar(25))')
    cur.execute('CREATE TABLE IF NOT EXISTS news (id int auto_increment primary key, date varchar(50), news varchar(5000), NewsId int, class varchar(6))')
    cur.execute('CREATE TABLE IF NOT EXISTS dz (id int auto_increment primary key, date varchar(50), predmet varchar(25), dz varchar(1000), dzId int, class varchar(25))')
    conn.commit()
    cur.close()
    conn.close()
    data["schoolsData"][str(schoolID)] = {}
    save_data()

def kretoffSchool(message):
    markup = types.InlineKeyboardMarkup()
    bot.send_message(message.chat.id, "В разработке", reply_markup=markup)

def kretoff_gpt(message):
    bot.send_message(message.chat.id, "Привет я kretofferGPT, могу помочь тебе с разного рода задачами.\nМой хозяин мне не платит, по этому платить мне будешь ты🫵\n"
                     "\n<b>micro</b> - очень легкие вопросы с очень кратким ответом\n"
                     "<b>mini</b> - более продвинутая версия\n"
                     "<b>lite</b> - версия которая может помочь с более сложными задачами\n"
                     "<b>standart</b> - стандартная версия которая подойдет для простеньких вопросов с объяснением <i>рекомендуется</i>\n"
                     "<b>bigModel</b> - подходит для развернутых ответов на сложные вопросы, написания текстов\n"
                     "<b>kretofferGPT pro</b> - супер умная версия бота которая может сделать что угодно (краткий ответ)\n"
                     "<b>kretofferGPT pro+</b> - развернутый ответ", reply_markup=kretofferGPT_variants_markup, parse_mode="HTML")
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('GPT_v:'))
def gpt_v(call):
    version = call.data.split(":")[1]

    versionsPrice = {"micro": 10, "mini": 20, "lite": 45, "standart": 100, "bigModel": 200}
    versionsProPrice = {"kretofferGPT_pro": 500, "kretofferGPT_pro_p": 1000}

    if version in versionsPrice:
        price = versionsPrice[version]
    elif version in versionsProPrice:
        price = versionsProPrice[version]
    userCoins = SQL_one_command("SELECT coins FROM users WHERE chatID = ?", (call.message.chat.id,), fetchMode="one").data[0]
    if userCoins < price:
        bot.send_message(call.message.chat.id, "Недостаточно монет")
        return
    bot.send_message(call.message.chat.id, "Напишите вопрос")
    bot.register_next_step_handler(call.message, ask_gpt_question, version, price)
def ask_gpt_question(message, version = "micro", price = 50):
    SQL_one_command("UPDATE users SET coins = coins - ? WHERE chatID = ?", (price, message.chat.id), commit=True)

    versions = {"micro": 50, "mini": 150, "lite": 250, "standart": 500, "bigModel": 1000}
    versionsPro = {"kretofferGPT_pro": 500, "kretofferGPT_pro_p": 1000}

    if version in versions:
        answer = ask_question(message.text, versions[version], "GigaChat")
    elif version in versionsPro:
        answer = ask_question(message.text, versionsPro[version], "GigaChat-Pro")
    bot.send_message(message.chat.id, answer, parse_mode="HTML")
@bot.message_handler()
def main(message):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE chatID = "%s"' % (message.chat.id))
    info = cur.fetchone()
    cur.close()
    conn.close()
    if info is None or info[6] == 0:
        bot.send_message(message.chat.id, "Что-то пошло не так, похоже вы не зарегестрировались, пропишите /start")
        return
    if message.text == "Личный кабинет 🪪":
        my_room(message)
    elif message.text == "Настройки ⚙️":
        bot.send_message(message.chat.id, "Настройки", reply_markup=settings_markup)
    elif message.text == "Обучение 📖":
        go_education(message)
    elif message.text == "Школа 🏫":
        school_info(message)
    elif message.text == "Другое":
        bot_message = bot.send_message(message.chat.id, "Вот меню", reply_markup=other_markup)
    elif message.text == "Школа kretoffer'a 💻":
        kretoffSchool(message)
    elif message.text == "Магазин 🛍️":
        openShop(message)
    elif message.text == "kretofferGPT 🤖":
        kretoff_gpt(message)
    elif message.text == "⬅️ Назад":
        bot_message = bot.send_message(message.chat.id, "Вы дома 🏠", reply_markup=my_markup())
    elif message.text.lower() == "але":
        bot.send_message(message.chat.id, "Абонент временно не доступен перезвоните позже")
    else:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Подписаться", url="https://t.me/kretoffer_school_chanel")
        markup.add(btn)
        if message.text.lower() in ["ты лох", "ты дурак", "ты ужасен", "ты худший", "ты дебил", "ты пидарас"]:
            bot.send_message(message.chat.id, f"Сам {message.text.lower()}! 😤")
            if bot.get_chat_member(config.CHANEL_ID, message.chat.id).status not in ["member", "administrator", "creator"]:
                bot.send_message(message.chat.id, "Вы еще не подписаны на наш канал, там вы можете найти что-то интересное", reply_markup=markup)
            return
        bot.send_message(message.chat.id, "Я вас не понимаю")
        if bot.get_chat_member(config.CHANEL_ID, message.chat.id).status not in ["member", "administrator", "creator"]:
            bot.send_message(message.chat.id, "Вы еще не подписаны на наш канал, там вы можете найти что-то интересное",reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data == "about_bot")
def about_bot(call):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Последнее обновление", callback_data="bot_update")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Справочник", callback_data="handbook")
    #markup.add(btn)
    usersCol = SQL_one_command("SELECT count(*) FROM users WHERE autorizationStep != 0", fetchMode="one").data[0]
    schoolsCol = SQL_one_command("SELECT count(*) FROM schools", fetchMode="one").data[0]
    usersInfo = f"\nВсего зарегестрировано {usersCol} пользователей из {schoolsCol} школ"
    bot.send_message(call.message.chat.id, config.bot_info + usersInfo, reply_markup=markup, parse_mode="HTML")
@bot.callback_query_handler(func=lambda callback: callback.data == "handbook")
def about_bot(call):
    markup = types.InlineKeyboardMarkup()
    bot.send_message(call.message.chat.id, config.bot_info, reply_markup=markup, parse_mode="HTML")
@bot.callback_query_handler(func=lambda callback: callback.data == "bot_update")
def about_bot(call):
    bot.send_message(call.message.chat.id, config.last_update_info, parse_mode="HTML")
@bot.callback_query_handler(func=lambda callback: callback.data.startswith("report_btn"))
def report(call):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute("SELECT report from timeOuts WHERE chatID = ?", (call.message.chat.id,))
    t = cur.fetchone()[0]
    cur.close()
    conn.close()
    if t > datetime.now().timestamp():
        if t > datetime.now().timestamp()+43200:
            bot.send_message(call.message.chat.id, "Вам временно запрещено отправлять репорты")
            return
        bot.send_message(call.message.chat.id, "Репорты можно отправлять один раз в 12 часов или чаще если репорт окажется полезным")
        return
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, 'Сейчас вы можете написать предложение или сообщить о баге, если вы не хотите этого делать напишите "Отмена". Если он окажется полезным, то вы получите 2 алмаза и 5 очков рейтинга', reply_markup=cancel_markup)
    bot.register_next_step_handler(call.message, report_send)
def report_send(message):
    if message.text.lower() == "отмена":
        bot.send_message(message.chat.id, "Репорт не отправлен", reply_markup=my_markup())
        return
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute("UPDATE timeOuts SET report = ? WHERE chatID = ?", (datetime.now().timestamp()+43200, message.chat.id))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(config.ADMIN_ID, f"Пользователь @{message.from_user.username} отправил репорт", reply_markup=report_repli_markup(message.chat.id))
    bot.forward_message(config.ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "Репорт отправлен, если что, то с вами свяжется администрация. Если же сообщение окажется спамом, то вам заблокируют отправку репортов на 2 недели. Репорты можно отправлять 1 раз в час", reply_markup=my_markup())

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('good_report:'))
def good_report_btn(call):
    message, userIdStr = call.data.split(":")
    message = call.message
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute("UPDATE timeOuts SET report = ? WHERE chatID = ?",(datetime.now().timestamp(), int(userIdStr)))
    cur.execute("UPDATE users SET diamonds = diamonds + 2 WHERE chatID = ?", (int(userIdStr),))
    cur.execute("UPDATE users SET rating = rating + 5 WHERE chatID = ?", (int(userIdStr),))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, "Репорт отменчен как полезный")
    bot.send_message(int(userIdStr), "Ваш репорт отмечен как полезный и вы можете написать новый")
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('bad_report:'))
def bad_report_btn(call):
    message, userIdStr = call.data.split(":")
    message = call.message
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute("UPDATE timeOuts SET report = ? WHERE chatID = ?",(datetime.now().timestamp()+1209600, int(userIdStr)))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, "Репорт отменчен как спам")
    bot.send_message(int(userIdStr), "Ваш репорт отмечен как спам и вы не сможете писать новые в течении 2 недель")
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('reply_report:'))
def reply_report_btn(call):
    message, userIdStr = call.data.split(":")
    message = call.message
    bot.send_message(message.chat.id, "Напишите ответ")
    bot.register_next_step_handler(message, reply_report, int(userIdStr))
def reply_report(message, userID):
    bot.send_message(userID, f"Администратор {message.from_user.username} ответил на ваш репорт\n\n<b>Ответ:</b>\n{message.text}", parse_mode='HTML')
    bot.send_message(message.chat.id, "Ответ отправлен", reply_markup=my_markup())
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global data
    callRazd = call.data.split(':')
    if callRazd[0] == "first_register_step":
        data["usersData"][str(call.message.chat.id)]["contry"] = callRazd[1]
        save_data()
        send_vibor_obl(call)
    elif callRazd[0] == "second_register_step":
        data["usersData"][str(call.message.chat.id)]["obl"] = callRazd[1]
        save_data()
        send_vibor_sity(call.message)
    elif callRazd[0] == "second_register_step_else":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        tempData["usersData"][str(call.message.chat.id)]["MessageID"] = bot.send_message(call.message.chat.id, "Введите название области").message_id
        save_data()
        bot.register_next_step_handler(call.message, else_obl)
    elif callRazd[0] == "serd_register_step":
        data["usersData"][str(call.message.chat.id)]["sity"] = callRazd[1]
        save_data()
        send_vibor_school(call.message)
    elif callRazd[0] == "serd_register_step_else":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        tempData["usersData"][str(call.message.chat.id)]["MessageID"] = bot.send_message(call.message.chat.id, "Введите название города").message_id
        save_data()
        bot.register_next_step_handler(call.message, else_sity)
    elif callRazd[0] == "fourth_register_step":
        conn = sql_conn()
        cur = conn.cursor()
        cur.execute("SELECT schoolID FROM schools WHERE school = ?",(callRazd[1],))
        school = cur.fetchone()
        cur.execute('UPDATE users SET schoolID = ? WHERE chatID = ?', (school[0], call.message.chat.id))
        cur.execute('UPDATE users SET autorizationStep = ? WHERE chatID = ?', (1, call.message.chat.id))
        cur.execute('INSERT INTO timeOuts (chatID, report, selectClass, selectSchool) VALUES ("%s", "%s", "%s", "%s")' % (call.message.chat.id, 0, 0, 0))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(call.message.chat.id, "Вы успешно зарегистрированы")
        Go_start(call.message)
    elif callRazd[0] == "fourth_register_step_else":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        tempData["usersData"][str(call.message.chat.id)]["MessageID"] = bot.send_message(call.message.chat.id, "Введите название/номер школы").message_id
        save_data()
        bot.register_next_step_handler(call.message, else_school)
    elif callRazd[0] == "school_info":
        conn = sql_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM schools WHERE schoolID = ?", (int(callRazd[1]),))
        info = cur.fetchone()
        if info is None:
            return
        cur.close()
        conn.close()
        infoText = f'ID: {info[1]}\n\nСтрана: {info[2]}\nОбласть: {info[3]}\nГород/деревня: {info[4]}\nШкола: {info[5]}\nРейтинг: {info[6]}'
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Назад", callback_data="back_to_my_room")
        markup.add(btn)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=infoText, reply_markup=markup)
    elif callRazd[0] == "back_to_my_room":
        conn = sql_conn()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE chatID = "%s"' % (call.message.chat.id))
        info = cur.fetchone()
        cur.close()
        conn.close()
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Школа", callback_data=f"school_info:{info[5]}")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Пригласить друга", callback_data="invite_frend")
        markup.add(btn)
        infoText = f"ID: {info[3]}\n\nИмя: {info[1]}\nФамилия: {info[2]}\n\nКласс: {info[13]}\n\nОпыт: {info[8]}\nУровень: {info[9]}\nМонеты: {info[10]}\nАлмазы: {info[11]}\nБилеты: {info[12]}\n\nПриглашено друзей: {data['usersData'][str(call.message.chat.id)]['invitedCol']}"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=infoText, reply_markup=markup)
    elif callRazd[0] == "class_vibor":
        conn = sql_conn()
        cur = conn.cursor()
        cur.execute('SELECT selectClass FROM timeOuts WHERE chatID = ?', (call.message.chat.id,))
        timeOut = int(cur.fetchone()[0])
        cur.close()
        conn.close()
        if timeOut+2592000 > datetime.now().timestamp() and call.message.chat.id != config.ADMIN_ID:
            bot.send_message(call.message.chat.id, f"Вы сможете изменить класс только через {int((timeOut+2592000-datetime.now().timestamp())/86400)} дней")
            return
        markup = types.InlineKeyboardMarkup()
        i = 0
        for i in range(0,11):
            i+=1
            btn = types.InlineKeyboardButton(str(i), callback_data=f"set_class:{i}")
            markup.add(btn)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбери класс",reply_markup=markup)
    elif callRazd[0] == "set_class":
        conn = sql_conn()
        cur = conn.cursor()
        cur.execute('UPDATE users SET class = ? WHERE chatID = ?', (callRazd[1], call.message.chat.id))
        conn.commit()
        cur.close()
        conn.close()
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('"А"', callback_data="set_class_letter:А")
        btn2 = types.InlineKeyboardButton('"Б"', callback_data="set_class_letter:Б")
        btn3 = types.InlineKeyboardButton('"В"', callback_data="set_class_letter:В")
        markup.add(btn1, btn2, btn3)
        btn1 = types.InlineKeyboardButton('"Г"', callback_data="set_class_letter:Г")
        btn2 = types.InlineKeyboardButton('"Д"', callback_data="set_class_letter:Д")
        btn3 = types.InlineKeyboardButton('"Е"', callback_data="set_class_letter:Е")
        markup.add(btn1, btn2, btn3)
        btn1 = types.InlineKeyboardButton('"Ж"', callback_data="set_class_letter:Ж")
        btn2 = types.InlineKeyboardButton('"З"', callback_data="set_class_letter:З")
        btn3 = types.InlineKeyboardButton('"И"', callback_data="set_class_letter:И")
        markup.add(btn1, btn2, btn3)
        btn1 = types.InlineKeyboardButton('<', callback_data="set_class_l4")
        btn2 = types.InlineKeyboardButton('>', callback_data="set_class_l2")
        markup.add(btn1, btn2)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбери класс", reply_markup=markup)
    elif callRazd[0] == "set_class_l1":
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('"А"', callback_data="set_class_letter:А")
        btn2 = types.InlineKeyboardButton('"Б"', callback_data="set_class_letter:Б")
        btn3 = types.InlineKeyboardButton('"В"', callback_data="set_class_letter:В")
        markup.add(btn1, btn2, btn3)
        btn1 = types.InlineKeyboardButton('"Г"', callback_data="set_class_letter:Г")
        btn2 = types.InlineKeyboardButton('"Д"', callback_data="set_class_letter:Д")
        btn3 = types.InlineKeyboardButton('"Е"', callback_data="set_class_letter:Е")
        markup.add(btn1, btn2, btn3)
        btn1 = types.InlineKeyboardButton('"Ж"', callback_data="set_class_letter:Ж")
        btn2 = types.InlineKeyboardButton('"З"', callback_data="set_class_letter:З")
        btn3 = types.InlineKeyboardButton('"И"', callback_data="set_class_letter:И")
        markup.add(btn1, btn2, btn3)
        btn1 = types.InlineKeyboardButton('<', callback_data="set_class_l4")
        btn2 = types.InlineKeyboardButton('>', callback_data="set_class_l2")
        markup.add(btn1, btn2)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    elif callRazd[0] == "set_class_l2":
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('"Й"', callback_data="set_class_letter:Й")
        btn2 = types.InlineKeyboardButton('"К"', callback_data="set_class_letter:К")
        btn3 = types.InlineKeyboardButton('"Л"', callback_data="set_class_letter:Л")
        markup.add(btn1, btn2, btn3)
        btn1 = types.InlineKeyboardButton('"М"', callback_data="set_class_letter:М")
        btn2 = types.InlineKeyboardButton('"Н"', callback_data="set_class_letter:Н")
        btn3 = types.InlineKeyboardButton('"О"', callback_data="set_class_letter:О")
        markup.add(btn1, btn2, btn3)
        btn1 = types.InlineKeyboardButton('"П"', callback_data="set_class_letter:П")
        btn2 = types.InlineKeyboardButton('"Р"', callback_data="set_class_letter:Р")
        btn3 = types.InlineKeyboardButton('"С"', callback_data="set_class_letter:С")
        markup.add(btn1, btn2, btn3)
        btn1 = types.InlineKeyboardButton('<', callback_data="set_class_l1")
        btn2 = types.InlineKeyboardButton('>', callback_data="set_class_l3")
        markup.add(btn1, btn2)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    elif callRazd[0] == "set_class_l3":
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('"Т"', callback_data="set_class_letter:Т")
        btn2 = types.InlineKeyboardButton('"У"', callback_data="set_class_letter:У")
        btn3 = types.InlineKeyboardButton('"Ф"', callback_data="set_class_letter:Ф")
        markup.add(btn1, btn2, btn3)
        btn1 = types.InlineKeyboardButton('"Х"', callback_data="set_class_letter:Х")
        btn2 = types.InlineKeyboardButton('"Ц"', callback_data="set_class_letter:Ц")
        btn3 = types.InlineKeyboardButton('"Ч"', callback_data="set_class_letter:Ч")
        markup.add(btn1, btn2, btn3)
        btn1 = types.InlineKeyboardButton('"Ш"', callback_data="set_class_letter:Ш")
        btn2 = types.InlineKeyboardButton('"Щ"', callback_data="set_class_letter:Щ")
        btn3 = types.InlineKeyboardButton('"Ъ"', callback_data="set_class_letter:Ъ")
        markup.add(btn1, btn2, btn3)
        btn1 = types.InlineKeyboardButton('<', callback_data="set_class_l2")
        btn2 = types.InlineKeyboardButton('>', callback_data="set_class_l4")
        markup.add(btn1, btn2)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    elif callRazd[0] == "set_class_l4":
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('"Ы"', callback_data="set_class_letter:Ы")
        btn2 = types.InlineKeyboardButton('"Ь"', callback_data="set_class_letter:Ь")
        markup.add(btn1, btn2)
        btn1 = types.InlineKeyboardButton('"Э"', callback_data="set_class_letter:Э")
        btn2 = types.InlineKeyboardButton('"Ю"', callback_data="set_class_letter:Ю")
        btn3 = types.InlineKeyboardButton('"Я"', callback_data="set_class_letter:Я")
        markup.add(btn1, btn2, btn3)
        btn1 = types.InlineKeyboardButton('<', callback_data="set_class_l3")
        btn2 = types.InlineKeyboardButton('>', callback_data="set_class_l1")
        markup.add(btn1, btn2)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    elif callRazd[0] == "set_class_letter":
        conn = sql_conn()
        cur = conn.cursor()
        cur.execute('SELECT class FROM users WHERE chatID = ?', (call.message.chat.id,))
        temp = cur.fetchone()
        cur.execute('UPDATE users SET class = ? WHERE chatID = ?', (f'{temp[0]}"{callRazd[1]}"', call.message.chat.id))
        cur.execute('UPDATE timeOuts SET selectClass = ? WHERE chatID = ?', (datetime.now().timestamp(), call.message.chat.id))
        conn.commit()
        cur.execute('SELECT * FROM users WHERE chatID = "%s"' % (call.message.chat.id))
        info = cur.fetchone()
        cur.close()
        conn.close()
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Школа", callback_data=f"school_info:{info[5]}")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Пригласить друга", callback_data="invite_frend")
        markup.add(btn)
        infoText = f"ID: {info[3]}\n\nИмя: {info[1]}\nФамилия: {info[2]}\n\nКласс: {info[13]}\n\nОпыт: {info[8]}\nУровень: {info[9]}\nМонеты: {info[10]}\nАлмазы: {info[11]}\nБилеты: {info[12]}\n\nПриглашено друзей: {data['usersData'][str(call.message.chat.id)]['invitedCol']}"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=infoText, reply_markup=markup)
    elif callRazd[0] == "invite_frend":
        bot.send_message(call.message.chat.id, f"Если ваш друг перейдет по вашей реферальной ссылке, то вы и ваш друг получите по 10 алмазов\n\nВаша ссылка:\nhttps://t.me/{config.BOT_NICKNAME}?start={call.message.chat.id}\n\nТекущее количество приглашенных людей: {data['usersData'][str(call.message.chat.id)]['invitedCol']}")
    elif callRazd[0] == "rasp":
        rasp(call.message, callRazd[1], callRazd[2], callRazd[3])
    elif callRazd[0] == "news":
        see_news(call.message, callRazd[1], callRazd[2])
    elif callRazd[0] == "homeTask":
        see_dz(call.message, callRazd[1], callRazd[2], callRazd[3])
    elif callRazd[0] == "school_infoo":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        school_info(call.message)
    elif callRazd[0] == "add_rasp_list":
        add_rasp_list(call.message, callRazd[1], callRazd[2])
    elif callRazd[0] == "add_dz":
        if len(callRazd)==4:
            add_dz(call.message, callRazd[1], callRazd[2], callRazd[3])
        elif len(callRazd)==5:
            add_dz(call.message, callRazd[1], callRazd[2], callRazd[3], callRazd[4])
        elif len(callRazd)==6:
            add_dz(call.message, callRazd[1], callRazd[2], callRazd[3], callRazd[4], callRazd[5])
    elif callRazd[0] == "add_homeTask":
        add_homeTask(call.message, callRazd[1], callRazd[2])
    elif callRazd[0] == "rem_homeTask":
        rem_homeTask(call.message, callRazd[1], callRazd[2])
    elif callRazd[0] == "GDZ":
        gdz(call.message)
    elif callRazd[0] == "see_dz_step_1":
        see_dz_step_1(call.message, callRazd[1], callRazd[2], callRazd[3])
    elif callRazd[0] == "new_name":
        bot.send_message(int(callRazd[1]), "Впишите новое имя")
        message = tempData["usersData"][str(callRazd[1])]["tempMessage"]
        bot.register_next_step_handler(message, new_name)
    elif callRazd[0] == "new_last_name":
        bot.send_message(int(callRazd[1]), "Впишите новую фамилию")
        message = tempData["usersData"][str(callRazd[1])]["tempMessage"]
        bot.register_next_step_handler(message, new_last_name)
    elif callRazd[0] == "add_homeTask_step_1":
        tempData["usersData"][str(call.message.chat.id)]["tempDate"] = callRazd[1]
        add_homeTask_step_1(call.message)
    elif callRazd[0] == "add_homeTask_step_2":
        add_homeTask_step_2(call.message, callRazd[1], callRazd[2])
    elif callRazd[0] == "rem_dz_step_1":
        rem_dz_step_1(call.message, callRazd[1], callRazd[2], callRazd[3])
    elif callRazd[0] == "rem_dz_step_2":
        rem_dz_step_2(call.message, callRazd[1], callRazd[2], callRazd[3], callRazd[4])
    elif callRazd[0] == "my_courses":
        my_courses(call.message)
    elif callRazd[0] == "lessons_list":
        lessons_list(call.message)
    elif callRazd[0] == "courses_list":
        courses_list(call.message)
    elif callRazd[0] == "tests_list":
        tests_list(call.message)
    elif callRazd[0] == "cheat_sheets_list":
        cheat_sheets_list(call.message)
    elif callRazd[0] == "completed_courses":
        completed_courses(call.message)
    elif callRazd[0] == "education":
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        go_education(call.message)
    elif callRazd[0] == "course":
        start_course(call.message, callRazd[1])
    elif callRazd[0] == "lesson":
        start_lesson(call.message, callRazd[1], int(callRazd[2]))
    elif callRazd[0] == "test":
        if callRazd[4] == "False": t = False
        elif callRazd[4] == "True": t = True
        start_test(call.message, callRazd[1], int(callRazd[2]), int(callRazd[3]), t)
    elif callRazd[0] == "sen_cheat_sheets_list":
        sen_cheat_sheets_list(call.message, callRazd[1], callRazd[2])
    elif callRazd[0] == "sen_cheat_sheets":
        sen_cheat_sheets(call.message, callRazd[1], callRazd[2], callRazd[3])
    elif callRazd[0] == "go_course_lesson":
        go_course_lesson(call.message, callRazd[1])
    elif callRazd[0] == "completed_lessons_list":
        completed_lessons_list(call.message)
    elif callRazd[0] == "completed_tests_list":
        completed_tests_list(call.message)
    elif callRazd[0] == "course_back":
        data['education'][str(call.message.chat.id)]['my_courses'][callRazd[1]]['completed'] = False
        data['education'][str(call.message.chat.id)]['my_courses'][callRazd[1]]['completed_lessons'] = 0
        save_data()
    elif callRazd[0] == "courses_subject_list":
        courses_subject_list(call.message, callRazd[1], int(callRazd[2]))
def new_name(message):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('UPDATE users SET first_name = ? WHERE chatID = ?', (message.text, message.chat.id))
    conn.commit()
    cur.close()
    conn.close()
    my_room(message)
def new_last_name(message):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('UPDATE users SET last_name = ? WHERE chatID = ?', (message.text, message.chat.id))
    conn.commit()
    cur.close()
    conn.close()
    my_room(message)

def send_vibor_obl(call):
    markup = types.InlineKeyboardMarkup()

    conn = sql_conn()
    cur = conn.cursor()
    temp = data["usersData"][f"{call.message.chat.id}"]["contry"]
    cur.execute('SELECT obl FROM schools WHERE contry = ?', (temp,))
    obls = cur.fetchall()
    cur.close()
    conn.close()
    my_array=[]
    for el in obls:
        if str(el[0]) != "None":
            if el[0] not in my_array:
                my_array.append(str(el[0]))
    for el in my_array:
        btn = types.InlineKeyboardButton(el, callback_data=f"second_register_step:{el}")
        markup.add(btn)
    btn = types.InlineKeyboardButton("Другая", callback_data="second_register_step_else")
    markup.add(btn)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выбери область',reply_markup=markup)

def else_obl(message):
    bot.delete_message(message.chat.id, message.message_id)
    data["usersData"][f"{message.chat.id}"]["obl"] = message.text
    save_data()
    send_vibor_sity(message, tempData["usersData"][str(message.chat.id)]["MessageID"])

def send_vibor_sity(message, messageID = None):
    if messageID is None:
        messageID = message.message_id
    markup = types.InlineKeyboardMarkup()
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT sity FROM schools WHERE contry = ? AND obl = ?', (data["usersData"][f"{message.chat.id}"]["contry"], data["usersData"][f"{message.chat.id}"]["obl"]))
    sitys = cur.fetchall()
    cur.close()
    conn.close()
    my_array = []
    for el in sitys:
        if str(el[0]) != "None":
            if el[0] not in my_array:
                my_array.append(el[0])
    for el in my_array:
        btn = types.InlineKeyboardButton(el, callback_data=f"serd_register_step:{el}")
        markup.add(btn)
    btn = types.InlineKeyboardButton("Друой", callback_data="serd_register_step_else")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id,message_id=messageID, text='Выбери город',reply_markup=markup)

def else_sity(message):
    bot.delete_message(message.chat.id, message.message_id)
    data["usersData"][f"{message.chat.id}"]["sity"] = message.text
    save_data()
    send_vibor_school(message, tempData["usersData"][str(message.chat.id)]["MessageID"])

def send_vibor_school(message, messageID = None):
    if messageID is None:
        messageID = message.message_id
    markup = types.InlineKeyboardMarkup()
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT school FROM schools WHERE contry = ? AND obl = ? AND sity = ?',
                (data["usersData"][f"{message.chat.id}"]["contry"], data["usersData"][f"{message.chat.id}"]["obl"], data["usersData"][f"{message.chat.id}"]["sity"]))
    schools = cur.fetchall()
    cur.close()
    conn.close()
    my_array = []
    for el in schools:
        if str(el[0]) != "None":
            if el[0] not in my_array:
                my_array.append(el[0])
    for el in my_array:
        btn = types.InlineKeyboardButton(el, callback_data=f"fourth_register_step:{el}")
        markup.add(btn)
    btn = types.InlineKeyboardButton("Другая", callback_data="fourth_register_step_else")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=messageID, text='Выбери школу',reply_markup=markup)

def else_school(message):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT school FROM schools')
    schols = cur.fetchall()
    cur.execute('INSERT INTO schools (contry, obl, sity, school, schoolID, rating) VALUES ("%s", "%s", "%s", "%s", "%s", "%s")' % (
    data["usersData"][f"{message.chat.id}"]["contry"], data["usersData"][f"{message.chat.id}"]["obl"], data["usersData"][f"{message.chat.id}"]["sity"], message.text, len(schols),0))
    cur.execute(f'UPDATE users SET schoolID = {len(schols)} WHERE chatID = {message.chat.id}')
    cur.execute(f'UPDATE users SET autorizationStep = {1} WHERE chatID = {message.chat.id}')
    cur.execute('INSERT INTO timeOuts (chatID, report, selectClass, selectSchool) VALUES ("%s", "%s", "%s", "%s")' % (message.chat.id, 0, 0, 0))
    conn.commit()
    cur.close()
    conn.close()
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, tempData["usersData"][str(message.chat.id)]["MessageID"])
    bot.send_message(message.chat.id,"Вы успешно зарегистрированы, для начала работы с ботом пропишите /start")
    create_new_scholl_db(len(schols))
    Go_start(message)

def run_bot():
    print("бот запущен...")
    delOldDz()
    #delTempSchools()
    #bot.send_message(config.ADMIN_ID, "Бот запущен")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    run_bot()