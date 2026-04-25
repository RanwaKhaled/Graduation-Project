# frontend/pages/new_pass.py
# this page will be accessed from the reset password link sent to the user's email
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
lilac = "#F4E6FF"

class NewPassPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/new_pass",
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

        # password reset message
        self.message = ft.Text(
            "Password reset successfully.",
            size=14,
            width=350,
            color=purple,
            visible=False,
        )
        # password field
        self.password_field = ft.TextField(
                        label="Password",
                        password=True,
                        can_reveal_password=True,
                        bgcolor=lightgrey,
                        color=grey,
                        width=350,
                        border=ft.Border.all(0),
                        prefix_icon=ft.Icons.PASSWORD,
                    )

        # shared error message
        self.shared_error = ft.Text("", color="red", size=14, visible=False)

        # main container w/ gradient background
        self.main_container = ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0,-1),
                end=ft.Alignment(0,1),
                colors=[lilac, purple],
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
                    ft.Text("Change Pasword", size=40, weight="bold", color=darkgrey),
                    self.message,

                    # text fields
                    # textfield for password
                    self.password_field,
                    self.shared_error,
                    # reset pass button
                    ft.Button(
                        ft.Text("Reset Password", size=20),
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
        fields = [self.password_field]
        for f in fields:
            f.border_color = None
        
        self.shared_error.visible = False
        empty_fields = False

        # 2. Check for empty fields
        for f in fields:
            if not f.value or f.value.strip() == "":
                f.border_color = "red"
                empty_fields = True

        # 4. Determine the shared message
        if empty_fields:
            self.shared_error.value = "Please fill in all required fields."
            self.shared_error.visible = True

        self.page.update()

        if not empty_fields:
            self.message.visible = True
            self.page.update()
            # password reset logic (empty for now) for the backend people to put  
            print("Success! Proceeding to reset logic...")
