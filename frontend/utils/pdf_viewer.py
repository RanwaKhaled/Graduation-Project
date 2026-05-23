import flet as ft
from flet_webview import WebView

class PdfViewer(ft.Container):
    def __init__(self, original_pdf_url: str, base_url: str = "http://127.0.0.1:8080", **kwargs):
        super().__init__(**kwargs)
        self.expand = True
        self.bgcolor = "#FFFFFF"
        self.border_radius = 12
        self.padding = 24
        self.base_url = base_url
        self.original_pdf_url = original_pdf_url
        self.current_pdf_url = original_pdf_url

        self.title_text = ft.Text(
            "Uploaded Document",
            size=20, weight=ft.FontWeight.W_700, color="#1A1A2E"
        )

        self.toggle_btn = ft.FilledButton(
            content=ft.Text("Back to Uploaded Document"),
            icon=ft.Icons.RESTORE_PAGE_ROUNDED,
            on_click=self.show_original,
            visible=False,
            style=ft.ButtonStyle(
                bgcolor="#F15C22",
                color="white",
                shape=ft.RoundedRectangleBorder(radius=8),
            )
        )

        self.header_row = ft.Row(
            [self.title_text, self.toggle_btn],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Full absolute URL — browsers require this to render PDFs in iframes
        self.viewer = WebView(
            url=self._full_url(original_pdf_url),
            expand=True,
            on_web_resource_error=lambda e: print("WebView error:", e.data),
        )

        self.content = ft.Column(
            [
                self.header_row,
                ft.Container(
                    content=self.viewer,
                    expand=True,
                    border=ft.Border.all(1.5, "#EBEBEB"),
                    border_radius=8,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE
                )
            ],
            expand=True,
            spacing=16
        )

    def _full_url(self, path: str) -> str:
        # If already absolute, use as-is
        if path.startswith("http"):
            return path
        # Strip leading slash and combine with base
        return f"{self.base_url}/{path.lstrip('/')}"

    def load_pdf(self, pdf_url: str, is_original: bool = False):
        self.current_pdf_url = pdf_url
        self.viewer.url = self._full_url(pdf_url)
        try:
            self.viewer.update()
        except RuntimeError:
            pass

        if is_original:
            self.title_text.value = "Uploaded Document"
            self.toggle_btn.visible = False
        else:
            doc_name = pdf_url.strip("/").split(".")[0].title()
            self.title_text.value = f"Generated {doc_name}"
            self.toggle_btn.visible = True

        try:
            self.title_text.update()
            self.toggle_btn.update()
        except RuntimeError:
            pass

    def show_original(self, e):
        self.load_pdf(self.original_pdf_url, is_original=True)


def convert_to_pdf(input_filepath: str, output_filepath: str):
    pass