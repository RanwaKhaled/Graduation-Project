# frontend/main.py
import flet as ft
import os
import time
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pages.home import HomePage
from pages.login import LoginPage
from pages.chat import ChatPage
from pages.signup import SignupPage
from pages.contact import ContactPage
from pages.reset_pass import ResetPage
from pages.new_pass import NewPassPage
from backend.database import supabase_auth

def main(page: ft.Page):
    page.title = "Yosr"
    page.theme = ft.Theme(color_scheme_seed="#6B21A8")
    page.padding = 0
    page.bgcolor = "#F8F9FA"

    if not hasattr(page, "client_storage"):
        class ClientStorageFallback:
            def __init__(self, p):
                self._page = p
                if not hasattr(self._page, "_in_memory_storage"):
                    self._page._in_memory_storage = {}
            def set(self, key, value):
                try:
                    if hasattr(self._page, "session") and hasattr(self._page.session, "set"):
                        self._page.session.set(key, value)
                    else:
                        self._page._in_memory_storage[key] = value
                except Exception:
                    self._page._in_memory_storage[key] = value
            def get(self, key):
                try:
                    if hasattr(self._page, "session") and hasattr(self._page.session, "get"):
                        return self._page.session.get(key)
                    return self._page._in_memory_storage.get(key)
                except Exception:
                    return self._page._in_memory_storage.get(key)
        page.client_storage = ClientStorageFallback(page)

    def route_change(e):
        print(f"Route changed → {page.route}")
        page.views.clear()

        # Route: Home
        if page.route == "/" or page.route == "":
            page.views.append(HomePage(page))

        # Route: Login & Google OAuth Capture
        elif page.route.startswith("/login"):
            if "?code=" in page.route:
                auth_code = page.route.split("?code=")[1].split("&")[0]
                
                try:
                    saved_verifier = page.client_storage.get("pkce_verifier")
                    if saved_verifier:
                        supabase_auth.auth._storage.set_item("supabase.auth.token-code-verifier", saved_verifier)

                    session_data = supabase_auth.auth.exchange_code_for_session({"auth_code": auth_code})
                    real_jwt_token = session_data.session.access_token
                    
                    page.client_storage.set("auth_token", real_jwt_token)
                    
                    print("Google Login Success! Directing to /chat")
                    time.sleep(1) 
                    page.go("/chat")
                    return
                    
                except Exception as ex:
                    print(f"Google Auth Exchange failed: {ex}")
                    page.go("/login")
                    return
            else:
                page.views.append(LoginPage(page))

        # Route: Signup, Reset, Contact
        elif page.route == "/signup":
            page.views.append(SignupPage(page))

        elif page.route == "/reset":
            page.views.append(ResetPage(page))

        elif page.route == "/new_pass":
            page.views.append(NewPassPage(page))

        elif page.route == "/contact":
            page.views.append(ContactPage(page))

        # Route: Chat (Protected)
        elif page.route == "/chat":
            stored_token = page.client_storage.get("auth_token")
            
            if not stored_token:
                print("No auth token - redirecting to login")
                page.go("/login")
                return 
            else:
                page.views.append(ChatPage(page, auth_token=stored_token))

        # Fallback
        else:
            page.views.append(HomePage(page))

        page.update()
        
    page.on_route_change = route_change
    
    if not page.route or page.route == "" or page.route == "/":
        page.route = "/"
    route_change(None)     
    page.update()

ft.run(
    main, 
    assets_dir="assets", 
    view=ft.AppView.WEB_BROWSER, 
    port=8080
)