import time
from urllib.parse import urlparse, parse_qs
import config
import flet as ft
import sqlite3 as sql

def sql_conn():
    conn = sql.connect("db.sql")
    return conn

conn = sql_conn()
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS clicker (chatID int primary key, clicks varchar(50))')
conn.commit()
cur.close()
conn.close()
async def clicks(chatID,col=1, znac="+"):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT clicks FROM clicker WHERE chatID = ?', (chatID,))
    clicks = int(cur.fetchone()[0])
    if znac == "+": clicks+=col
    elif znac == "-": clicks-= col
    cur.execute('UPDATE clicker SET clicks = ? WHERE chatID=?', (str(clicks), chatID))
async def main(page: ft.Page):
    page.title = "kretoffer clicker"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.fonts = {"standart": "fonts/standart.otf"}
    page.theme = ft.Theme(font_family="standart")
    query_params = parse_qs(urlparse(page.route).query)
    chatID = query_params.get("chatID", [0])[0]

    def click(e):
        score.data += 1
        score.value = str(score.data)
        button.scale = 0.7
        page.update()
        time.sleep(0.1)
        button.scale = 1
        page.update()

    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT clicks FROM clicker WHERE chatID = ?', (chatID,))
    clicks = int(cur.fetchone()[0])
    cur.close()
    conn.close()
    score = ft.Text(value=str(clicks), data=clicks, size=100)
    score_counter = ft.Text(size=50, animate_opacity=ft.Animation(duration=600, curve=ft.AnimationCurve.BOUNCE_IN))

    button = ft.Container(bgcolor="#030059", border_radius=250, width=page.width*0.8, height=page.width*0.8, animate_scale=ft.Animation(duration=600, curve=ft.AnimationCurve.EASE), margin=ft.margin.only(bottom=50), on_click=click)

    progress_bar = ft.Container(ft.ProgressBar(value=0, width=page.width*0.95, bar_height=20, color="#FF8B1F", bgcolor="#BF6524"), alignment=ft.alignment.center, border_radius=30)
    main_ui = ft.Container(content=ft.Column([
        ft.Row([score], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([ft.Stack([
            button,
            score_counter
        ], alignment=ft.MainAxisAlignment.CENTER)], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([progress_bar], alignment=ft.MainAxisAlignment.CENTER)
    ]), alignment=ft.alignment.center)


    page.add(main_ui)

ft.app(target=main, view=None, port=config.miniAppPort, assets_dir="assets")