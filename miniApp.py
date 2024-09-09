from datetime import datetime
import time
from urllib.parse import urlparse, parse_qs
import config
import flet as ft
import sqlite3 as sql
import asyncio

def sql_conn():
    conn = sql.connect("db.sql")
    return conn

conn = sql_conn()
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS clicker (chatID int primary key, clicks varchar(50), energy int, maxEnergy int, multitap int, boost int, megaEnergy int, lastSeen int, regenEnergySpeed int)')
conn.commit()
cur.close()
conn.close()
async def edit_clicks(chatID, col=1, znac="+", energy = 1):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT clicks FROM clicker WHERE chatID = ?', (chatID,))
    clicks = int(cur.fetchone()[0])
    if znac == "+": clicks+=col
    elif znac == "-": clicks-= col
    cur.execute('SELECT lastSeen FROM clicker WHERE chatID = ?', (chatID,))
    lastSeen = cur.fetchone()[0]
    if int(datetime.now().timestamp()) - lastSeen >=5:
        cur.execute('UPDATE clicker SET energy = energy + 1 WHERE chatID = ?', (chatID,))
        cur.execute('UPDATE clicker SET lastSeen = ? WHERE chatID=?', (datetime.now().timestamp(), chatID))
    cur.execute('UPDATE clicker SET clicks = ? WHERE chatID=?', (str(clicks), chatID))
    cur.execute('UPDATE clicker SET energy = energy - ? WHERE chatID=?', (energy, chatID))
    conn.commit()
    cur.close()
    conn.close()
def check_for_auto_clicker(clicks, old_clicks):
    #if abs(clicks[1]-clicks[0]) <= 0.08 or abs(round(clicks[1] - clicks[0], 3)) == abs(round(old_clicks[1] - old_clicks[0], 3)):
    #   return True
    return False
async def main(page: ft.Page):
    page.title = "kretoffer clicker"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.fonts = {"standart": "fonts/standart.otf"}
    page.theme = ft.Theme(font_family="standart")
    page.bgcolor = "#000000"
    query_params = parse_qs(urlparse(page.route).query)
    chatID = int(query_params.get("userID", [0])[0])
    last_clicks = [0, 3]
    old_last_clicks = [0, 8]
    clicksStep = 0
    last_auto = 0

    async def click(e: ft.ControlEvent):
        nonlocal clicksStep, last_clicks, old_last_clicks, last_auto
        last_clicks[clicksStep] = datetime.now().timestamp()
        clicksStep += 1
        last_auto += 1
        if clicksStep >= 2: clicksStep = 0
        if check_for_auto_clicker(last_clicks, old_last_clicks):
            await edit_clicks(chatID, 1, znac="-")
            score.data -= 1
            if last_auto <= 15:
                await edit_clicks(chatID, 10, znac="-")
                score.data -= 10
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Не используйте автокликер", size=30, text_align=ft.TextAlign.CENTER, color="#FF0000"),
                    bgcolor="#25223A")
                page.snack_bar.open = True
                page.update()
            last_auto = 0
            score.value = str(score.data)
            return
        old_last_clicks = last_clicks.copy()
        if progress_bar.data <= 0:
            conn = sql_conn()
            cur = conn.cursor()
            cur.execute('SELECT lastSeen FROM clicker WHERE chatID = ?', (chatID,))
            lastSeen = cur.fetchone()[0]
            if int(datetime.now().timestamp()) - lastSeen >= 5:
                while int(datetime.now().timestamp()) - lastSeen >= 5:
                    cur.execute('UPDATE clicker SET energy = energy + 1 WHERE chatID = ?', (chatID,))
                    progress_bar.data += 1
                    cur.execute('UPDATE clicker SET lastSeen = ? WHERE chatID=?', (datetime.now().timestamp(), chatID))
                    conn.commit()
                    lastSeen+=5
                cur.close()
                conn.close()
                return
            page.snack_bar = ft.SnackBar(content=ft.Text("У вас нет энергии", size=30, text_align=ft.TextAlign.CENTER, color="#FFFFFF"), bgcolor="#25223A")
            page.snack_bar.open = True
            page.update()
            return
        score.data += 1
        score.value = str(score.data)
        button.scale = 0.7
        progress_bar.data -= 1
        progress_bar.value = progress_bar.data/user[3]
        page.update()
        await edit_clicks(chatID)
        await asyncio.sleep(0.1)
        button.scale = 1
        page.update()

    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM clicker WHERE chatID = ?', (chatID,))
    user = cur.fetchone()
    user = list(user)
    if user is not None: clicks = int(user[1])
    else: pass
    if user[2] != user[3]:
        user[2]+=(int(datetime.now().timestamp())-user[7])/5
        if user[2] > user[3]: user[2] = user[3]
        cur.execute('UPDATE clicker SET energy = ? WHERE chatID = ?', (user[2], chatID))
        conn.commit()
    cur.close()
    conn.close()
    async def open_dilog(e):
        page.dialog = clicks_to_coins_dilog
        clicks_to_coins_dilog.open = True
        page.update()
    async def clicks_to_coins(e):
        if score.data >= 10:
            conn = sql_conn()
            cur = conn.cursor()
            cur.execute("UPDATE clicker SET clicks = 0 WHERE chatID = ?", (chatID,))
            cur.execute("UPDATE users SET coins = coins + ? WHERE chatID = ?", (int(score.data/10), chatID))
            conn.commit()
            cur.close()
            conn.close()
            score.data = 0
            score.value = "0"
            page.dialog.title = ft.Text("Все супер")
            page.dialog.content = ft.Text("Клики успешно выведены")
            page.dialog.actions = [ft.TextButton("Выйти", on_click=close_dilog)]
            page.update()
        else:
            page.dialog.title = ft.Text("Мало натапал")
            page.dialog.content = ft.Text("У вас недостаточно кликов, тапайте дальше")
            page.dialog.actions = [ft.TextButton("Выйти", on_click=close_dilog)]
            page.update()
    async def close_dilog(e):
        clicks_to_coins_dilog.open = False
        page.update()

    score = ft.Text(value=str(clicks), data=clicks, size=100)
    score_counter = ft.Text(size=50, animate_opacity=ft.Animation(duration=600, curve=ft.AnimationCurve.BOUNCE_IN))

    button = ft.Container(bgcolor="#030059", border=ft.border.all(30, "#010025"), border_radius=250, width=page.width*0.8, height=page.width*0.8, animate_scale=ft.Animation(duration=600, curve=ft.AnimationCurve.EASE), margin=ft.margin.only(bottom=50), on_click=click, content=ft.Text("Типа хомяк", size=35), alignment=ft.alignment.center)

    clicks_to_coins_btn=ft.Container(bgcolor="#141414", border_radius=15, alignment=ft.alignment.center, content=ft.Text("Клики в монеты", size=30), height=120, width=page.width, margin=ft.margin.symmetric(vertical=10), on_click=open_dilog)

    clicks_to_coins_dilog = ft.AlertDialog(
        modal=True, title=ft.Text("Вы уверены"),
        content=ft.Text("Если вы уверены, то все ваши клики исчезнут, а в @kretoffer_school_bot появятся монеты. Нынешний курс 10 кликов = 1 монета"),
        actions=[
            ft.TextButton("Вывести", on_click=clicks_to_coins),
            ft.TextButton("Отмена", on_click=close_dilog)
        ],actions_alignment=ft.MainAxisAlignment.END
    )

    progress_bar = ft.ProgressBar(value=user[2] / user[3], width=page.width*0.95, bar_height=20, color="#d17c0d", bgcolor="#844e08", data=user[2])
    progress_bar_container = ft.Container(progress_bar, alignment=ft.alignment.center, border_radius=30)
    main_ui = ft.Container(content=ft.Column([
        ft.Row([score], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([ft.Stack([
            button,
            score_counter
        ], alignment=ft.MainAxisAlignment.CENTER)], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([progress_bar_container], alignment=ft.MainAxisAlignment.CENTER),
        clicks_to_coins_btn
    ]), alignment=ft.alignment.center)


    page.add(main_ui)

def run_miniApp():
    ft.app(target=main, view=None, port=config.miniAppPort, assets_dir="assets")

if __name__ == "__main__":
    ...#run_miniApp()
run_miniApp()