# frontend/pages/chat.py
import flet as ft
import requests
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
babypurple = "#FBF7FF"
lightpurple = "#EADAF8"

class ContactPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/contact",
                         padding=0,
                         spacing=0,
                         bgcolor=babypurple)
        
        self.scroll = ft.ScrollMode.AUTO

        # page elements
        # navigation bar
        # 1. navigation links
        nav_links = ft.Row(
            controls=[
                ft.TextButton(content=ft.Text("Home", size=18, weight=ft.FontWeight.BOLD), 
                              style=ft.ButtonStyle(color=purple),
                              on_click=lambda e: page.go("/")),
                ft.TextButton(content=ft.Text("How It Works", size=18, weight=ft.FontWeight.BOLD), 
                              style=ft.ButtonStyle(color=purple),
                              on_click=lambda e: page.go("/")),
                ft.TextButton(content=ft.Text("Features", size=18, weight=ft.FontWeight.BOLD), 
                              style=ft.ButtonStyle(color=purple),
                              on_click=lambda e: page.go("/")
                              ),
                ft.TextButton(content=ft.Text("Contact Us", size=18, weight=ft.FontWeight.BOLD), 
                              style=ft.ButtonStyle(color=purple),
                              on_click=lambda e: page.go("/contact")
                              ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        # 2. authentication buttons on top right
        auth_buttons = ft.Row(
            controls=[
                ft.OutlinedButton(
                    content=ft.Text("Log In", size=16, weight=ft.FontWeight.BOLD),  # You can use the simple text property here
                    style=ft.ButtonStyle(
                        color=purple,  # Colors the text
                        shape=ft.RoundedRectangleBorder(radius=5),
                        side=ft.BorderSide(width=1, color=purple), # Colors the border
                    ),
                    on_click=lambda e: page.go("/login"),
                ),
                ft.Button(content=ft.Text("Sign Up", size=16, weight=ft.FontWeight.BOLD),
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=5),
                                bgcolor=orange,
                                color=ft.Colors.WHITE),
                            on_click=lambda e: page.go("/signup")
                        )
            ]
        )
        # 3. assembling nav bar
        self.header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(height=80, 
                                 content=ft.Image(src="/logo_black.png", fit= ft.BoxFit.CONTAIN)),
                    ft.Container(content=nav_links, 
                                 expand=True,
                                 alignment=ft.Alignment.CENTER),
                    auth_buttons
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment= ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=white,
            padding= ft.Padding.symmetric(vertical=10, horizontal=40),
            height=80,
        )

        # error message
        self.contact_error = ft.Text("", color="red", size=13, visible=False)

        # container with the contact form on the right side
        self.contact_form = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
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

        # white card for the form
        self.righ_card = ft.Container(
            content=self.contact_form,
            bgcolor=white,
            padding=40,
            border_radius=24,
            shadow=ft.BoxShadow(
                blur_radius=30,
                color=ft.Colors.with_opacity(0.1, black),
                offset=ft.Offset(0,10),
            )
        ) 

        # left part (headers + info rows)
        def create_info_row(icon_name, title, description):
            return ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                controls=[
                    ft.Container(
                        content=ft.Icon(icon_name, color=purple, size=28),
                        bgcolor=lightpurple,
                        shape=ft.BoxShape.CIRCLE,
                        width=50,
                        height=50,
                        alignment=ft.Alignment.CENTER
                    ),
                    ft.Column(
                        spacing=2,
                        width=300,
                        controls=[
                            ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=black),
                            ft.Text(description, size=14, color=black, no_wrap=False)
                        ]
                    )
                ]
            )
        self.info_rows = ft.Column(
            spacing=25,
            controls=[
                create_info_row(ft.CupertinoIcons.ENVELOPE,"We reply fast", "Our team typically responds within 24 hours"),
                create_info_row(ft.CupertinoIcons.LOCK_SHIELD, "Your data is safe", "We take your privacy seriously and keep your information secure"),
                create_info_row(ft.CupertinoIcons.HEART, "We're here to help", "Whether it's a question or feedback, we'd love to hear from you"),
            ]
        )

        self.left_column = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=15,
            width=350,
            controls=[
                ft.Text("Get in Touch", size=36, weight=ft.FontWeight.BOLD, color=black),
                ft.Text("Got a technical issue? Want to send feedback about a feature? Let us know.", 
                        width=400, size=16, color=black),
                ft.Container(bgcolor=purple, width=50, height=3, border_radius=2),
                #ft.Container(height=10), # Spacer
                self.info_rows,
            ]
        )

        # bg img layer
        self.bg_img = ft.Image(
            src="/bg1.svg",
            fit=ft.BoxFit.COVER,
            expand=True
        )

        # assemble left and right parts
        self.main_container = ft.Container(
            expand=True,
            padding=ft.Padding.symmetric(vertical=60, horizontal=80),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=100,
                controls=[
                    self.left_column,
                    self.righ_card,
                ]
            )
        )

        # making the footer
        self.footer = ft.Container(
            bgcolor=purple,
            padding=ft.Padding.symmetric(vertical=20, horizontal=50),
            content=ft.Column(
                controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content= ft.Row(
                                        controls=[
                                            ft.Image(src="/logo_white.png", height=80, fit=ft.BoxFit.CONTAIN),
                                            ft.Text("Your AI learning assistant that turns \nlectures into understanding.",
                                                    color=ft.Colors.WHITE,
                                                    size=16,
                                                    )
                                                ],
                                        spacing=20
                                        ),
                                    ), 
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.GestureDetector(
                                                on_tap=lambda _: self.page.go("/"),
                                                content=ft.Container(
                                                    content=ft.Text("Product", size=16, color=white, weight=ft.FontWeight.BOLD),
                                                    padding=ft.Padding.only(top=1, bottom=1),
                                                )
                                            ),
                                            ft.GestureDetector(
                                                mouse_cursor=ft.MouseCursor.CLICK,
                                                on_tap=lambda _: self.page.go("/"),
                                                content=ft.Container(
                                                    content=ft.Text("Home", size=16, color=white),
                                                    padding=ft.Padding.only(top=1, bottom=1),
                                                )
                                            ),
                                            ft.GestureDetector(
                                                mouse_cursor=ft.MouseCursor.CLICK,
                                                on_tap=lambda _: self.page.go("/"),
                                                content=ft.Container(
                                                    content=ft.Text("How It Works", size=16, color=white),
                                                    padding=ft.Padding.only(top=1, bottom=1),
                                                )
                                            ),
                                            ft.GestureDetector(
                                                mouse_cursor=ft.MouseCursor.CLICK,
                                                on_tap=lambda _: self.page.go("/"),
                                                content=ft.Container(
                                                    content=ft.Text("Features", size=16, color=white),
                                                    padding=ft.Padding.only(top=1, bottom=1),
                                                )
                                            ),
                                            ft.GestureDetector(
                                                mouse_cursor=ft.MouseCursor.CLICK,
                                                on_tap=lambda _: self.page.go("/contact"),
                                                content=ft.Container(
                                                    content=ft.Text("Contact", size=16, color=white),
                                                    padding=ft.Padding.only(top=1, bottom=1),
                                                )
                                            ),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.START
                                        ),
                                )
                            ],
                            spacing=300,
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Divider(),
                        ft.Text("\u00A9 2026 Yosr. All rights reserved.",
                                        color=ft.Colors.WHITE,
                                        size=16,
                                        ), 
                    
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
        )
        

        # Assemble the UI components into a single column layer
        main_content_layer = ft.Column(
            controls=[
                self.header,
                self.main_container,
                self.footer,
            ],
            spacing=0,
            expand=True,
        )

        # Use a Stack to overlay the text/form content layer over your SVG background image
        self.controls = [
            ft.Stack(
                expand=True,
                controls=[
                    self.bg_img,         # Bottom layer (Background shapes)
                    main_content_layer,  # Top layer (Header, forms, footer)
                ]
            )
        ]
    
    def send_message(self, e): 
    
        # grab refs to the text fields
        fields = self.contact_form.controls
        email_field    = fields[1]   # index based on your controls list
        subject_field  = fields[3]
        desc_field     = fields[5]

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
        email_val = email_field.value.strip() if email_field.value else ""
        if email_val and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email_val):
            email_field.border_color = "red"
            valid_email = False

        if empty:
            self.contact_error.value = "Please fill in all fields."
            self.contact_error.visible = True
            self.contact_error.color = "red"
        elif not valid_email:
            self.contact_error.value = "Please enter a valid email."
            self.contact_error.visible = True
            self.contact_error.color = "red"

        self.page.update()

        # --- THE BACKEND CONNECTION ---
        if not empty and valid_email:
            try:
                # 1. Show a loading state so the user knows it's working
                self.contact_error.value = "Sending message..."
                self.contact_error.color = "blue"
                self.contact_error.visible = True
                self.page.update()

                # 2. Send data to the FastAPI backend
                # Mapping your 'subject' and 'desc' UI fields to the 'name' and 'message' backend variables
                response = requests.post(
                    "http://localhost:8000/contact/send",
                    json={
                        "name": subject_field.value.strip(), 
                        "email": email_val,
                        "message": desc_field.value.strip()
                    }
                )
                
                # 3. Handle the response
                if response.status_code == 200:
                    # Success! Clear the fields
                    email_field.value = ""
                    subject_field.value = ""
                    desc_field.value = ""
                    
                    self.contact_error.value = "Message sent successfully!"
                    self.contact_error.color = "green"
                    self.page.update()
                    print("Success! Message saved to Supabase.")
                else:
                    # Backend rejected it
                    error_data = response.json()
                    self.contact_error.value = error_data.get("detail", "Failed to send message.")
                    self.contact_error.color = "red"
                    self.page.update()
                    
            except requests.exceptions.ConnectionError:
                self.contact_error.value = "Cannot connect to server. Is the backend running?"
                self.contact_error.color = "red"
                self.page.update()