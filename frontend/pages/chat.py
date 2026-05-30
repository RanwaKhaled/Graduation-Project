import flet as ft
import uuid
from flet_audio import Audio, ReleaseMode

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

    def build_ui(self):
        def toggle_sidebar(e):
            my_sidebar.width = 200 if my_sidebar.width == 80 else 80
            my_sidebar.update()

        my_sidebar = sidebar(toggle_sidebar)

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