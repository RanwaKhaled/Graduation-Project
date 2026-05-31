import flet as ft
import uuid
from flet_audio import Audio, ReleaseMode
import requests
from utils.components import MAIN_BG, sidebar, top_bar, main_area
from utils.right_panel import right_panel
from utils.pdf_viewer import PdfViewer

class ChatPage(ft.View):
    def __init__(self, page: ft.Page, auth_token: str = None):
        super().__init__(route="/chat", padding=0, bgcolor=MAIN_BG)
        
        self.auth_token = auth_token
        self.viewer_ref = ft.Ref[PdfViewer]()
        
        # 1. Generate the conversation ID the moment they open the chat
        self.current_conversation_id = str(uuid.uuid4())

        self.history_listview = ft.ListView(expand=True, spacing=5)

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

        self.fetch_history()

    def build_ui(self):

        def toggle_sidebar(e):
            my_sidebar.width = 200 if my_sidebar.width == 80 else 80
            my_sidebar.update()

        my_sidebar = sidebar(toggle_sidebar, self.history_listview, on_logout=self.handle_logout)

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
                history_data = res.json().get("history", [])
                self.populate_sidebar(history_data)
        except Exception as e:
            print(f"History fetch failed: {e}")

    def populate_sidebar(self, history_data):
        self.history_listview.controls.clear()
        
        for chat in history_data:
            is_active = (chat["id"] == self.current_conversation_id)

            chat_btn = ft.Container(
                content=ft.Text(chat["title"], color="white", size=14, no_wrap=True),
                padding=10,
                border_radius=8,
                bgcolor="#5A1B8A" if is_active else None, # Default to None on first load
                data=chat["id"], 
                on_click=lambda e, cid=chat["id"]: self.load_historical_chat(cid),
                on_hover=self.highlight_chat
            )
            self.history_listview.controls.append(chat_btn)
            
        if self.history_listview.page:
            self.history_listview.update()


    def highlight_chat(self, e):
        # In Flet, e.data is the string "true" when the mouse enters, and "false" when it leaves
        is_hovered = (e.data == "true")
        
        # Check the secret ID we stored in the control against the active chat ID
        is_active = (e.control.data == self.current_conversation_id)
        
        if is_active:
            # If they are currently viewing this chat, KEEP it highlighted!
            e.control.bgcolor = "#5A1B8A" 
        else:
            # If it's inactive, give it a subtle hover effect, or remove the background
            e.control.bgcolor = "#3F1361" if is_hovered else None
            
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
                # 1. Update our master dictionary with the old database URLs
                self.document_urls = res.json()
                
                # 2. Swap the Upload UI out for the Viewer if it isn't already active
                if not self.viewer_ref.current:
                    self.viewer_ref.current = PdfViewer(document_urls=self.document_urls)
                    self.inner_row.controls[0] = ft.Container(
                        content=self.viewer_ref.current,
                        expand=True,
                        padding=ft.Padding.only(left=48, right=48, top=40, bottom=40)
                    )
                
                # 3. Force the viewer to ingest the old URLs and render the Document
                self.viewer_ref.current.document_urls = self.document_urls
                self.viewer_ref.current.load_pdf(doc_type="Document")
                
                self.page.update()
                
        except Exception as e:
            print(f"Error loading chat context: {e}")

    def update_sidebar_selection(self):
        # Loops through existing buttons and softly updates their background color
        for btn in self.history_listview.controls:
            is_active = (btn.data == self.current_conversation_id)
            btn.bgcolor = "#5A1B8A" if is_active else None
            
            # 🛡️ THE SAFETY LOCK: Prevents the ghost-button crash
            if btn.page:
                btn.update()