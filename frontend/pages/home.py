# frontend/pages/home.py
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

class HomePage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/",
                         padding = 0,
                         spacing=0,
                         bgcolor=ft.Colors.WHITE,
                        )
        
        self.scroll = ft.ScrollMode.AUTO
        
        # helper functions
        # function to go to features
        async def scroll_to_features(e):
            try:
                await self.scroll_to(
                    offset=600,  # approximate pixel offset — adjust this number to match your header + intro height
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
                ft.TextButton(content=ft.Text("Home", size=22), 
                              style=ft.ButtonStyle(color=ft.Colors.WHITE),
                              on_click=lambda e: page.go("/")),
                ft.TextButton(content=ft.Text("Features", size=22), 
                              style=ft.ButtonStyle(color=ft.Colors.WHITE),
                              on_click=scroll_to_features
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
                    ft.Container(height=80, content=ft.Image(src="/logo_white.png", fit= ft.BoxFit.CONTAIN)),
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

        # intro slogan
        self.slogans = ft.Column(
            controls=[
                ft.Text("Welcome to Yosr, \nwhere complexity is simplified",
                        size=45,
                        weight='bold',
                        color=purple
                        ),
                ft.Text("The all-in-one platform to manage your workflow without the headache. \nStop fighting with your tools. Start getting things done with Yosr.",
                        size=20,
                        color=ft.Colors.BLACK
                ),
                ft.Button(
                    ft.Text("Get Started Today", size=22),
                    bgcolor=orange,
                    color=ft.Colors.WHITE,
                    height=50,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=30)),
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
                    ft.Container(#height=100,
                                 expand=True, 
                                 content=ft.Image(src="/laptop.png", fit= ft.BoxFit.CONTAIN)),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=blue,
            padding=ft.Padding.all(50),
            
        ) 

        # features part
        # helper function to create a feature card easily
        def create_feature_card(icon_path, title, description):
            return ft.Container(
                content=ft.Column(
                    controls=[
                        # Icon Container (The small rounded square for the image)
                        ft.Container(
                            content=ft.Image(src=icon_path, height=70, fit=ft.BoxFit.CONTAIN),
                            bgcolor=pink,
                            padding=5,
                            border_radius=15,
                            width=70,
                            height=70,
                        ),
                        ft.Text(title, color=orange, size=24, weight="bold"),
                        ft.Text(description, color=ft.Colors.BLACK, size=16),
                    ],
                    spacing=10,
                ),
                bgcolor=babypink,
                padding=30,
                border_radius=30, # Makes it look like the Figma
                width=220,        # Give cards a consistent width
                height=250,       # Give cards a consistent height
            )

        # Create the three cards
        self.summarization = create_feature_card(
            "/report.png", "Summaries", "Smart summaries of your content in Egyptian Arabic"
        )
        self.tts = create_feature_card(
            "/microphone.png", "Text-to-Speech", "Listen to explanations using our Egyptian TTS feature"
        )
        self.qa = create_feature_card(
            "/chat.png", "MCQ & Essay Questions", "Create multiple-choice and essay questions from your content"
        )

        # Assemble the section
        self.features = ft.Container(
                        key = "features_section",
                        padding=ft.Padding.symmetric(vertical=60, horizontal=50),
                        content=ft.Column(
                            controls=[
                                ft.Text("Features", size=40, weight="bold", color=purple),
                                ft.ResponsiveRow(
                                    controls=[
                                        # Assign the 'col' property to each card
                                        # This says: on desktop (large), take 4/12 (3 per row)
                                        # On mobile (small), take 12/12 (stack vertically)
                                        ft.Container(self.summarization, col={"sm": 10, "md": 6, "lg": 3}),
                                        ft.Container(self.tts, col={"sm": 10, "md": 6, "lg": 3}),
                                        ft.Container(self.qa, col={"sm": 10, "md": 6, "lg": 3}),
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
        
        # making the footer
        self.footer = ft.Container(
            bgcolor=purple,
            padding=ft.Padding.symmetric(vertical=15, horizontal=50),
            content=ft.Row(
                controls=[
                    ft.Image(src="/logo_white.png", height=40, fit=ft.BoxFit.CONTAIN),
                    ft.Text("\u00A9 2026 Yosr. All rights reserved.",
                            color=ft.Colors.WHITE,
                            size=14,
                            ), 
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        # add elemets to the page
        self.controls = [
            self.header,
            self.intro,
            self.features,
            self.footer,
        ]