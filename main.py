import telebot
from telebot import types
import sqlite3 as sql
import datetime
from datetime import *
import time
import random
import requests
import os
import json

testBot = telebot.TeleBot('6764297608:AAEx5Eqbvh5BMTTbAMV0FVRM5B7tqObZYmU')
realBot = telebot.TeleBot("6468345657:AAFY4m6lYkktI8ZecWW-5EfChyT0aOHWWW8")
bot = testBot

conn = sql.connect('db.sql')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, first_name varchar(50), last_name varchar(50), chatID int, bagsTimeOut float, schoolID int, autorizationStep int, teacher bit, experience int, level int, coins int, diamonds int, tickets int, class var(6))')
cur.execute('CREATE TABLE IF NOT EXISTS schools(id int auto_increment primary key, schoolID int, contry varchar(20), obl varchar(50), sity varchar(50), school varchar(50), rating int)')
cur.execute('CREATE TABLE IF NOT EXISTS bags (id int auto_increment primary key, date varchar(50), user varchar(100), bag varchar(5000), bagId int)')
cur.execute('CREATE TABLE IF NOT EXISTS admins (id int auto_increment primary key, name varchar(50), chatID int)')
cur.execute('CREATE TABLE IF NOT EXISTS news (id int auto_increment primary key, date varchar(50), news varchar(5000), NewsId int)')
#cur.execute('INSERT INTO schools (contry) VALUES ("%s")' % ("Беларусь"))
#cur.execute('INSERT INTO schools (contry) VALUES ("%s")' % ("Россия"))

BOT_NICKNAME = "K_gymnasium_7a_bot"

conn.commit()
cur.close()
conn.close()
data = {
    "usersData":{

    },
    "education":{

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
def my_markup():
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton("Личный кабинет 🪪")
    btn2 = types.KeyboardButton("Настройки ⚙️")
    markup.row(btn1, btn2)
    btn = types.KeyboardButton("Обучение 📖")
    markup.add(btn)
    return markup
@bot.message_handler(commands=['allMessage'])
def main(message):
  if (message.chat.id != 1917247858):
    bot.send_message(message.chat.id, "Вам не доступна эта команда")
    return
  markup = types.ReplyKeyboardMarkup(row_width=1)
  btn = types.KeyboardButton("Отмена")
  markup.add(btn)
  bot.send_message(message.chat.id,'Введите сообщение которое отправится всем пользователям бота, для отмены напишите "отмена"', reply_markup=markup)
  bot.register_next_step_handler(message, allMesage)

def allMesage(message):
  if message.text.strip().lower() == "отмена":
    bot.send_message(message.chat.id, "отмена прошла успешно")
    return
  conn = sql.connect('db.sql')
  cur = conn.cursor()

  cur.execute('SELECT * FROM users')
  users = cur.fetchall()

  cur.close()
  conn.close()

  for el in users:
    bot.send_message(el[3], f'Рассылка:\n{message.text}', reply_markup=my_markup())
@bot.message_handler(commands=['start'])
def main(message):
    i = False
    for users in data["usersData"]:
        if users == message.chat.id:
            i = True
    if i == False:
        data["usersData"][str(message.chat.id)] = {}
        data["usersData"][str(message.chat.id)]["invited"] = {}
        data["usersData"][str(message.chat.id)]["invitedCol"] = 0
        data["usersData"][str(message.chat.id)]["inviter"] = None
        data["education"][str(message.chat.id)] = {}
        save_data()
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    cur.close()
    conn.close()
    ok = True
    ccc = True
    for el in users:
        if el[3] == message.chat.id:
            ok = False
            if el[6] != 0:
                ccc = False
    if ccc == True:
        if ok == True:
            conn = sql.connect('db.sql')
            cur = conn.cursor()
            cur.execute('INSERT INTO users (first_name, last_name, chatID, bagsTimeOut, autorizationStep, experience, level, coins, diamonds, tickets) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (message.from_user.first_name, message.from_user.last_name, message.chat.id, 0, 0, 0, 0, 0, 0, 0))
            conn.commit()
            cur.close()
            conn.close()
            start_command = message.text
            refer_id = str(start_command[7:])
            if refer_id != "" and refer_id != str(message.chat.id):
                data["usersData"][str(message.chat.id)]["inviter"] = int(refer_id)
                data["usersData"][str(refer_id)]["invitedCol"]+=1
                data["usersData"][str(message.chat.id)]["invited"][str(data["usersData"][str(refer_id)]["invitedCol"])] = message.chat.id
                save_data()
                bot.send_message(refer_id, f"По вашей ссылке зарегестрировался пользователь @{message.from_user.username}")
        markup = types.InlineKeyboardMarkup()
        btnBel = types.InlineKeyboardButton("Беларусь", callback_data="first_register_step:Беларусь")
        btnRus = types.InlineKeyboardButton("Россия", callback_data="first_register_step:Россия")
        btn1488 = types.InlineKeyboardButton('1488', url='https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        markup.row(btnBel)
        markup.row(btnRus)
        markup.row(btn1488)
        bot.send_message(message.chat.id,"Выбери страну", reply_markup=markup)
    if ccc==False and ok == False:
        Go_start(message)
def go_education(message):
    i = False
    for users in data["education"]:
        if users == str(message.chat.id):
            i = True
    if i == False or data['education'][str(message.chat.id)] == {}:
        data['education'][str(message.chat.id)]['completed_lesson'] = 0
        data['education'][str(message.chat.id)]['completed_tests'] = 0
        data['education'][str(message.chat.id)]['my_courses'] = {}
        data['education'][str(message.chat.id)]['complet_lessons'] = {}
        data['education'][str(message.chat.id)]['complet_tests'] = {}
        data['education'][str(message.chat.id)]['completed_courses'] = 0
        data['education'][str(message.chat.id)]['GPA'] = 0
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
    text = f"Давай начнем обучение.\n\nТы прошел(а):\n{data['education'][str(message.chat.id)]['completed_lesson']} уроков" \
           f"\n{data['education'][str(message.chat.id)]['completed_courses']} учебных курсов\n{data['education'][str(message.chat.id)]['completed_tests']} тестов\n" \
           f"\nСредний балл: {data['education'][str(message.chat.id)]['GPA']}\n\nРешено задач: {data['education'][str(message.chat.id)]['problems_solved']}" \
           f"\nРешено правильно: {data['education'][str(message.chat.id)]['decided_correctly']}"
    bot.send_message(message.chat.id, text, reply_markup=markup)
def my_courses(message):
    info = f"Вы прошли {data['education'][str(message.chat.id)]['completed_courses']} учебных курсов"
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Пройденные курсы", callback_data="completed_courses")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    for el in data['education'][str(message.chat.id)]['my_courses']:
        btn = types.InlineKeyboardButton(lessonsData['courses'][el]['name'], callback_data=f"course:{el}")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
def completed_courses(message):
    temp = data['education'][str(message.chat.id)]['my_courses']
    info = "Пройденныйе курсы:\n"
    for el in lessonsData['courses']:
        i = 0
        for i in range(0, data['education'][str(message.chat.id)]['completed_courses']):
            if (el[0] == temp[i]):
                info += lessonsData["courses"][i]["name"] + "\n"
            i += 1
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="my_courses")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
def courses_list(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    for el in lessonsData['courses']:
        btn = types.InlineKeyboardButton(lessonsData['courses'][el]['name'], callback_data=f"course:{el}")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери курс", reply_markup=markup)
def start_course(message, courseID):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Начать урок", callback_data=f"go_course_lesson:{courseID}")
    markup.add(btn)
    info = f"Курс {lessonsData['courses'][str(courseID)]['name']}:\n{lessonsData['courses'][str(courseID)]['subtitle']}\n\nКласс: {lessonsData['courses'][str(courseID)]['class']}\nУроков: {len(lessonsData['courses'][str(courseID)]['lessons'])}\n\nРекомендации к курсу: {lessonsData['courses'][str(courseID)]['recommendations']}"
    if str(courseID) in data['education'][str(message.chat.id)]['my_courses']:
        info += f"Пройдено уроков: {data['education'][str(message.chat.id)]['my_courses'][str(courseID)]['completed_lessons']}"
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
def go_course_lesson(message, courseID):
    if str(courseID) in data['education'][str(message.chat.id)]['my_courses']:
        pass
    else:
        data['education'][str(message.chat.id)]['my_courses'][str(courseID)]={"completed_lessons":0}
    save_data()
def lessons_list(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    for el in lessonsData['lessons']:
        btn = types.InlineKeyboardButton(lessonsData['lessons'][el]['name'], callback_data=f"lesson:{el}:1")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери урок", reply_markup=markup)
def tests_list(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    for el in lessonsData['tests']:
        btn = types.InlineKeyboardButton(lessonsData['tests'][el]['name'], callback_data=f"test:{el}:1:0:False")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери тест", reply_markup=markup)
def cheat_sheets_list(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    for el in lessonsData["subjects"]:
        btn = types.InlineKeyboardButton(lessonsData["subjects"][el], callback_data=f"sen_cheat_sheets_list:{lessonsData['subjects'][el]}")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери предмет", reply_markup=markup)
def start_lesson(message, lessonID, index):
    markup = types.InlineKeyboardMarkup()
    if index == len(lessonsData["lessons"][lessonID]["text"]):
        if str(lessonID) in data['education'][str(message.chat.id)]['complet_lessons']:
            data['education'][str(message.chat.id)]['complet_lessons'][str(lessonID)]+=1
        else:
            data['education'][str(message.chat.id)]['completed_lesson']+=1
            data['education'][str(message.chat.id)]['complet_lessons'][str(lessonID)]=1
        save_data()
        btn = types.InlineKeyboardButton("Пройти тест", callback_data=f'test:{lessonsData["lessons"][lessonID]["test"]}:1:0:False')
        markup.add(btn)
    else:
        btn = types.InlineKeyboardButton("Дальше", callback_data=f'lesson:{lessonID}:{index+1}')
        markup.add(btn)
    btn = types.InlineKeyboardButton("Закончить", callback_data='lessons_list')
    markup.add(btn)
    info = lessonsData["lessons"][lessonID]["text"][str(index)]
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
def start_test(message, testID, index, score, true=False):
    markup = types.InlineKeyboardMarkup()
    question = ""
    if index != 1 and true == False:
        question += "Не верно\nПравильный ответ: " + lessonsData["tests"][testID]["questions"][f"{index-1}variants"]["1"] + "\n\n"
    if true == True:
        question += "Верно\n\n"
        score+=1
    if index > len(lessonsData["tests"][testID]["questions"])/2:
        info = f"Результат теста\nВопросов: {index-1}\nПравильных ответов: {score}"
        if str(testID) in data['education'][str(message.chat.id)]['complet_tests']:
            data['education'][str(message.chat.id)]['complet_tests'][str(testID)]+=1
        else:
            data['education'][str(message.chat.id)]['completed_tests']+=1
            i = 10/(index-1)*score
            t = data['education'][str(message.chat.id)]['GPA']
            data['education'][str(message.chat.id)]['GPA'] = (i+t)/2
            data['education'][str(message.chat.id)]['complet_tests'][str(testID)]=1
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
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=question, reply_markup=markup)
def sen_cheat_sheets_list(message, subject):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="cheat_sheets_list")
    markup.add(btn)
    for el in lessonsData["cheat_sheets"]:
        btn = types.InlineKeyboardButton(lessonsData['cheat_sheets'][el]['name'], callback_data=f"sen_cheat_sheets:{el}")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"Шпаргалки по предмету {subject}", reply_markup=markup)
def sen_cheat_sheets(message, cheat_sheetsID):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"sen_cheat_sheets_list:{lessonsData['cheat_sheets'][cheat_sheetsID]['subject']}")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=lessonsData['cheat_sheets'][cheat_sheetsID]["text"], reply_markup=markup)
def Go_start(message):
    bot.send_message(message.chat.id, "Привет, я твой телеграм бот помощник. Что ты хочешь узнать?", reply_markup=my_markup())
def save_data():
    with open('data.json', 'w') as f:
        json.dump(data, f)
def my_room(message):
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE chatID = "%s"'%(message.chat.id))
    info = cur.fetchone()
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Школа", callback_data=f"school_info:{info[5]}")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Пригласить друга", callback_data="invite_frend")
    markup.add(btn)
    if (info[13] == None):
        btn = types.InlineKeyboardButton("Выбрать класс", callback_data=f"class_vibor")
        markup.add(btn)
    infoText = f"ID: {info[3]}\n\nИмя: {info[1]}\nФамилия: {info[2]}\n\nКласс: {info[13]}\n\nОпыт: {info[8]}\nУровень: {info[9]}\nМонеты: {info[10]}\nАлмазы: {info[11]}\nБилеты: {info[12]}\n\nПриглашено друзей: {data['usersData'][str(message.chat.id)]['invitedCol']}"
    bot.send_message(message.chat.id, infoText, reply_markup=markup)

@bot.message_handler(commands=['op'])
def main(message):
  if (message.chat.id != 1917247858):
    bot.send_message(message.chat.id, "Вам не доступна эта команда")
    return
  bot.send_message(message.chat.id, 'Введите имя администратора')
  bot.register_next_step_handler(message, addAdmin)

@bot.message_handler(commands=['deop'])
def main(message):
  if (message.chat.id != 1917247858):
    bot.send_message(message.chat.id, "Вам не доступна эта команда")
    return
  bot.send_message(message.chat.id, 'Введите имя администратора')
  bot.register_next_step_handler(message, delAdmin)

def delAdmin(message):
  conn = sql.connect('bd.sql')
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
  conn = sql.connect('bd.sql')
  cur = conn.cursor()

  cur.execute('SELECT * FROM users')
  users = cur.fetchall()

  chatID = None

  for el in users:
    if(message.text.strip() == el[1]):
      chatID = el[3]
  if chatID == None:
    bot.send_message(message.chat.id, "Такого пользователя не существует")
    cur.close()
    conn.close()
    return

  cur.execute('INSERT INTO admins (name, chatID) VALUES ("%s", "%s")' % (message.text.strip(), chatID))
  conn.commit()
  bot.send_message(message.chat.id, 'Администратор успешно добавлен')
  cur.close()
  conn.close()

@bot.message_handler()
def main(message):
    if message.text == "Личный кабинет 🪪":
        my_room(message)
    elif message.text == "Настройки ⚙️":
        bot.send_message(message.chat.id, "Раздел находится в разработке")
    elif message.text == "Обучение 📖":
        go_education(message)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global data
    callRazd = call.data.split(':')
    if callRazd[0] == "first_register_step":
        data["usersData"][str(call.message.chat.id)]["contry"] = callRazd[1]
        send_vibor_obl(call)
    elif callRazd[0] == "second_register_step":
        data["usersData"][str(call.message.chat.id)]["obl"] = callRazd[1]
        send_vibor_sity(call.message)
    elif callRazd[0] == "second_register_step_else":
        data["usersData"][str(call.message.chat.id)]["botMessageID"] = call.message
        data["usersData"][str(call.message.chat.id)]["MessageID"] = bot.send_message(call.message.chat.id, "Введите название").message_id
        bot.register_next_step_handler(call.message, else_obl)
    elif callRazd[0] == "serd_register_step":
        data["usersData"][str(call.message.chat.id)]["sity"] = callRazd[1]
        send_vibor_school(call.message)
    elif callRazd[0] == "serd_register_step_else":
        data["usersData"][str(call.message.chat.id)]["botMessageID"] = call.message
        data["usersData"][str(call.message.chat.id)]["MessageID"] = bot.send_message(call.message.chat.id, "Введите название").message_id
        bot.register_next_step_handler(call.message, else_sity)
    elif callRazd[0] == "fourth_register_step":
        conn = sql.connect('db.sql')
        cur = conn.cursor()
        cur.execute(f"SELECT schoolID FROM schools WHERE school = ?",(callRazd[1],))
        school = cur.fetchone()
        cur.execute('UPDATE users SET schoolID = ? WHERE chatID = ?', (school[0], call.message.chat.id))
        cur.execute('UPDATE users SET autorizationStep = ? WHERE chatID = ?', (1, call.message.chat.id))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(call.message.chat.id, "Вы успешно зарегистрированы")
        Go_start(call.message)
    elif callRazd[0] == "fourth_register_step_else":
        data["usersData"][str(call.message.chat.id)]["botMessageID"] = call.message
        data["usersData"][str(call.message.chat.id)]["MessageID"] = bot.send_message(call.message.chat.id, "Введите название").message_id
        bot.register_next_step_handler(call.message, else_school)
    elif callRazd[0] == "school_info":
        conn = sql.connect('db.sql')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM schools WHERE schoolID = ?", (int(callRazd[1]),))
        info = cur.fetchone()
        if info == None:
            return
        cur.close()
        conn.close()
        infoText = f'ID: {info[1]}\n\nСтрана: {info[2]}\nОбласть: {info[3]}\nГород/деревня: {info[4]}\nШкола: {info[5]}\nРэйтинг: {info[6]}'
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Назад", callback_data="back_to_my_room")
        btn1 = types.InlineKeyboardButton("Изменить класс", callback_data="class_vibor")
        markup.add(btn, btn1)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=infoText, reply_markup=markup)
    elif callRazd[0] == "back_to_my_room":
        conn = sql.connect('db.sql')
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
        markup = types.InlineKeyboardMarkup()
        i = 0
        for i in range(0,11):
            i+=1
            btn = types.InlineKeyboardButton(str(i), callback_data=f"set_class:{i}")
            markup.add(btn)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбери класс",reply_markup=markup)
    elif callRazd[0] == "set_class":
        conn = sql.connect('db.sql')
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
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбери класс", reply_markup=markup)
    elif callRazd[0] == "set_class_letter":
        conn = sql.connect('db.sql')
        cur = conn.cursor()
        cur.execute('SELECT class FROM users WHERE chatID = ?', (call.message.chat.id,))
        temp = cur.fetchone()
        cur.execute('UPDATE users SET class = ? WHERE chatID = ?', (f'{temp[0]}"{callRazd[1]}"', call.message.chat.id))
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
        bot.send_message(call.message.chat.id, f"Если ваш друг перейдет по вашей реферальной ссылке, то вы получите 10 алмазов\n\nВаша ссылка:\nhttps://t.me/{BOT_NICKNAME}?start={call.message.chat.id}\n\nТекущее количество приглашенных людей: {data['usersData'][str(call.message.chat.id)]['invitedCol']}")
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
        sen_cheat_sheets_list(call.message, callRazd[1])
    elif callRazd[0] == "sen_cheat_sheets":
        sen_cheat_sheets(call.message, callRazd[1])
    elif callRazd[0] == "go_course_lesson":
        go_course_lesson(call.message, callRazd[1])

def send_vibor_obl(call):
    markup = types.InlineKeyboardMarkup()

    conn = sql.connect('db.sql')
    cur = conn.cursor()
    temp = data["usersData"][f"{call.message.chat.id}"]["contry"]
    cur.execute('SELECT obl FROM schools WHERE contry = ?', (temp,))
    obls = cur.fetchall()
    cur.close()
    conn.close()
    for el in obls:
        if str(el[0]) != "None":
            btn = types.InlineKeyboardButton(str(el[0]), callback_data=f"second_register_step:{el[0]}")
            markup.add(btn)
    btn = types.InlineKeyboardButton("Другая", callback_data=f"second_register_step_else")
    markup.add(btn)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выбери область',reply_markup=markup)

def else_obl(message):
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('INSERT INTO schools (contry, obl) VALUES ("%s", "%s")' % (data["usersData"][f"{message.chat.id}"]["contry"], message.text))
    conn.commit()
    cur.close()
    conn.close()
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, data["usersData"][str(message.chat.id)]["MessageID"])
    data["usersData"][f"{message.chat.id}"]["obl"] = message.text
    send_vibor_sity(data["usersData"][f"{message.chat.id}"]["botMessageID"])

def send_vibor_sity(message):
    markup = types.InlineKeyboardMarkup()

    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('SELECT sity FROM schools WHERE contry = ? AND obl = ?', (data["usersData"][f"{message.chat.id}"]["contry"], data["usersData"][f"{message.chat.id}"]["obl"]))
    sitys = cur.fetchall()
    cur.close()
    conn.close()
    for el in sitys:
        if str(el[0]) != "None":
            btn = types.InlineKeyboardButton(str(el[0]), callback_data=f"serd_register_step:{el[0]}")
            markup.add(btn)
    btn = types.InlineKeyboardButton("Друой", callback_data=f"serd_register_step_else")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Выбери город',reply_markup=markup)

def else_sity(message):
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('INSERT INTO schools (contry, obl, sity) VALUES ("%s", "%s", "%s")' % (data["usersData"][f"{message.chat.id}"]["contry"],data["usersData"][f"{message.chat.id}"]["obl"],  message.text))
    conn.commit()
    cur.close()
    conn.close()
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, data["usersData"][str(message.chat.id)]["MessageID"])
    data["usersData"][f"{message.chat.id}"]["sity"] = message.text
    send_vibor_school(data["usersData"][f"{message.chat.id}"]["botMessageID"])

def send_vibor_school(message):
    markup = types.InlineKeyboardMarkup()

    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('SELECT school FROM schools WHERE contry = ? AND obl = ? AND sity = ?',
                (data["usersData"][f"{message.chat.id}"]["contry"], data["usersData"][f"{message.chat.id}"]["obl"], data["usersData"][f"{message.chat.id}"]["sity"]))
    schools = cur.fetchall()
    cur.close()
    conn.close()
    for el in schools:
        if str(el[0]) != "None":
            btn = types.InlineKeyboardButton(str(el[0]), callback_data=f"fourth_register_step:{el[0]}")
            markup.add(btn)
    btn = types.InlineKeyboardButton("Другая", callback_data=f"fourth_register_step_else")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Выбери школу',reply_markup=markup)

def else_school(message):
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('SELECT school FROM schools')
    schols = cur.fetchall()
    cur.execute('INSERT INTO schools (contry, obl, sity, school, schoolID, rating) VALUES ("%s", "%s", "%s", "%s", "%s", "%s")' % (
    data["usersData"][f"{message.chat.id}"]["contry"], data["usersData"][f"{message.chat.id}"]["obl"], data["usersData"][f"{message.chat.id}"]["sity"], message.text, len(schols),0))
    cur.execute(f'UPDATE users SET schoolID = {len(schols)} WHERE chatID = {message.chat.id}')
    cur.execute(f'UPDATE users SET autorizationStep = {1} WHERE chatID = {message.chat.id}')
    conn.commit()
    cur.close()
    conn.close()
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, data["usersData"][str(message.chat.id)]["MessageID"])
    bot.send_message(message.chat.id,"Вы успешно зарегистрированы, для начала работы с ботом пропишите /start")
    Go_start(message)

bot.polling(none_stop=True)