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
cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, first_name varchar(50), last_name varchar(50), chatID int, bagsTimeOut float, schoolID int, autorizationStep int, teacher bit)')
cur.execute('CREATE TABLE IF NOT EXISTS schools(id int auto_increment primary key, schoolID int, contry varchar(20), obl varchar(50), sity varchar(50), school varchar(50))')
cur.execute('CREATE TABLE IF NOT EXISTS bags (id int auto_increment primary key, date varchar(50), user varchar(100), bag varchar(5000), bagId int)')
cur.execute('CREATE TABLE IF NOT EXISTS admins (id int auto_increment primary key, name varchar(50), chatID int)')
#cur.execute('INSERT INTO schools (contry) VALUES ("%s")' % ("Беларусь"))
#cur.execute('INSERT INTO schools (contry) VALUES ("%s")' % ("Россия"))

conn.commit()
cur.close()
conn.close()
data = {
    "usersData":{

    }
}
@bot.message_handler(commands=['start'])
def main(message):
    data["usersData"][str(message.chat.id)] = {}
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    cur.close()
    conn.close()
    ok = True
    ccc = True
    for el in users:
        print(el)
        if el[3] == message.chat.id:
            ok = False
            if el[6] != 0:
                ccc = False
    if ccc == True:
        if ok == True:
            conn = sql.connect('db.sql')
            cur = conn.cursor()
            cur.execute('INSERT INTO users (first_name, last_name, chatID, bagsTimeOut, autorizationStep) VALUES ("%s", "%s", "%s", "%s", "%s")' % (message.from_user.first_name, message.from_user.last_name, message.chat.id, 0, 0))
            conn.commit()
            cur.close()
            conn.close()
        markup = types.InlineKeyboardMarkup()
        btnBel = types.InlineKeyboardButton("Беларусь", callback_data="first_register_step:Беларусь")
        btnRus = types.InlineKeyboardButton("Россия", callback_data="first_register_step:Россия")
        btn1488 = types.InlineKeyboardButton('1488', url='https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        markup.row(btnBel)
        markup.row(btnRus)
        markup.row(btn1488)
        bot.send_message(message.chat.id,"Выбери страну", reply_markup=markup)

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
  conn = sqlite3.connect('bd.sql')
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
  conn = sqlite3.connect('bd.sql')
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
    elif callRazd[0] == "fourth_register_step_else":
        data["usersData"][str(call.message.chat.id)]["botMessageID"] = call.message
        data["usersData"][str(call.message.chat.id)]["MessageID"] = bot.send_message(call.message.chat.id, "Введите название").message_id
        bot.register_next_step_handler(call.message, else_school)


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
    btn = types.InlineKeyboardButton("Друая", callback_data=f"fourth_register_step_else")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Выбери школу',reply_markup=markup)

def else_school(message):
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('SELECT school FROM schools')
    schols = cur.fetchall()
    cur.execute('INSERT INTO schools (contry, obl, sity, school, schoolID) VALUES ("%s", "%s", "%s", "%s", "%s")' % (
    data["usersData"][f"{message.chat.id}"]["contry"], data["usersData"][f"{message.chat.id}"]["obl"], data["usersData"][f"{message.chat.id}"]["sity"], message.text, len(schols)))
    cur.execute(f'UPDATE users SET schoolID = {len(schols)-1} WHERE chatID = {message.chat.id}')
    cur.execute(f'UPDATE users SET autorizationStep = {1} WHERE chatID = {message.chat.id}')
    conn.commit()
    cur.close()
    conn.close()
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, data["usersData"][str(message.chat.id)]["MessageID"])
    bot.send_message(message.chat.id,"Вы успешно зарегистрированы, для начала работы с ботом пропишите /start")

bot.polling(none_stop=True)