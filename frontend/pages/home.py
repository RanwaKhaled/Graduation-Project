# frontend/pages/home.py
import flet as ft
import time
import asyncio
import threading

# colors: global vars
purple = "#450A75"
blue = "#E4FAFD"
babypink = "#FFEFF3"
pink = "#F0A4BF"
orange = "#F75C2D"
lightgrey = "#EBEBEB"
grey = "#7D7D7D"
darkgrey = "#2D2D2D"
babypurple = "#FBF7FF"
lightpurple = "#EADAF8"
white="#FFFFFF"
black = "#000000"

class HomePage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/",
                         padding = 0,
                         spacing=0,
                         bgcolor=ft.Colors.WHITE,
                        )
        
        self.scroll = ft.ScrollMode.AUTO
        
        # helper functions
        # function to go to how it works
        async def scroll_to_how(e):
            try:
                await self.scroll_to(
                    offset=650,  # approximate pixel offset — adjust this number to match your header + intro height
                    duration=1000,
                    curve=ft.AnimationCurve.DECELERATE,
                )
            except Exception as ex:
                print(f"Scroll failed: {ex}")
        
        # function to go to features
        async def scroll_to_features(e):
            try:
                await self.scroll_to(
                    offset=950,  # approximate pixel offset — adjust this number to match your header + intro height
                    duration=1000,
                    curve=ft.AnimationCurve.DECELERATE,
                )
            except Exception as ex:
                print(f"Scroll failed: {ex}")

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
                              on_click=scroll_to_how),
                ft.TextButton(content=ft.Text("Features", size=18, weight=ft.FontWeight.BOLD), 
                              style=ft.ButtonStyle(color=purple),
                              on_click=scroll_to_features
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

        # AI label
        self.ai_label = ft.TextButton(
            icon=ft.Icon(ft.CupertinoIcons.SPARKLES, size=25, color=purple),
            icon_color=purple,
            content=ft.Text("AI-Powered Learning Assistant", 
                            weight=ft.FontWeight.BOLD, 
                            size=12, 
                            color=purple),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10),
                                 bgcolor=lightpurple)                   
        )

        # intro slogan
        self.slogans = ft.Column(
            controls=[
                self.ai_label,
                ft.Text("Turn Any Lecture Into Audio Explanations & Smart Notes",
                        size=35,
                        weight='bold',
                        color=purple
                        ),
                ft.Text("Upload your slides and get high-quality audio explanations in Egyptian Arabic, smart summarize and practice questions in seconds.",
                        size=16,
                        color=ft.Colors.BLACK
                ),
                # advantages
                ft.Column(
                    controls=[
                        ft.TextButton(
                            icon=ft.CupertinoIcons.CHECKMARK_ALT_CIRCLE_FILL,
                            icon_color=purple,
                            content=ft.Text("Audio explanations in Egyptian Arabic",
                                            size=16, color=black),
                        ),
                        ft.TextButton(
                            icon=ft.CupertinoIcons.CHECKMARK_ALT_CIRCLE_FILL,
                            icon_color=purple,
                            content=ft.Text("Smart summaries of your content",
                                            size=16, color=black),
                        ),
                        ft.TextButton(
                            icon=ft.CupertinoIcons.CHECKMARK_ALT_CIRCLE_FILL,
                            icon_color=purple,
                            content=ft.Text("MCQ & Essay questions",
                                            size=16, color=black),
                        ),
                        ft.TextButton(
                            icon=ft.CupertinoIcons.CHECKMARK_ALT_CIRCLE_FILL,
                            icon_color=purple,
                            content=ft.Text("Downloadable study materials",
                                            size=16, color=black),
                        ),
                    ]
                ),
                ft.Button(
                    ft.Text("Get Started Today", size=20),
                    icon=ft.Icon(ft.CupertinoIcons.CLOUD_UPLOAD, size=30),
                    icon_color=white,
                    bgcolor=orange,
                    color=ft.Colors.WHITE,
                    height=50,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=15)),
                    on_click=lambda _: self.page.go("/signup")
                )
            ],
            spacing=20,
            expand=True
        )

        self.intro = ft.Container(
            ft.Row(
                controls=[
                    self.slogans,
                    ft.Container(
                                 expand=True, 
                                 content=ft.Image(src="/main_noside0.png", 
                                                  fit= ft.BoxFit.CONTAIN,
                                                  height=400,
                                                  ),
                                ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=babypurple,
            padding=ft.Padding.all(70),
            
        ) 

        # How it works section
        # helper function to create the step card
        def create_step_card(count, icon_name, title, description):
            return ft.Container(
                content=
                    ft.Row(
                    controls=[
                        # orange circle with number (count)
                        ft.Container(
                            margin=ft.Margin.only(top=4),
                            width=24,
                            height=24,
                            shape=ft.BoxShape.CIRCLE,
                            bgcolor=orange,
                            alignment=ft.Alignment(0,0),
                            content=ft.Text(str(count), color=white, size=14, weight='bold'),
                        ),
                        ft.Row(
                        controls=[    # container for the icon
                                ft.Container(
                                    content= ft.Icon(icon=icon_name, 
                                                    color=purple,
                                                    size=32),
                                    height=50,
                                    width=50,
                                    bgcolor=lightpurple,
                                    border_radius=8,
                                    alignment=ft.Alignment(0,0)
                                ),
                                # title and text
                                ft.Column(
                                    controls=[
                                        ft.Text(title, color=purple, size=18, weight="bold"),
                                        ft.Container(
                                            content= ft.Text(description, color=ft.Colors.BLACK, size=13, no_wrap=False),
                                            width=230,
                                            ),
                                    ],
                                    spacing=4,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                )],
                        spacing=15,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    )
                ,
                # alignment=ft.Alignment.CENTER,
                shadow=ft.BoxShadow(spread_radius=1, offset=(1,1), blur_radius=5, color=ft.Colors.with_opacity(0.15, black)),
                bgcolor=white,
                padding=20,
                border_radius=12,
            )
        
        # arrow helper
        def arrow():
            return ft.Container(
                content=ft.Icon(ft.Icons.ARROW_FORWARD, color=lightgrey, size=28),
                alignment=ft.Alignment(0,0),
                padding=ft.Padding.only(top=20),
            )
        
        # create step cards
        self.upload = create_step_card(1, ft.CupertinoIcons.CLOUD_UPLOAD, 
                                          "Upload Documents", 
                                          "Upload your lecture slides or documents in PDF, PPT or DOC")
        self.process = create_step_card(2, ft.CupertinoIcons.SPARKLES, 
                                          "AI Processing", 
                                          "Our AI generates audio explanations, summaries and questions")
        self.ready = create_step_card(3, ft.Icons.EDIT_DOCUMENT, 
                                          "Materials Ready", 
                                          "Listen, read, and download your study materials instantly")
        
        # Assemble the section
        self.steps = ft.Container(
                        key = "how it works",
                        padding=ft.Padding.symmetric(vertical=40, horizontal=50),
                        content=ft.Column(
                            controls=[
                                ft.Text("How It Works", size=30, weight="bold", color=purple),
                                ft.ResponsiveRow(
                                    controls=[
                                        # Assign the 'col' property to each card
                                        # This says: on desktop (large), take 4/12 (3 per row)
                                        # On mobile (small), take 12/12 (stack vertically)
                                        ft.Container(self.upload, col={"sm": 8, "md": 4, "lg": 3}),
                                        ft.Container(arrow(), col={"sm": 0, "md": 1, "lg": 1},
                                                    alignment=ft.Alignment(0, 0)),
                                        ft.Container(self.process, col={"sm": 8, "md": 4, "lg": 3}),
                                        ft.Container(arrow(), col={"sm": 0, "md": 1, "lg": 1},
                                                    alignment=ft.Alignment(0, 0)),
                                        ft.Container(self.ready, col={"sm": 8, "md": 4, "lg": 3}),
                                    ],
                                    spacing=5,
                                    run_spacing=30, # Vertical gap when they wrap
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                )
                            ],
                            spacing=40,
                            # alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    )
        
        # features part
        # helper function to create a feature card easily
        def create_feature_card(icon_path, title, description):
            return ft.Container(
                content=ft.Column(
                    controls=[
                        # Icon Container (The small rounded square for the image)
                        ft.Container(
                            content=ft.Container(
                                    content=ft.Image(src=icon_path, height=40, fit=ft.BoxFit.CONTAIN),
                                    alignment=ft.Alignment.CENTER # Keeps the image centered and honors its internal height
                                ),
                            bgcolor=lightpurple,
                            padding=5,
                            border_radius=10,
                            width=60,
                            height=60,
                        ),
                        ft.Text(title, color=purple, size=18, weight="bold"),
                        ft.Text(description, color=ft.Colors.BLACK, size=14),
                    ],
                    spacing=10,
                ),
                bgcolor=white,
                padding=30,
                border_radius=10, # Makes it look like the Figma
                width=150,        # Give cards a consistent width
                height=200,       # Give cards a consistent height
                shadow=ft.BoxShadow(spread_radius=1, offset=(1,1), blur_radius=5, color=ft.Colors.with_opacity(0.2, black))
            )

        # Create the three cards
        self.tts = create_feature_card(
            "/headphone.png", "Audio Explanations", "Listen to your lecture in Egyptian Arabic with our advanced TTS technology"
        )
        self.summarization = create_feature_card(
            "/contract.png", "Smart Summaries", "Get concise, accurate summaries that help you understand faster"
        )
        self.qa = create_feature_card(
            "/question.png", "MCQ & Essay Questions", "Practice with AI-generated questions to test your understanding"
        )
        self.download = create_feature_card(
            "/downloads.png", "Download & Study", "Download audio, transcripts, summaries and explanations for offline study."
        )

        # Assemble the section
        self.features = ft.Container(
                        key = "features_section",
                        padding=ft.Padding.symmetric(vertical=40, horizontal=50),
                        content=ft.Column(
                            controls=[
                                ft.Text("Powerful Features for Smarter Learning", size=30, weight="bold", color=purple),
                                ft.ResponsiveRow(
                                    controls=[
                                        # Assign the 'col' property to each card
                                        # This says: on desktop (large), take 4/12 (3 per row)
                                        # On mobile (small), take 12/12 (stack vertically)
                                        ft.Container(self.summarization, col={"sm": 10, "md": 6, "lg": 3}),
                                        ft.Container(self.tts, col={"sm": 10, "md": 6, "lg": 3}),
                                        ft.Container(self.qa, col={"sm": 10, "md": 6, "lg": 3}),
                                        ft.Container(self.download, col={"sm": 10, "md": 6, "lg": 3})
                                    ],
                                    spacing=50,
                                    run_spacing=30, # Vertical gap when they wrap
                                    alignment=ft.MainAxisAlignment.CENTER,
                                )
                            ],
                            spacing=40,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    )
        

        # in action carousel
        # See It In Action Section
        self.in_action = ft.Container(
            padding=ft.Padding.symmetric(vertical=40, horizontal=50),
            content=ft.Column(
                controls=[
                    # Title
                    ft.Text(
                        "See It In Action", 
                        size=30, 
                        weight="bold", 
                        color=purple
                    ),
                    # Row of showcasing cards
                    ft.ResponsiveRow(
                        controls=[
                            ft.Container(
                                content=ft.Image(
                                    src="/main.png",   
                                    fit=ft.BoxFit.CONTAIN,
                                    border_radius=12,
                                ),
                                col={"sm": 10, "md": 6, "lg": 3.5},
                            ),
                            ft.Container(
                                content=ft.Image(
                                    src="/sidebar_open0.png",   
                                    fit=ft.BoxFit.CONTAIN,
                                    border_radius=12,
                                ),
                                col={"sm": 10, "md": 6, "lg": 3.5},
                            ),
                            ft.Container(
                                content=ft.Image(
                                    src="/options_hover1.png",   
                                    fit=ft.BoxFit.CONTAIN,
                                    border_radius=12,
                                ),
                                col={"sm": 10, "md": 6, "lg": 3.5},
                            ),
                        ],
                        spacing=20,
                        run_spacing=20,
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                ],
                spacing=30,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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
                                            ft.Text("Your AI learning assistant that turns \nlectures into real understanding.",
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
                                                on_tap=scroll_to_how,
                                                content=ft.Container(
                                                    content=ft.Text("How It Works", size=16, color=white),
                                                    padding=ft.Padding.only(top=1, bottom=1),
                                                )
                                            ),
                                            ft.GestureDetector(
                                                mouse_cursor=ft.MouseCursor.CLICK,
                                                on_tap=scroll_to_features,
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

        # add elemets to the page
        self.controls = [
            self.header,
            self.intro,
            self.steps,
            self.features,
            self.in_action,
            self.footer,
        ]