import flet as ft
import uuid
from flet_audio import Audio, ReleaseMode
import requests
from utils.components import MAIN_BG, sidebar, top_bar, main_area
from utils.right_panel import right_panel
from utils.pdf_viewer import PdfViewer
import threading

class ChatPage(ft.View):
    def __init__(self, page: ft.Page, auth_token: str = None):
        super().__init__(route="/chat", padding=0, bgcolor=MAIN_BG)
        
        self.auth_token = auth_token
        self.viewer_ref = ft.Ref[PdfViewer]()
        
        # 1. Generate the conversation ID the moment they open the chat
        self.current_conversation_id = str(uuid.uuid4())
        self.profile_name = ft.Text("...", color="white", size=15, weight=ft.FontWeight.W_600, animate_opacity=150)
        self.chat_history_text = ft.Text("Chat History", color="white", size=15, weight=ft.FontWeight.W_600, opacity=0, animate_opacity=150)
        self.logout_text = ft.Text("Log Out", color="white", size=15, weight=ft.FontWeight.W_600, opacity=0, animate_opacity=150)
        self.history_listview = ft.ListView(expand=True, spacing=5, visible=False)

        # 2. Set up our URLs. 
        # Using safe public PDFs for Explanation/Quiz so you can test the UI buttons NOW.
        self.document_urls = {
            "Document": None, # Will be filled when they upload
            "Explanation": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "Transcript":  "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "Quiz": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
        }

        self.audio = Audio(
            src="audio.mp3", 
            autoplay=False, 
            volume=1.0, 
            release_mode=ReleaseMode.STOP
        )
        self.services.append(self.audio)

        self.body_col = None
        self.inner_row = None
        self.controls = [self.build_ui()]

        threading.Thread(target=self.fetch_history, daemon=True).start()

    def build_ui(self):
        def toggle_sidebar(e):
            is_closed = (my_sidebar.width == 70)
            
            my_sidebar.width = 280 if is_closed else 70

            new_opacity = 1 if is_closed else 0
            self.chat_history_text.opacity = new_opacity
            self.profile_name.opacity = new_opacity
            self.logout_text.opacity = new_opacity
            self.history_listview.visible = is_closed

            my_sidebar.update()
            self.chat_history_text.update()
            self.profile_name.update()
            self.logout_text.update()
            self.history_listview.update()

        my_sidebar = sidebar(toggle_sidebar, self.history_listview, user_first_name=self.profile_name, chat_history_text=self.chat_history_text, logout_text=self.logout_text, on_logout=self.handle_logout)

        def on_view_change(doc_type: str):
            # This triggers when you click "Explanation" or "Quiz" in the right panel
            if self.viewer_ref.current:
                self.viewer_ref.current.load_pdf(doc_type=doc_type)
                self.page.update()

        # Pass the accepted function down
        upload_zone = main_area(on_file_accepted=self.accepted, auth_token=self.auth_token)

        self.inner_row = ft.Row(
            [
                upload_zone,
                right_panel(self.audio, on_view_change=on_view_change),
            ],
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        self.body_col = ft.Column(
            [
                top_bar(active_step=1),
                self.inner_row,
            ],
            expand=True,
            spacing=0,
        )

        return ft.Row(
            [my_sidebar, self.body_col],
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

    def accepted(self, f, public_url: str):
        # 3. This runs when FastAPI successfully returns the Supabase URL
        print(f"✅ Real Supabase URL received: {public_url}")

        # Update our dictionary with the REAL document URL
        self.document_urls["Document"] = public_url

        if self.body_col:
            self.body_col.controls[0] = top_bar(active_step=2)
            self.page.update()

        # 4. Initialize the viewer with our dictionary of URLs
        if not self.viewer_ref.current:
            self.viewer_ref.current = PdfViewer(document_urls=self.document_urls)

        # 5. Swap the UploadBox for the PdfViewer
        if self.inner_row:
            self.inner_row.controls[0] = ft.Container(
                content=self.viewer_ref.current,
                expand=True,
                padding=ft.Padding.only(left=48, right=48, top=40, bottom=40)
            )

            if self.body_col:
                self.body_col.controls[0] = top_bar(active_step=3)
                self.page.update()

    def handle_logout(self, e):
        self.page.client_storage.set("auth_token", None)
        print("Logged out successfully.")
        self.page.go("/login")

    def fetch_history(self):
        try:
            res = requests.get(
                "http://localhost:8000/chat/history",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            if res.status_code == 200:
                data = res.json() # Parse the JSON once
                
                # 1. Update the UI with the user's real first name!
                self.profile_name.value = data.get("first_name", "User")
                if self.profile_name.page:
                    self.profile_name.update()
                
                # 2. Populate the history list
                history_data = data.get("history", [])
                self.populate_sidebar(history_data)
        except Exception as e:
            pass

    def populate_sidebar(self, history_data):
        self.history_data = history_data 
        self.history_listview.controls.clear()
        
        for chat in history_data:
            is_active = (chat["id"] == self.current_conversation_id)
            
            chat_btn = ft.Container(
                content=ft.Text(chat["title"], color="white", size=14, no_wrap=True),
                padding=12, # Added slightly more padding so the text doesn't hit the new borders
                border_radius=8,
                
                # 🎨 THE NEW UI UPGRADES:
                # A subtle, 15% opacity white border so they are distinct but not distracting
                border=ft.Border.all(1, ft.Colors.with_opacity(0.3 if is_active else 0.15, "white")),
                bgcolor="#5A1B8A" if is_active else None, 
                
                # Smooth 150ms fade effect for when the mouse hovers over it!
                animate=ft.Animation(150, curve=ft.AnimationCurve.EASE_OUT), 
                
                data=chat["id"], 
                on_click=lambda e, cid=chat["id"]: self.load_historical_chat(cid),
                on_hover=self.highlight_chat
            )
            self.history_listview.controls.append(chat_btn)
            
        if self.history_listview.page:
            self.history_listview.update()


    def highlight_chat(self, e):
        is_hovered = (e.data == "true")
        is_active = (e.control.data == self.current_conversation_id)
        
        if is_active:
            # Active chat stays bright
            e.control.bgcolor = "#5A1B8A" 
            e.control.border = ft.Border.all(1, ft.Colors.with_opacity(0.3, "white"))
        else:
            # Inactive chats get a dark purple background and slightly brighter border ON HOVER
            e.control.bgcolor = "#3F1361" if is_hovered else None
            e.control.border = ft.Border.all(1, ft.Colors.with_opacity(0.3 if is_hovered else 0.15, "white"))
            
        if e.control.page:
            e.control.update()

    def load_historical_chat(self, conversation_id):
        print(f"Loading old chat: {conversation_id}")
        self.current_conversation_id = conversation_id
        self.update_sidebar_selection()
            
        try:
            res = requests.get(
                f"http://localhost:8000/chat/{conversation_id}/documents",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            if res.status_code == 200:
                self.document_urls = res.json()
                
                # If the viewer doesn't exist, build it and mount it
                if not self.viewer_ref.current:
                    self.viewer_ref.current = PdfViewer(document_urls=self.document_urls)
                    self.inner_row.controls[0] = ft.Container(
                        content=self.viewer_ref.current,
                        expand=True,
                        padding=ft.Padding.only(left=48, right=48, top=40, bottom=40)
                    )
                    # 🚀 THE FIX: Force Flet to physically draw the viewer on screen BEFORE we try to load text into it!
                    self.page.update() 
                
                # Now it is safe to load the PDF!
                self.viewer_ref.current.document_urls = self.document_urls
                self.viewer_ref.current.load_pdf(doc_type="Document")
                self.page.update()
                
        except Exception as e:
            print(f"Error loading chat context: {e}")

    def update_sidebar_selection(self):
        for btn in self.history_listview.controls:
            is_active = (btn.data == self.current_conversation_id)
            
            btn.bgcolor = "#5A1B8A" if is_active else None
            btn.border = ft.Border.all(1, ft.Colors.with_opacity(0.3 if is_active else 0.15, "white"))
            
            if btn.page:
                btn.update()