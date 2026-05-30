import flet as ft
from flet_webview import WebView
import urllib.parse

class PdfViewer(ft.Container):
    def __init__(self, document_urls: dict, **kwargs):
        super().__init__(**kwargs)
        self.expand = True
        self.bgcolor = "#FFFFFF"
        self.border_radius = 12
        self.padding = 24
        
        self.document_urls = document_urls
        self.current_doc_type = "Document"

        self.title_text = ft.Text("Uploaded Document", size=20, weight=ft.FontWeight.W_700)

        self.toggle_btn = ft.FilledButton(
            "Back to Uploaded Document",
            icon=ft.Icons.RESTORE_PAGE_ROUNDED,
            on_click=self.show_original,
            visible=False,
            style=ft.ButtonStyle(bgcolor="#F15C22", color="white")
        )

        self.header_row = ft.Row([self.title_text, self.toggle_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Grab the initial URL and make it embeddable
        initial_url = self.document_urls.get("Document", "")
        safe_url = self.make_embeddable(initial_url)

        self.viewer = WebView(
            url=safe_url, 
            expand=True,
        )

        self.content = ft.Column([
            self.header_row,
            ft.Container(content=self.viewer, expand=True, border=ft.Border.all(1.5, "#EBEBEB"), border_radius=8)
        ], expand=True, spacing=16)

    def make_embeddable(self, raw_url: str):
        if not raw_url:
            return ""
        encoded_url = urllib.parse.quote(raw_url, safe="")
        # MUST BE localhost
        return f"http://localhost:8000/documents/proxy?url={encoded_url}"

    def load_pdf(self, doc_type: str):
        target_url = self.document_urls.get(doc_type)
        
        if not target_url:
            return

        self.current_doc_type = doc_type
        
        # Apply the wrapper before updating the viewer!
        self.viewer.url = self.make_embeddable(target_url)
        self.viewer.update()

        if doc_type == "Document":
            self.title_text.value = "Uploaded Document"
            self.toggle_btn.visible = False
        else:
            self.title_text.value = f"Generated {doc_type}"
            self.toggle_btn.visible = True

        self.title_text.update()
        self.toggle_btn.update()

    def show_original(self, e):
        self.load_pdf(doc_type="Document")