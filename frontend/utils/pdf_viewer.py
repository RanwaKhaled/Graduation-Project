import flet as ft
import os
import shutil

try:
    from flet_webview import WebView
except ImportError:
    WebView = None

class PdfViewer(ft.Container):
    def __init__(self, original_pdf_url: str, **kwargs):
        super().__init__(**kwargs)
        self.expand = True
        self.bgcolor = "#FFFFFF"
        self.border_radius = 12
        self.padding = 24
        self.original_pdf_url = original_pdf_url
        self.current_pdf_url = original_pdf_url

        # --- Header Elements ---
        self.title_text = ft.Text("Uploaded Document", size=20, weight=ft.FontWeight.W_700, color="#1A1A2E")

        self.toggle_btn = ft.ElevatedButton(
            content="Back to Uploaded Document",
            icon=ft.Icons.RESTORE_PAGE_ROUNDED,
            color="white",
            bgcolor="#F15C22",
            on_click=self.show_original,
            visible=False, # Hidden initially
            height=40,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                elevation=2,
            )
        )

        self.header_row = ft.Row(
            [
                self.title_text,
                self.toggle_btn
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # --- Viewer Element ---
        if WebView:
            self.viewer = WebView(
                url=self.current_pdf_url,
                expand=True,
            )
        else:
            self.viewer = ft.Container(
                content=ft.Text(
                    "Please install flet-webview (pip install flet-webview)",
                    color="red", weight=ft.FontWeight.W_600
                ),
                expand=True, alignment=ft.Alignment.CENTER, bgcolor="#F4EEF9"
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

    def load_pdf(self, pdf_url: str, is_original: bool = False):
        self.current_pdf_url = pdf_url
        
        if hasattr(self.viewer, 'url'):
            self.viewer.url = pdf_url
            self.viewer.update()
        
        # Update the UI dynamically
        if is_original:
            self.title_text.value = "Uploaded Document"
            self.toggle_btn.visible = False
        else:
            # Change title based on URL (e.g. "/dummy.pdf" -> "Dummy")
            # When you plug in real URLs like /quiz.pdf, this will say "Generated Quiz"
            doc_name = pdf_url.strip("/").split(".")[0].title()
            self.title_text.value = f"Generated {doc_name}"
            self.toggle_btn.visible = True

        self.title_text.update()
        self.toggle_btn.update()

    def show_original(self, e):
        self.load_pdf(self.original_pdf_url, is_original=True)


def convert_to_pdf(input_filepath: str, output_filepath: str):
    # (Leaving this in case you need it later, though we bypassed it in main.py)
    pass