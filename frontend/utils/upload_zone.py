import flet as ft 
from .dashed_box import dashed_box
import shutil
import os
from pathlib import Path
import httpx
import uuid   

UPLOAD_STATE_IDLE = "idle"
UPLOAD_STATE_HOVER = "hover"
UPLOAD_STATE_FAILED = "failed"

UPLOAD_URL = "http://localhost:8000/documents/upload"
UPLOAD_DIR = Path("assets/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class UploadZone(ft.Container):

    def __init__(self, on_file_accepted=None, auth_token=None, **kwargs):
        self.on_file_accepted = on_file_accepted
        self.selected_file = None
        self.current_state = UPLOAD_STATE_IDLE
        self.auth_token = auth_token
        self._icon  = ft.Icon(ft.Icons.CLOUD_UPLOAD_OUTLINED, size=28, color="#4D1F84")
        self._icon_circle = ft.Container(
            content=self._icon,
            bgcolor="#DCC9F7",
            width=56,
            height=56,
            shape=ft.BoxShape.CIRCLE,
            alignment=ft.Alignment.CENTER,
        )

        self._title = ft.Text("Drop your file here", size=15, weight=ft.FontWeight.W_600, color="#3D1F84")
        
        self._sub = ft.Row(
            [
                ft.Container(expand=True, height=1.5, bgcolor="#BD9CE8"),
                ft.Container(content=ft.Text("or", size=13, color="#4D1F84", weight=ft.FontWeight.W_400), padding=ft.Padding(left=10, right=10, top=0, bottom=0 )),
                ft.Container(expand=True, height=1.5, bgcolor="#BD9CE8"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            width=320,
        )
        
        self._btn = ft.Container(
            content=ft.Text("Browse Files", color="#4D1F84", size=13, weight=ft.FontWeight.W_600),
            bgcolor="#E2D1FC", border_radius=30,
            border=ft.Border.all(1.5, "#BD9CE8"),
            padding=ft.Padding(left=28, right=28, top=10, bottom=10),
            on_click=self._pick_file, ink=True,
        )

        self._idle_col = ft.Column(
            [self._icon_circle, self._title, self._sub, self._btn],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

        self._idle_view = dashed_box(
            width=500, height=230,
            content=self._idle_col,
            border_color="#A682DF",
            bgcolor="#F1E7FE",
            border_radius=28,
            dash_len=8, gap_len=6
        )

        self._hover_view = dashed_box(
            width=500, height=230,
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.CLOUD_UPLOAD_OUTLINED, size=28, color="#5B2D99"),
                        bgcolor="#EFE7F5",
                        width=56, height=56,
                        shape=ft.BoxShape.CIRCLE,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Text("Drop your file here", size=15, weight=ft.FontWeight.W_600, color="#3D1F84"),
                    ft.Row(
                        [
                            ft.Container(expand=True, height=1.5, bgcolor="#9B6FD4"),
                            ft.Container(content=ft.Text("or", size=13, color="#4D1F84", weight=ft.FontWeight.W_400), padding=ft.Padding(left=10, right=10, top=0, bottom=0)),
                            ft.Container(expand=True, height=1.5, bgcolor="#9B6FD4"),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        width=320,
                    ),
                    ft.Container(
                        content=ft.Text("Browse Files", color="#5B2D99", size=13, weight=ft.FontWeight.W_600),
                        bgcolor="#EFE7F5", border_radius=30,
                        border=ft.Border.all(1.5, "#9B6FD4"),
                        padding=ft.Padding(left=28, right=28, top=10, bottom=10),
                        on_click=self._pick_file, ink=True,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=12,
            ),
            border_color="#7B3FBF",
            bgcolor="#C9A8F0",
            border_radius=28,
            dash_len=8, gap_len=6
        )

        self._err_icon = ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, size=28, color="#F7C3D1")
        self._err_icon_circle = ft.Container(
            content=self._err_icon,
            bgcolor="#E96486",
            width=56,
            height=56,
            shape=ft.BoxShape.CIRCLE,
            alignment=ft.Alignment.CENTER,
        )

        self._err_title = ft.Text("Unsupported File Type or File is Too Large", size=15, weight=ft.FontWeight.W_600, color="#C34A68")

        def make_tag(text):
            return ft.Container(
                content=ft.Text(text, size=11, color="#FFFFFF", weight=ft.FontWeight.W_500),
                border=ft.Border.all(1.2, "#F3D0DA"), 
                border_radius=12,
                padding=ft.Padding.symmetric(horizontal=12, vertical=4),
                bgcolor="transparent",
            )

        self._tags_row = ft.Row(
            [
                make_tag("PDF"),
                make_tag("DOC"),
                make_tag("TXT"),
                make_tag("PPTX"),
                make_tag("Max. 20 MB"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        )

        self._err_btn = ft.Container(
            content=ft.Text("Try another file", color="#FFFFFF", size=13, weight=ft.FontWeight.W_600),
            bgcolor="#DF6484", border_radius=30,
            border=ft.Border.all(1.5, "#F7C3D1"),
            padding=ft.Padding(left=28, right=28, top=10, bottom=10),
            on_click=self._pick_file, ink=True,
        )

        self._err_col = ft.Column(
            [self._err_icon_circle, self._err_title, self._tags_row, self._err_btn],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

        self._error_view = dashed_box(
            width=500, height=230,
            content=self._err_col,
            border_color="#CC2B52",
            bgcolor="#F7A1B8",
            border_radius=28,
            dash_len=8, gap_len=6
        )

        self._switcher = ft.AnimatedSwitcher(
            content=self._idle_view,
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=200,
        )

        super().__init__(
            width=500, height=230, border_radius=28,
            bgcolor=ft.Colors.TRANSPARENT, 
            content=self._switcher,
            on_hover=self._on_hover, 
            **kwargs,
        )

    def _update_visual_state(self, state):
        self.current_state = state

        if state == UPLOAD_STATE_IDLE:
            self._switcher.content = self._idle_view
        elif state == UPLOAD_STATE_HOVER:
            self._switcher.content = self._hover_view
        elif state == UPLOAD_STATE_FAILED:
            self._switcher.content = self._error_view

        self._safe_update()

    def _set_idle(self):
        self._update_visual_state(UPLOAD_STATE_IDLE)

    def _set_error(self, reason):
        self._update_visual_state(UPLOAD_STATE_FAILED)

    def _safe_update(self):
        try:
            self.update()
        except Exception:
            pass

    def _on_hover(self, e):
        is_hovering = e.data == True or e.data == "true"  # handles both types safely
        self.mouse_cursor = ft.MouseCursor.CLICK if is_hovering else ft.MouseCursor.BASIC

        if self.current_state != UPLOAD_STATE_FAILED:
            if is_hovering:
                self._update_visual_state(UPLOAD_STATE_HOVER)
            else:
                self._update_visual_state(UPLOAD_STATE_IDLE)


    async def _pick_file(self, e):
        try:
            picked_files = await ft.FilePicker().pick_files(
                allow_multiple=False,
                allowed_extensions=["pdf", "doc", "docx", "txt", "pptx"],
                with_data=True,
            )

            if not picked_files:
                self._set_idle()
                return

            f = picked_files[0]

            if f.size and f.size > 20 * 1024 * 1024:
                self._set_error("File too large (max 20 MB)")
                return

            title_field = ft.TextField(
                label="Document Topic",
                hint_text="e.g., Final Year Grad Project",
                autofocus=True,
                color="#2D2D2D", 
                border_color="#4D1F84",
                cursor_color="#4D1F84",
                focused_border_color="#4D1F84"
            )

            def close_dialog(e):
                dialog.open = False
                self.page.update()
                self._set_idle()

            async def submit_title(e):
                # If they leave it blank, default back to the raw file name
                user_title = title_field.value.strip() or f.name
                dialog.open = False
                self.page.update()
                
                # Pass the file and the custom title to the second half of our upload logic!
                await self._execute_upload(f, user_title)

            dialog = ft.AlertDialog(
                bgcolor="#F8F4FF",
                shape=ft.RoundedRectangleBorder(radius=16), # Softer, modern corners
                
                title=ft.Row(
                    [
                        ft.Icon(ft.Icons.DESCRIPTION_ROUNDED, color="#4D1F84", size=24),
                        ft.Text("Name this document", weight=ft.FontWeight.W_700, color="#2D2D2D", size=18)
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10
                ),
                
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("What topic are we tackling today?", size=14, color="#6B4B9A"),
                        title_field
                    ], tight=True, spacing=15),
                    padding=ft.Padding(10, 10, 10, 0),
                    width=400 # Gives the text field nice breathing room
                ),
                
                actions=[
                    ft.TextButton(
                        "Cancel", 
                        on_click=close_dialog, 
                        style=ft.ButtonStyle(color="#8D63C6")
                    ),
                    ft.FilledButton(
                        "Upload", 
                        on_click=submit_title, 
                        style=ft.ButtonStyle(
                            bgcolor="#4D1F84", 
                            color="white", 
                            shape=ft.RoundedRectangleBorder(radius=8)
                        )
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                actions_padding=ft.Padding(15, 10, 15, 15), # Pushes the buttons off the bottom edge
            )

            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()

        except Exception as ex:
            print("Upload error:", ex)
            self._set_error(f"Error: {str(ex)}")


    # --- THE SECOND HALF OF YOUR EXISTING LOGIC ---
    async def _execute_upload(self, f, custom_title):
        try:
            print(f"📤 Uploading: {f.name} as '{custom_title}'")
            
            chat_page = self.page.views[-1]
            conv_id = getattr(chat_page, 'current_conversation_id', str(uuid.uuid4()))

            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}

            async with httpx.AsyncClient() as client:
                files = {"file": (f.name, f.bytes, "application/pdf")}
                
                data = {
                    "conversation_id": conv_id,
                    "title": custom_title
                } 

                response = await client.post(
                    UPLOAD_URL, 
                    files=files, 
                    data=data,
                    headers=headers,
                    timeout=60.0
                )

                if response.status_code != 200:
                    print("Backend Error:", response.text)
                    self._set_error(f"Upload failed: {response.text[:300]}")
                    return

                result = response.json()
                public_url = result.get("file_url")

            print(f"✅ Success! URL: {public_url}")

            if self.on_file_accepted:
                self.on_file_accepted(f, public_url, custom_title)

        except Exception as ex:
            print("Upload error:", ex)
            self._set_error(f"Error: {str(ex)}")