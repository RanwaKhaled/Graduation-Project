import flet as ft
from flet_webview import WebView

class PdfViewer(ft.Container):
    def __init__(self, original_pdf_url: str, **kwargs):
        super().__init__(**kwargs)
        self.expand = True
        self.bgcolor = "#FFFFFF"
        self.border_radius = 12
        self.padding = 24
        
        self.original_pdf_url = original_pdf_url
        self.current_pdf_url = original_pdf_url

        self.title_text = ft.Text("Uploaded Document", size=20, weight=ft.FontWeight.W_700)

        self.toggle_btn = ft.FilledButton(
            "Back to Uploaded Document",
            icon=ft.Icons.RESTORE_PAGE_ROUNDED,
            on_click=self.show_original,
            visible=False,
            style=ft.ButtonStyle(bgcolor="#F15C22", color="white")
        )

        self.header_row = ft.Row([self.title_text, self.toggle_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.viewer = WebView(
            url=original_pdf_url,   # Direct public URL
            expand=True,
        )

        self.content = ft.Column([
            self.header_row,
            ft.Container(content=self.viewer, expand=True, border=ft.border.all(1.5, "#EBEBEB"), border_radius=8)
        ], expand=True, spacing=16)

    def load_pdf(self, doc_type: str = "", pdf_url: str = "", is_original: bool = False):
        # For generated files (Explanation, Quiz, etc.)
        if doc_type in ["Explanation", "Transcript", "Quiz"]:
            # TODO: Later replace with real URLs from backend
            pdf_url = f"https://your-supabase-url.supabase.co/storage/v1/object/public/documents/generated_{doc_type.lower()}.pdf"

        elif not pdf_url:
            pdf_url = self.original_pdf_url

        self.current_pdf_url = pdf_url
        self.viewer.url = pdf_url
        self.viewer.update()

        if is_original or doc_type == "Document":
            self.title_text.value = "Uploaded Document"
            self.toggle_btn.visible = False
        else:
            self.title_text.value = f"Generated {doc_type}"
            self.toggle_btn.visible = True

        self.title_text.update()
        self.toggle_btn.update()

    def show_original(self, e):
        self.load_pdf(doc_type="Document", is_original=True)