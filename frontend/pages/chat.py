import os
import flet as ft
import httpx
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

        self.audio = Audio(
            src="audio.mp3", 
            autoplay=False, 
            volume=1.0, 
            release_mode=ReleaseMode.STOP
        )
        self.services.append(self.audio)

        self.body_col = None
        self.inner_row = None

        # FIXED: Attach the audio directly to the view's controls
        self.controls = [self.build_ui()]

    def build_ui(self):
        def toggle_sidebar(e):
            my_sidebar.width = 200 if my_sidebar.width == 80 else 80
            my_sidebar.update()

        my_sidebar = sidebar(toggle_sidebar)

        def on_view_change(doc_type: str):
            if self.viewer_ref.current:
                self.viewer_ref.current.load_pdf(doc_type=doc_type)
                self.page.update()

        # Pass the accepted handler + auth_token to main_area if needed
        upload_zone = main_area(on_file_accepted=self.accepted)

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

    # This is called after successful upload from main_area
    def accepted(self, f, public_url: str):
        print(f"✅ File accepted: {f.name}")
        print(f"Public URL: {public_url}")

        # Step 2
        if self.body_col:
            self.body_col.controls[0] = top_bar(active_step=2)
            self.page.update()

        # Load PDF Viewer
        if not self.viewer_ref.current:
            self.viewer_ref.current = PdfViewer(original_pdf_url=public_url)

        # Replace upload zone with viewer
        if self.inner_row:
            self.inner_row.controls[0] = ft.Container(
                content=self.viewer_ref.current,
                expand=True,
                padding=ft.padding.only(left=48, right=48, top=40, bottom=40)
            )

            # Step 3
            if self.body_col:
                self.body_col.controls[0] = top_bar(active_step=3)
                self.page.update()