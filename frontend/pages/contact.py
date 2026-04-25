# frontend/pages/chat.py
import flet as ft

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

class ContactPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/contact",
                         padding=0,
                         spacing=0,
                         bgcolor=white)

        # page elements
        # navigation bar
        # 1. navigation links
        nav_links = ft.Row(
            controls=[
                ft.TextButton(content=ft.Text("Home", size=22), 
                              style=ft.ButtonStyle(color=ft.Colors.WHITE),
                              on_click=lambda e: page.go("/")),
                ft.TextButton(content=ft.Text("Features", size=22), 
                              style=ft.ButtonStyle(color=ft.Colors.WHITE),
                              on_click=lambda e: page.go("/"),
                              ),
                ft.TextButton(content=ft.Text("Contact Us", size=22), 
                              style=ft.ButtonStyle(color=ft.Colors.WHITE),
                              on_click=lambda e: page.go("/contact")
                              ),
            ],
            alignment=ft.MainAxisAlignment.START,
        )
        # 2. authentication buttons on top right
        auth_buttons = ft.Row(
            controls=[
                ft.TextButton(content=ft.Text("Log In", size=22), 
                              style=ft.ButtonStyle(color=ft.Colors.WHITE),
                              on_click=lambda e: page.go("/login")),
                ft.Button(content=ft.Text("Sign Up", size=22),
                            bgcolor=orange,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                            on_click=lambda e: page.go("/signup"))
            ]
        )
        # 3. assembling nav bar
        self.header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(width=50),  # transparent divider
                    ft.Container(height=90, content=ft.Image(src="/logo_white.png", fit= ft.BoxFit.CONTAIN)),
                    ft.Container(width=20),  # transparent divider
                    ft.Container(content=nav_links, expand=True),
                    auth_buttons
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            bgcolor=purple,
            padding= ft.Padding.symmetric(vertical=10, horizontal=20),
            height=70,
        )

        # error message
        self.contact_error = ft.Text("", color="red", size=13, visible=False)

        # container with the contact form on the right side
        self.contact_form = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Text("Get in Touch", size=36, weight=ft.FontWeight.BOLD, color=black),
                ft.Text("Got a technical issue? Want to send feedback about a feature? Let us know.", 
                        width=400, size=16, color=black),

                # email field
                ft.Text("Email", size=14, weight=ft.FontWeight.BOLD, color=black),
                ft.TextField(hint_text="Email address", 
                             text_size=14,
                             width=400,
                             bgcolor=lightgrey, 
                             border_radius=10, 
                             height=42, 
                             content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                             border_color=ft.Colors.TRANSPARENT),
                
                # Subject Field
                ft.Text("Subject", size=14, weight=ft.FontWeight.BOLD, color=black),
                ft.TextField(hint_text="Let us know how we can help you", 
                             text_size=14,
                             width=400,
                             bgcolor=lightgrey, 
                             border_radius=10, 
                             height=42, 
                             content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                             border_color=ft.Colors.TRANSPARENT),
                
                # Description Field
                ft.Text("Full description", size=14, weight=ft.FontWeight.BOLD, color=black),
                ft.TextField(
                    hint_text="Include as much detail as you can", 
                    text_size=14,
                    width=400,
                    bgcolor=lightgrey, 
                    border_radius=10, 
                    border_color=ft.Colors.TRANSPARENT,
                    multiline=True,
                    min_lines=4,
                    max_lines=4,  # cap it so it doesn't grow
                    content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                ),
                
                ft.Text(
                    r"You can include files by uploading them to any third-party file sharing service such as Google Drive, Microsoft OneDrive or similar . Please make sure the correct sharing permissions have been sets. All files sent to us are 100% confidential.",
                    size=10, color=darkgrey,
                    width=400,
                ),
                # send buttton and error message
                ft.Row(
                    controls=[
                        ft.Button(
                            content=ft.Text("Send", color=white, size=18),
                            bgcolor=orange,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                            width=120,
                            height=45,
                            on_click=self.send_message
                        ),
                        self.contact_error,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                )
            ]
        )

        # assemble left and right parts
        self.main_container = ft.Container(
            expand=True,
            padding=ft.Padding.symmetric(vertical=20, horizontal=60),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=50,
                controls=[
                    ft.Container(
                        content=ft.Image(src="/phone.png", fit=ft.BoxFit.CONTAIN),
                        expand=1,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    ),
                    ft.Container(content=self.contact_form,
                                 expand=1,
                                 padding=ft.Padding.only(right=40))
                ]
            )
        )

        # making the footer
        self.footer = ft.Container(
            bgcolor=purple,
            padding=ft.Padding.symmetric(vertical=15, horizontal=50),
            content=ft.Row(
                controls=[
                    ft.Image(src="/logo_white.png", height=50, fit=ft.BoxFit.CONTAIN),
                    ft.Text("\u00A9 2026 Yosr. All rights reserved.",
                            color=ft.Colors.WHITE,
                            size=14,
                            ), 
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        
        self.controls = [
            self.header,
            self.main_container,
            self.footer,
        ]
    
    def send_message(self, e): 
        # grab refs to the text fields
        fields = self.contact_form.controls
        email_field    = fields[3]   # index based on your controls list
        subject_field  = fields[5]
        desc_field     = fields[7]

        # reset borders
        for f in [email_field, subject_field, desc_field]:
            f.border_color = ft.Colors.TRANSPARENT

        self.contact_error.visible = False

        empty = False
        valid_email = True

        # check empty
        for f in [email_field, subject_field, desc_field]:
            if not f.value or f.value.strip() == "":
                f.border_color = "red"
                empty = True

        # check email format
        import re
        email_val = email_field.value.strip() if email_field.value else ""
        if email_val and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email_val):
            email_field.border_color = "red"
            valid_email = False

        if empty:
            self.contact_error.value = "Please fill in all fields."
            self.contact_error.visible = True
        elif not valid_email:
            self.contact_error.value = "Please enter a valid email."
            self.contact_error.visible = True

        self.page.update()

        if not empty and valid_email:
            # reset the fields
            email_field.value = ""
            subject_field.value = ""
            desc_field.value = ""
            self.page.update()
            # backend send logic here
            print("Message sent!")
            pass