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

    # Provide a storage-compatible shim so both versions of Flet work.
    # Some environments expose page.client_storage; others don't. Create a minimal
    # fallback that tries page.session (if available) and otherwise keeps values
    # in-memory on the page object.
    if not hasattr(page, "client_storage"):
        class ClientStorageFallback:
            def __init__(self, page):
                self._page = page
                if not hasattr(self._page, "_in_memory_storage"):
                    self._page._in_memory_storage = {}
            def set(self, key, value):
                try:
                    # Prefer session API if present
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
                # 1. Extract the temporary OAuth code
                auth_code = page.route.split("?code=")[1].split("&")[0]
                
                try:
                    # 2. Exchange the code for a REAL Supabase Session (which contains the JWT)
                    session_data = supabase_auth.auth.exchange_code_for_session({"auth_code": auth_code})
                    real_jwt_token = session_data.session.access_token
                    
                    # 3. Save the REAL JWT token to client storage
                    page.client_storage.set("auth_token", real_jwt_token)
                    
                    print("Google Login Success! Directing to /chat")
                    time.sleep(1) 
                    page.go("/chat")
                    return
                    
                except Exception as e:
                    print(f"Google Auth Exchange failed: {e}")
                    # If it fails, clear the URL and force them to log in normally
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
            # Retrieve token securely from the browser
            stored_token = page.client_storage.get("auth_token")
            
            if not stored_token:
                print("No auth token - redirecting to login")
                page.go("/login")
                return  # Stop execution and let the router handle the redirect
            else:
                page.views.append(ChatPage(page, auth_token=stored_token))

        # Fallback
        else:
            page.views.append(HomePage(page))

        page.update()
        
    page.on_route_change = route_change
    
    # Start the app at the current browser route if set, otherwise default to "/"
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