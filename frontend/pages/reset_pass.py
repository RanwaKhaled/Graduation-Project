# frontend/pages/reset_pass.py
import flet as ft
import re

# colors: global vars
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
lilac = "#ECDCF9"

class ResetPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/reset",
                         padding=0,
                         bgcolor=purple)
        
        # the back button (goes back home)
        self.back_btn=ft.Container(
            content=ft.Icon(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, 
                            color=darkgrey, 
                            size=20),
                            bgcolor=lightgrey,
                            width=50,
                            height=50,
                            border_radius=12,
                            on_click=lambda _: page.go("/")
        )

        # message prompting email entry for reset
        self.reset_prompt = ft.Text("Enter your account email and we’ll send a password reset link.",
                            size=14,
                            color=black,
                            width=350)

        # message confirming that email was sent
        self.message = ft.Container(
            content=ft.Text("If an account exists for that email, we sent a reset password link. Check your inbox.",
                            size=14),
            bgcolor=lilac,
            visible=False,
            width=350,
        )

        # email field
        self.email_field = ft.TextField(label="Email", 
                                 bgcolor=lightgrey, 
                                 color=grey,
                                 width=350,
                                 border=ft.Border.all(0),
                                 prefix_icon=ft.Icons.EMAIL,
                                )
        # shared error message
        self.shared_error = ft.Text("", color="red", size=14, visible=False)
        
        # main container w/ gradient background
        self.main_container = ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0,-1),
                end=ft.Alignment(0,1),
                colors=[white, purple],
            ),
            alignment=ft.Alignment(0,0),
            content=self.create_login_card()
        )
        

        # add the components to the page
        self.controls = [self.main_container]

    def create_login_card(self):
        # the white card 
        return ft.Container(
            clip_behavior=ft.ClipBehavior.NONE,
            bgcolor=white,
            width=500,
            height=600,
            padding=ft.Padding.only(top=40, left=30, right=30, bottom=40), # Added top padding for logo space,
            border_radius=40,
            shadow=ft.BoxShadow(
                blur_radius=20,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                ),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    ft.Row([
                        # back button
                            self.back_btn,
                            ft.Container(expand=True),
                        ]),
                    ft.Container(
                        content=ft.Image(src="/logo_black.png", width=120),
                        margin=ft.Margin.only(top=-80), 
                    ),
                    # title
                    ft.Text("Reset Your Pasword", size=40, weight="bold", color=darkgrey),
                    self.reset_prompt,
                    self.message,
                    # text fields
                    # textfield for email
                    self.email_field,
                    self.shared_error,
                    # send reset pass email button
                    ft.Button(
                        ft.Text("Send Reset Instructions", size=20),
                        bgcolor=darkgrey,
                        color=ft.Colors.WHITE,
                        height=40,
                        width=350,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                        # login authentication logic should be called here
                        on_click= self.submit_clicked
                    ),
                    # back to login
                    ft.TextButton(
                        "Back to Login",
                        on_click=lambda _: self.page.go("/login"),
                        style=ft.ButtonStyle(
                            color=grey,
                            padding=ft.Padding.all(0),
                            text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
                        ),
                    ),
                ]
            )
        )
    
    def submit_clicked(self, e):
        # 1. Reset everything
        fields = [self.email_field]
        for f in fields:
            f.border_color = None
        
        self.shared_error.visible = False
        empty_fields = False
        valid_email = True

        # 2. Check for empty fields
        for f in fields:
            if not f.value or f.value.strip() == "":
                f.border_color = "red"
                empty_fields = True

        # 3. Check email format (only if email isn't already empty)
        email_val = self.email_field.value.strip()
        if email_val and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email_val):
            self.email_field.border_color = "red"
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
            # show email sent message
            self.reset_prompt.visible=False  # hide prompt
            self.message.visible=True  # show email sent message
            self.email_field.value = ""  # reset email field
            self.page.update()
            # password reset logic (empty for now) for the backend people to put  
            print("Success! Proceeding to reset logic...")

