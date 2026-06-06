# frontend/pages/reset_pass.py
import flet as ft
import re
import requests

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

class ResetPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/reset", padding=0, bgcolor=deep_purple)

        # the back button (goes back to login)
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

        # message prompting email entry for reset
        self.reset_prompt = ft.Text(
            "Enter your account email and we'll send a password reset link.",
            size=14,
            color=text_secondary,
            width=360,
            text_align=ft.TextAlign.CENTER,
        )

        # success confirmation container
        self.message = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.MARK_EMAIL_READ_OUTLINED, color=mid_purple, size=18),
                    ft.Text(
                        "If an account exists for that email, we sent a reset link. Check your inbox.",
                        size=13,
                        color=mid_purple,
                        expand=True,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            bgcolor=ft.Colors.with_opacity(0.08, mid_purple),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, mid_purple)),
            border_radius=12,
            padding=ft.Padding.all(14),
            width=360,
            visible=False,
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

        # shared error message
        self.shared_error = ft.Text("", color=orange_accent, size=13, visible=False)

        # Submit button — gradient style matching login.py
        self.submit_btn_text = ft.Text("Send reset instructions", size=16, color=white, weight=ft.FontWeight.W_600)
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
                        content=self.create_reset_card(),
                    ),
                ],
                expand=True,
            )
        )

        self.controls = [self.main_container]

    def create_reset_card(self):
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
                        "Reset your password",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=text_primary,
                    ),
                    ft.Container(
                        content=self.reset_prompt,
                        margin=ft.Margin.only(top=6, bottom=20),
                    ),

                    self.message,
                    ft.Container(height=4),

                    self.email_field,

                    # error message
                    ft.Container(
                        content=self.shared_error,
                        margin=ft.Margin.only(top=8, bottom=4),
                    ),

                    self.submit_btn,

                    # back to login
                    ft.Container(
                        content=ft.TextButton(
                            "Back to login",
                            on_click=lambda _: self.page.go("/login"),
                            style=ft.ButtonStyle(
                                color={
                                    ft.ControlState.HOVERED: mid_purple,
                                    ft.ControlState.DEFAULT: soft_purple,
                                },
                                text_style=ft.TextStyle(size=13, weight=ft.FontWeight.W_500),
                                padding=ft.Padding.all(0),
                                overlay_color=ft.Colors.TRANSPARENT,
                            ),
                        ),
                        margin=ft.Margin.only(top=14),
                    ),
                ]
            )
        )

    def submit_clicked(self, e):
        # 1. Reset everything
        self.email_field.border_color = None
        self.shared_error.visible = False
        empty_fields = False
        valid_email = True

        # 2. Check for empty fields
        if not self.email_field.value or self.email_field.value.strip() == "":
            self.email_field.border_color = orange_accent
            empty_fields = True

        # 3. Check email format
        email_val = self.email_field.value.strip() if self.email_field.value else ""
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

        # 5. Live Backend Connection
        if not empty_fields and valid_email:
            # Trigger loading UI
            self.submit_btn.content = ft.Row([
                ft.ProgressRing(width=18, height=18, color=white, stroke_width=2),
                ft.Text("Sending...", size=16, color=white, weight=ft.FontWeight.W_600)
            ], alignment=ft.MainAxisAlignment.CENTER)
            self.submit_btn.on_click = None
            self.page.update()

            try:
                response = requests.post(
                    "http://localhost:8000/auth/forgot-password",
                    json={"email": email_val}
                )

                if response.status_code == 200:
                    self.reset_prompt.visible = False
                    self.message.visible = True
                    self.email_field.value = ""
                    # Revert btn to normal (can resend)
                    self.submit_btn.content = ft.Text("Send reset instructions", size=16, color=white, weight=ft.FontWeight.W_600)
                    self.submit_btn.on_click = self.submit_clicked
                    self.page.update()
                else:
                    error_data = response.json()
                    self.shared_error.value = error_data.get("detail", "Failed to send reset link.")
                    self.shared_error.visible = True

                    self.submit_btn.content = ft.Text("Send reset instructions", size=16, color=white, weight=ft.FontWeight.W_600)
                    self.submit_btn.on_click = self.submit_clicked
                    self.page.update()

            except requests.exceptions.ConnectionError:
                self.shared_error.value = "Cannot connect to server. Is the backend running?"
                self.shared_error.visible = True

                self.submit_btn.content = ft.Text("Send reset instructions", size=16, color=white, weight=ft.FontWeight.W_600)
                self.submit_btn.on_click = self.submit_clicked
                self.page.update()