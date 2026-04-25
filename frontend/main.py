# frontend/main.py
import flet as ft
from pages.home import HomePage
from pages.login import LoginPage
from pages.chat import ChatPage
from pages.signup import SignupPage
from pages.contact import ContactPage
from pages.reset_pass import ResetPage
from pages.new_pass import NewPassPage

def main(page: ft.Page):
    page.title = "Yosr"
    page.theme = ft.Theme(color_scheme_seed="#6B21A8")

    def route_change(e):
        print(f"route changed to {page.route}")
        page.views.clear()
        if page.route == "/":
            page.views.append(HomePage(page))
        elif page.route == "/login":
            page.views.append(LoginPage(page))
        elif page.route == "/signup":
            page.views.append(SignupPage(page))
        elif page.route == "/reset":
            page.views.append(ResetPage(page))
        elif page.route == "/new_pass":
            page.views.append(NewPassPage(page))
        elif page.route == "/contact":
            page.views.append(ContactPage(page))
        elif page.route == "/chat":
            if not page.session.store.contains_key("key"):
                page.push_route("/login")  # was page.go()
                return
            page.views.append(ChatPage(page))
        page.update()

    page.on_route_change = route_change
    page.views.append(HomePage(page))
    page.update()
    #page.push_route("/")  # was page.go("/")

ft.run(main, assets_dir="assets", port=8080)  # was ft.app()