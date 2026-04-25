# frontend/pages/chat.py
import flet as ft

class ChatPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/chat")
        self.controls = [
            ft.Text("Chat Page - coming soon", size=30)
        ]