import os
import shutil
import time
import flet as ft
from flet_audio import Audio, ReleaseMode

# Adjust these imports based on where your files actually live
from utils.components import MAIN_BG, sidebar, top_bar, main_area
from utils.right_panel import right_panel
from utils.pdf_viewer import PdfViewer, convert_to_pdf 

def main(page: ft.Page):
    page.title = "Upload & View"
    page.bgcolor = MAIN_BG
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1200
    page.window.height = 760

    os.makedirs("assets", exist_ok=True)

    audio = Audio(src="audio.mp3", autoplay=False, volume=1.0, release_mode=ReleaseMode.STOP)
    page.services.append(audio)
    page.update()

    def toggle_sidebar(e):
        my_sidebar.width = 200 if my_sidebar.width == 80 else 80
        my_sidebar.update()

    my_sidebar = sidebar(toggle_sidebar)

    viewer_ref = ft.Ref[PdfViewer]()

    def handle_view_change(pdf_url: str):
        if viewer_ref.current:
            viewer_ref.current.load_pdf(pdf_url, is_original=False)

    def accepted(f):
        print(f"✅ File accepted: {f.name} ({f.size} bytes)")
        
        body_col.controls[0] = top_bar(active_step=2)
        page.update()

        uploaded_path = os.path.join("assets", f.name)
        if hasattr(f, 'path') and f.path:
            shutil.copy(f.path, uploaded_path)
        
        final_pdf_name = f.name.rsplit('.', 1)[0] + "_converted.pdf"
        final_pdf_path = os.path.join("assets", final_pdf_name)
        
        convert_to_pdf(uploaded_path, final_pdf_path)

        viewer_url = f"/{final_pdf_name}"
        viewer_ref.current = PdfViewer(original_pdf_url=viewer_url)
        
        inner_row.controls[0] = ft.Container(
            content=viewer_ref.current,
            expand=True,
            padding=ft.Padding(left=48, right=48, top=40, bottom=40)
        )

        body_col.controls[0] = top_bar(active_step=3)
        page.update()

    inner_row = ft.Row(
        [
            main_area(on_file_accepted=accepted),
            right_panel(audio, on_view_change=handle_view_change),
        ],
        expand=True,
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    body_col = ft.Column(
        [
            top_bar(active_step=1),
            inner_row,
        ],
        expand=True,
        spacing=0,
    )

    page.add(
        ft.Row(
            [my_sidebar, body_col],
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )
    )

ft.run(main, assets_dir="assets")