# frontend/pages/chat.py
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
lilac="#F4E6FF"


class SignupPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/signup",
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


        # First Name field
        self.firstname_field = ft.TextField(
            label="First Name",
            bgcolor=lightgrey, 
            color=grey,
            width=170,
            border=ft.Border.all(0)
        )

        # Last Name field
        self.lastname_field = ft.TextField(
            label="Last Name",
            bgcolor=lightgrey, 
            color=grey,
            width=170,
            border=ft.Border.all(0)
        )

        # email field
        self.email_field = ft.TextField(label="Email", 
                                 bgcolor=lightgrey, 
                                 color=grey,
                                 width=350,
                                 border=ft.Border.all(0),
                                 prefix_icon=ft.Icons.EMAIL,
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
            content=self.create_signup_card()
        )
        

        # add the components to the page
        self.controls = [self.main_container]

    def create_signup_card(self):
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
                spacing=10,
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
                    ft.Text("Sign Up", size=40, weight="bold", color=darkgrey),
                    # text fields
                    ft.Row(
                        width=350,
                        controls=[self.firstname_field, self.lastname_field],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    # textfield for email
                    self.email_field,
                    # password with reveal button
                    self.password_field,
                    self.shared_error,
                    # sign up button
                    ft.Button(
                        ft.Text("Sign up", size=20),
                        bgcolor=darkgrey,
                        color=ft.Colors.WHITE,
                        height=40,
                        width=350,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                        # signup authentication logic should be called here
                        on_click= self.submit_clicked
                    ),
                    # or divider
                    ft.Row(
                        controls=[
                            ft.Divider(thickness=1, color=lightgrey, expand=True),
                            ft.Text("  Or  ", color=grey, size=13),
                            ft.Divider(thickness=1, color=lightgrey, expand=True),
                        ],
                        width=350,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    # signup w/ google button
                    ft.Container(ft.Row(
                        controls=[
                            ft.Image(src="/google.png", height=20),
                            ft.Text("Sign up with Google", color=darkgrey, size=20),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,   
                    ),
                    height=40,
                    width=350,
                    bgcolor=white,
                    border=ft.Border.all(1, darkgrey),
                    border_radius=10,
                    ),
                    # prompt to sign up if you have an account
                    ft.Row(
                        controls=[
                            ft.Text("Already have an account?", size=14, color=grey),
                            ft.TextButton(
                                "Log in",
                                on_click=lambda _: self.page.go("/login"),
                                style=ft.ButtonStyle(
                                    color=purple,
                                    padding=ft.Padding.all(0),
                                    text_style=ft.TextStyle(weight=ft.FontWeight.BOLD)
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=4,
                    ),
                ]
            )
        )
    
    # function to submit user credentials
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
            print("Success! Proceeding to backend...")
            # sign up logic call from backend