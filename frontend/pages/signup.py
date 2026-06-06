# frontend/pages/signup.py
import flet as ft
import re
import requests
from backend.database import supabase_auth

# colors: global vars (legacy)
purple = "#450A75"
blue = "#E4FAFD"
babypink = "#FFEFF3"
pink = "#F0A4BF"
orange = "#F75C2D"
lightgrey = "#EBEBEB"
grey = "#7D7D7D"
darkgrey = "#2D2D2D"
white = "#FFFFFF"
black = "#000000"
lilac = "#F4E6FF"

# design tokens (matching login.py)
deep_purple = "#2D0550"
mid_purple = "#6B1FA8"
soft_purple = "#9B59D4"
teal_accent = "#C8F5F9"
card_bg = "#FAFAFA"
input_bg = "#F2F2F7"
input_border = "#E0E0E8"
input_focus = "#6B1FA8"
label_color = "#9090A8"
text_primary = "#1A1A2E"
text_secondary = "#6B6B80"
divider_color = "#EBEBF0"
orange_accent = "#F75C2D"

class SignupPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/signup", padding=0, bgcolor=deep_purple)

        # the back button (goes back home)
        self.back_btn = ft.Container(
            content=ft.Icon(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, color=text_secondary, size=16),
            bgcolor=white,
            width=40,
            height=40,
            border_radius=12,
            shadow=ft.BoxShadow(
                blur_radius=8,
                spread_radius=0,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            on_click=lambda _: page.go("/")
        )

        # First Name field
        self.firstname_field = ft.TextField(
            label="First name",
            label_style=ft.TextStyle(color=label_color, size=13),
            bgcolor=input_bg,
            color=text_primary,
            width=170,
            height=56,
            border_radius=14,
            border=ft.Border.all(1.5, input_border),
            focused_border_color=input_focus,
            focused_border_width=1.5,
            cursor_color=mid_purple,
            text_style=ft.TextStyle(size=15, weight=ft.FontWeight.W_400),
        )

        # Last Name field
        self.lastname_field = ft.TextField(
            label="Last name",
            label_style=ft.TextStyle(color=label_color, size=13),
            bgcolor=input_bg,
            color=text_primary,
            width=170,
            height=56,
            border_radius=14,
            border=ft.Border.all(1.5, input_border),
            focused_border_color=input_focus,
            focused_border_width=1.5,
            cursor_color=mid_purple,
            text_style=ft.TextStyle(size=15, weight=ft.FontWeight.W_400),
        )

        # email field
        self.email_field = ft.TextField(
            label="Email address",
            label_style=ft.TextStyle(color=label_color, size=13),
            bgcolor=input_bg,
            color=text_primary,
            width=360,
            height=56,
            border_radius=14,
            border=ft.Border.all(1.5, input_border),
            focused_border_color=input_focus,
            focused_border_width=1.5,
            prefix_icon=ft.Icons.ALTERNATE_EMAIL_ROUNDED,
            cursor_color=mid_purple,
            text_style=ft.TextStyle(size=15, weight=ft.FontWeight.W_400),
        )

        # password field
        self.password_field = ft.TextField(
            label="Password",
            label_style=ft.TextStyle(color=label_color, size=13),
            password=True,
            can_reveal_password=True,
            bgcolor=input_bg,
            color=text_primary,
            width=360,
            height=56,
            border_radius=14,
            border=ft.Border.all(1.5, input_border),
            focused_border_color=input_focus,
            focused_border_width=1.5,
            prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED,
            cursor_color=mid_purple,
            text_style=ft.TextStyle(size=15, weight=ft.FontWeight.W_400),
        )

        # shared error message
        self.shared_error = ft.Text("", color=orange_accent, size=13, visible=False)

        # Submit button — gradient style matching login.py
        self.submit_btn_text = ft.Text("Create account", size=16, color=white, weight=ft.FontWeight.W_600)
        self.submit_btn = ft.Container(
            content=self.submit_btn_text,
            width=360,
            height=52,
            border_radius=14,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=[mid_purple, soft_purple],
            ),
            shadow=ft.BoxShadow(
                blur_radius=20,
                spread_radius=0,
                color=ft.Colors.with_opacity(0.35, mid_purple),
                offset=ft.Offset(0, 6),
            ),
            alignment=ft.Alignment(0, 0),
            on_click=self.submit_clicked,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )

        # Google button
        self.google_btn = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Image(src="/google.png", height=18),
                    ft.Text("Continue with Google", color=text_primary, size=15, weight=ft.FontWeight.W_500),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            height=52,
            width=360,
            bgcolor=white,
            border=ft.Border.all(1.5, divider_color),
            border_radius=14,
            shadow=ft.BoxShadow(
                blur_radius=8,
                spread_radius=0,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            on_click=self.google_signin_clicked
        )

        # main container w/ gradient background
        self.main_container = ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0.4, 1),
                colors=[deep_purple, mid_purple, "#1A0535"],
            ),
            alignment=ft.Alignment(0, 0),
            content=ft.Stack(
                controls=[
                    # decorative blobs
                    ft.Container(
                        width=300,
                        height=300,
                        border_radius=150,
                        bgcolor=ft.Colors.with_opacity(0.12, soft_purple),
                        left=-80,
                        top=-60,
                    ),
                    ft.Container(
                        width=200,
                        height=200,
                        border_radius=100,
                        bgcolor=ft.Colors.with_opacity(0.10, teal_accent),
                        right=-40,
                        bottom=100,
                    ),
                    ft.Container(
                        width=120,
                        height=120,
                        border_radius=60,
                        bgcolor=ft.Colors.with_opacity(0.15, orange_accent),
                        right=60,
                        top=80,
                    ),
                    # the card
                    ft.Container(
                        alignment=ft.Alignment(0, 0),
                        content=self.create_signup_card(),
                    ),
                ],
                expand=True,
            )
        )

        self.controls = [self.main_container]

    def create_signup_card(self):
        return ft.Container(
            bgcolor=card_bg,
            width=480,
            padding=ft.Padding.only(top=36, left=40, right=40, bottom=40),
            border_radius=28,
            shadow=ft.BoxShadow(
                blur_radius=60,
                spread_radius=0,
                color=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
                offset=ft.Offset(0, 20),
            ),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                tight=True,
                controls=[
                    # top row: back btn
                    ft.Row([
                        self.back_btn,
                        ft.Container(expand=True),
                    ]),

                    # logo
                    ft.Container(
                        content=ft.Image(src="/logo_black.png", width=84),
                        margin=ft.Margin.only(top=8, bottom=4),
                    ),

                    # heading
                    ft.Text(
                        "Create your account",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=text_primary,
                    ),
                    ft.Container(
                        content=ft.Text(
                            "Start your learning journey today",
                            size=14,
                            color=text_secondary,
                        ),
                        margin=ft.Margin.only(top=2, bottom=20),
                    ),

                    # name row
                    ft.Container(
                        content=ft.Row(
                            controls=[self.firstname_field, self.lastname_field],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            width=360,
                        ),
                        width=360,
                    ),
                    ft.Container(height=10),
                    self.email_field,
                    ft.Container(height=10),
                    self.password_field,

                    # error message
                    ft.Container(
                        content=self.shared_error,
                        margin=ft.Margin.only(top=8, bottom=4),
                    ),

                    self.submit_btn,

                    # divider
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Divider(thickness=1, color=divider_color, expand=True),
                                ft.Container(
                                    content=ft.Text("or", color=label_color, size=12),
                                    margin=ft.Margin.symmetric(horizontal=12, vertical=0),
                                ),
                                ft.Divider(thickness=1, color=divider_color, expand=True),
                            ],
                            width=360,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        margin=ft.Margin.symmetric(vertical=14),
                    ),

                    self.google_btn,

                    # log in row
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text("Already have an account?", size=13, color=text_secondary),
                                ft.TextButton(
                                    "Log in",
                                    on_click=lambda _: self.page.go("/login"),
                                    style=ft.ButtonStyle(
                                        color=mid_purple,
                                        padding=ft.Padding.all(0),
                                        overlay_color=ft.Colors.TRANSPARENT,
                                        text_style=ft.TextStyle(
                                            weight=ft.FontWeight.W_600,
                                            size=13,
                                        ),
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=2,
                        ),
                        margin=ft.Margin.only(top=12),
                    ),
                ]
            )
        )

    def submit_clicked(self, e):
        # 1. Reset everything
        fields = [self.firstname_field, self.lastname_field, self.email_field, self.password_field]
        for f in fields:
            f.border_color = None

        self.shared_error.visible = False
        empty_fields = False
        valid_email = True

        # 2. Check for empty fields
        for f in fields:
            if not f.value or f.value.strip() == "":
                f.border_color = orange_accent
                empty_fields = True

        # 3. Check email format
        email_val = self.email_field.value.strip()
        if email_val and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email_val):
            self.email_field.border_color = orange_accent
            valid_email = False

        # 4. Determine the shared message
        if empty_fields:
            self.shared_error.value = "Please fill in all required fields."
            self.shared_error.visible = True
        elif not valid_email:
            self.shared_error.value = "Please enter a valid email address."
            self.shared_error.visible = True

        self.page.update()

        if not empty_fields and valid_email:
            # Trigger loading UI
            self.submit_btn.content = ft.Row([
                ft.ProgressRing(width=18, height=18, color=white, stroke_width=2),
                ft.Text("Creating account...", size=16, color=white, weight=ft.FontWeight.W_600)
            ], alignment=ft.MainAxisAlignment.CENTER)
            self.submit_btn.on_click = None
            self.page.update()

            email_val = self.email_field.value.strip()
            password_val = self.password_field.value

            try:
                response = requests.post(
                    "http://localhost:8000/auth/register",
                    json={
                        "first_name": self.firstname_field.value,
                        "last_name": self.lastname_field.value,
                        "email": email_val,
                        "password": password_val
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    token = data.get("token")

                    if token:
                        self.page.client_storage.set("auth_token", token)

                    print("Success! Redirecting to chat...")
                    self.page.go("/chat")

                else:
                    error_data = response.json()
                    self.shared_error.value = error_data.get("detail", "Registration failed.")
                    self.shared_error.visible = True

                    # Revert UI
                    self.submit_btn.content = ft.Text("Create account", size=16, color=white, weight=ft.FontWeight.W_600)
                    self.submit_btn.on_click = self.submit_clicked
                    self.page.update()

            except requests.exceptions.ConnectionError:
                self.shared_error.value = "Cannot connect to server. Is the backend running?"
                self.shared_error.visible = True

                # Revert UI
                self.submit_btn.content = ft.Text("Create account", size=16, color=white, weight=ft.FontWeight.W_600)
                self.submit_btn.on_click = self.submit_clicked
                self.page.update()

    async def google_signin_clicked(self, e):
        # Trigger loading UI for Google Button
        self.google_btn.content = ft.Row([
            ft.ProgressRing(width=18, height=18, color=mid_purple, stroke_width=2),
            ft.Text("Redirecting...", color=text_primary, size=15, weight=ft.FontWeight.W_500)
        ], alignment=ft.MainAxisAlignment.CENTER)
        self.google_btn.disabled = True
        self.page.update()

        try:
            response = supabase_auth.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": "http://localhost:8080/login"  # Change this when deploying!
                }
            })

            # PKCE Fix
            verifier = supabase_auth.auth._storage.get_item("supabase.auth.token-code-verifier")
            if verifier:
                self.page.client_storage.set("pkce_verifier", verifier)

            if hasattr(response, "url") and response.url:
                await self.page.launch_url(
                    ft.Url(url=response.url, target=ft.UrlTarget.SELF)
                )
            else:
                self.shared_error.value = "Failed to initiate Google Authentication."
                self.shared_error.visible = True

                # Revert UI
                self.google_btn.content = ft.Row([
                    ft.Image(src="/google.png", height=18),
                    ft.Text("Continue with Google", color=text_primary, size=15, weight=ft.FontWeight.W_500),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
                self.google_btn.disabled = False
                self.page.update()

        except Exception as ex:
            self.shared_error.value = f"Error: {str(ex)}"
            self.shared_error.visible = True

            # Revert UI
            self.google_btn.content = ft.Row([
                ft.Image(src="/google.png", height=18),
                ft.Text("Continue with Google", color=text_primary, size=15, weight=ft.FontWeight.W_500),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
            self.google_btn.disabled = False
            self.page.update()