import flet as ft

async def main(page: ft.Page):
    page.title = "kretoffer clicker"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.fonts = {"standart": "fonts/standart.otf"}
    page.theme = ft.Theme(font_family="standart")

    score = ft.Text(value="0", data=0, size=100)
    score_counter = ft.Text(size=50, animate_opacity=ft.Animation(duration=600, curve=ft.AnimationCurve.BOUNCE_IN))

    button = ft.Container(bgcolor="#030059", border_radius=200, width=page.width*0.8, height=page.width*0.8, animate_scale=ft.Animation(duration=600, curve=ft.Animation.E))

    page.add()

ft.app(target=main, view=ft.WEB_BROWSER, port=26112, assets_dir="assets")