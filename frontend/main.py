# frontend/main.py
import flet as ft
import os
import sys

# 1. This MUST run before importing any local project modules!
# It forces Python to look at the parent directory (Graduation-Project) so it can see 'backend'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
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
        
        # --- GOOGLE OAUTH URL TOKEN SNIFFER ---
        current_url = page.route
        
        # Check if the landing URL contains either a direct code or an access token string
        if "?code=" in current_url or "#access_token=" in current_url or "code=" in current_url:
            print("OAuth redirect detected, attempting to parse token...")
            try:
                # Handle standard query parameters (?code=...)
                if "?" in current_url:
                    raw_params = current_url.split("?")[1]
                # Handle hash fragments (#access_token=...)
                elif "#" in current_url:
                    raw_params = current_url.split("#")[1]
                else:
                    raw_params = current_url

                # Build a clean dictionary out of the parameters
                params = dict(item.split("=") for item in raw_params.split("&") if "=" in item)
                
                # Check for either code or access_token
                auth_code = params.get("code")
                token = params.get("access_token")
                
                if auth_code or token:
                    print(f"Google Auth credentials caught successfully! Key: {auth_code or token}")
                    
                    # Store the credential securely so your chat guard passes
                    page.auth_token = auth_code or token
                    
                    # Route straight past the login guard directly to your chat dashboard!
                    page.route = "/chat"

                    
            except Exception as ex:
                print(f"Error parsing OAuth redirect values: {str(ex)}")
        # --- END OAUTH SNIFFER ---
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
            if not hasattr(page, "auth_token"):
                page.route = "/login"
                page.update()
                return
            page.views.append(ChatPage(page))    
        #elif page.route == "/chat":
            #if not page.session.store.contains_key("key"):
                #page.push_route("/login")  # was page.go()
                #return
            #page.views.append(ChatPage(page))
        page.update()

    page.on_route_change = route_change
    route_change(None) 
    page.update()
    #page.push_route("/")  # was page.go("/")

ft.run(main, assets_dir="assets",view=ft.AppView.WEB_BROWSER ,port=8080)  # was ft.app()