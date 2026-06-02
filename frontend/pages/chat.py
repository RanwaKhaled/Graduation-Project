import time
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
        self.processing_chats = set()

        self.shield = ft.Container(
            bgcolor=ft.Colors.TRANSPARENT,
            left=0, right=0, top=0, bottom=0,
            visible=False,
            on_click=self.show_locked_warning
        )

        self.empty_shield = ft.Container(
            bgcolor=ft.Colors.TRANSPARENT,
            left=0, right=0, top=0, bottom=0,
            visible=True, 
            on_click=self.show_empty_warning
        )

        self.current_conversation_id = str(uuid.uuid4())
        
        self.profile_name = ft.Text("...", color="white", size=15, weight=ft.FontWeight.W_600, animate_opacity=150)
        self.chat_history_text = ft.Text("Chat History", color="white", size=15, weight=ft.FontWeight.W_600, opacity=0, animate_opacity=150)
        self.logout_text = ft.Text("Log Out", color="white", size=15, weight=ft.FontWeight.W_600, opacity=0, animate_opacity=150)
        self.history_listview = ft.ListView(expand=True, spacing=5, visible=False)


        self.document_urls = {
            "Document": None, 
            "Explanation": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "Transcript":  "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "Quiz": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf", 
            "Audio": "audio.mp3"
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

        upload_zone = main_area(on_file_accepted=self.accepted, auth_token=self.auth_token)

        safe_right_panel = ft.Stack(
            controls=[
                right_panel(self.audio, on_view_change=self.handle_view_change),
                self.shield,
                self.empty_shield,
            ],
        )

        self.inner_row = ft.Row(
            [
                upload_zone,
                safe_right_panel,
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

    def accepted(self, f, public_url: str, custom_title: str): 
        print(f"✅ Real Supabase URL received: {public_url}")

        self.document_urls["Document"] = public_url
        active_id = self.current_conversation_id

        self.processing_chats.add(active_id)
        
        if self.body_col:
            self.body_col.controls[0] = top_bar(active_step=2)

        if not self.viewer_ref.current:
            self.viewer_ref.current = PdfViewer(document_urls=self.document_urls, document_title=custom_title)
            self.inner_row.controls[0] = ft.Container(
                content=self.viewer_ref.current,
                expand=True,
                padding=ft.Padding.only(left=48, right=48, top=40, bottom=40)
            )
        else:
            self.viewer_ref.current.document_title = custom_title
            self.viewer_ref.current.document_urls = self.document_urls
            self.viewer_ref.current.load_pdf(doc_type="Document")

        if self.inner_row:
            self.inner_row.controls[0] = ft.Container(
                content=self.viewer_ref.current,
                expand=True,
                padding=ft.Padding.only(left=48, right=48, top=40, bottom=40)
            )

        
        self.shield.visible = True
        self.empty_shield.visible = False
        self.page.update()

        threading.Thread(target=self.fetch_history, daemon=True).start()
        threading.Thread(target=self.wait_for_ai_generation, args=(active_id,), daemon=True).start()

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
        
        # 🚀 ADDITION: The "New Conversation" Button
        new_chat_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD_ROUNDED, color="white", size=20),
                ft.Text("New Conversation", color="white", size=14, weight=ft.FontWeight.W_600)
            ]),
            padding=12,
            border_radius=8,
            bgcolor="#7B3FBF", # A slightly lighter purple to make it stand out!
            on_click=self.start_new_conversation # We will write this function next!
        )
        self.history_listview.controls.append(new_chat_btn)
        
        # --- The History Loop ---
        for chat in history_data:
            is_active = (chat["id"] == self.current_conversation_id)
            
            chat_btn = ft.Container(
                content=ft.Text(chat["title"], color="white", size=14, no_wrap=True),
                padding=12, 
                border_radius=8,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.3 if is_active else 0.15, "white")),
                bgcolor="#5A1B8A" if is_active else None, 
                animate=ft.Animation(150, curve=ft.AnimationCurve.EASE_OUT), 
                data=chat["id"], 
                # 🚀 THE FIX: We bind ctitle as a default argument right next to cid!
                on_click=lambda e, cid=chat["id"], ctitle=chat["title"]: self.load_historical_chat(cid, ctitle=ctitle),
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

    def load_historical_chat(self, conversation_id, ctitle="Uploaded Document"):
        print(f"Loading old chat: {conversation_id}")
        self.current_conversation_id = conversation_id
        self.update_sidebar_selection()

        is_processing = conversation_id in self.processing_chats

        self.document_urls = {
            "Document": None,
            "Explanation": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "Transcript":  "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "Quiz": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "Audio": "audio.mp3" 
        }

        if self.body_col:
            self.body_col.controls[0] = top_bar(active_step=2 if is_processing else 3)

        self.shield.visible = is_processing
        self.empty_shield.visible = False

        if self.inner_row:
            self.inner_row.controls[1] = ft.Stack(
                controls=[
                    right_panel(self.audio, on_view_change=self.handle_view_change, has_materials=not is_processing),
                    self.shield,
                    self.empty_shield,
                ],
            )
        
        try:
            res = requests.get(
                f"http://localhost:8000/chat/{conversation_id}/documents",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            if res.status_code == 200:
                fetched_urls = res.json()
                
                for key, val in fetched_urls.items():
                    if val is not None:
                        self.document_urls[key] = val
                
                if not self.viewer_ref.current:
                    self.viewer_ref.current = PdfViewer(document_urls=self.document_urls, document_title=ctitle)
                    self.inner_row.controls[0] = ft.Container(
                        content=self.viewer_ref.current,
                        expand=True,
                        padding=ft.Padding.only(left=48, right=48, top=40, bottom=40)
                    )
                    self.page.update() 
                else: 
                    self.viewer_ref.current.document_title = ctitle
                    self.viewer_ref.current.document_urls = self.document_urls
                
                self.viewer_ref.current.load_pdf(doc_type="Document")

                try:
                    self.audio.pause()
                except Exception:
                    pass

                new_audio_url = self.document_urls.get("Audio")
                self.audio.src = new_audio_url if new_audio_url else "audio.mp3"

                if self.audio.page:
                    self.audio.update()

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

    def start_new_conversation(self, e=None):
        # 1. Generate a brand new conversation ID
        self.current_conversation_id = str(uuid.uuid4())
        
        # 2. Reset the URLs back to default
        self.document_urls = {
            "Document": None,
            "Explanation": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "Transcript":  "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "Quiz": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "Audio": "audio.mp3",
        }
        
        # 3. Nuke the old PDF viewer reference so it builds fresh next time
        self.viewer_ref = ft.Ref[PdfViewer]()
        
        # 4. Swap the Upload UI back in!
        upload_zone = main_area(on_file_accepted=self.accepted, auth_token=self.auth_token)
        self.inner_row.controls[0] = upload_zone
        self.body_col.controls[0] = top_bar(active_step=1)

        try:
            self.audio.pause()
            self.audio.src = "audio.mp3"
            if self.audio.page:
                self.audio.update()

        except Exception:
            pass

        self.inner_row.controls[1] = ft.Stack(
            controls=[
                right_panel(self.audio, on_view_change=self.handle_view_change, has_materials=False),
                self.shield,
                self.empty_shield,
            ]
        )
        self.shield.visible = False
        self.empty_shield.visible = True
        
        # 5. Clear the active highlight in the sidebar
        self.update_sidebar_selection()
        self.page.update()

    def wait_for_ai_generation(self, target_convo_id):
        time.sleep(20) 

        self.processing_chats.discard(target_convo_id)
        if self.current_conversation_id == target_convo_id:
            self.refresh_documents()
            
            if self.body_col:
                self.body_col.controls[0] = top_bar(active_step=3)
                
            if self.inner_row:
                self.inner_row.controls[1] = ft.Stack(
                    controls=[
                        right_panel(self.audio, on_view_change=self.handle_view_change, has_materials=True),
                        self.shield,
                        self.empty_shield
                    ]
                )
                
            self.shield.visible = False

            success_snack = ft.SnackBar(
                content=ft.Text("Your materials are ready!", color="white", weight=ft.FontWeight.W_600),
                bgcolor="#E96486",
                behavior=ft.SnackBarBehavior.FLOATING
            )
            self.page.overlay.append(success_snack)
            success_snack.open = True
            
            self.page.update()

        self.fetch_history()

    def refresh_documents(self):
        try:
            res = requests.get(
                f"http://localhost:8000/chat/{self.current_conversation_id}/documents",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            if res.status_code == 200:
                fetched_urls = res.json()
                for key, val in fetched_urls.items():
                    if val is not None:
                        self.document_urls[key] = val
                
                # Push the new URLs to the viewer silently in the background
                if self.viewer_ref.current:
                    self.viewer_ref.current.document_urls = self.document_urls
                
                new_audio_url = self.document_urls.get("Audio")
                if new_audio_url and new_audio_url != "audio.mp3":
                    self.audio.src = new_audio_url
                    if self.audio.page:
                        self.audio.update()

        except Exception as e:
            print(f"Error refreshing documents: {e}")

    def show_locked_warning(self, e):
        warning_snack = ft.SnackBar(
            content=ft.Text("Hold tight! We are currently generating your materials...", color="white"),
            bgcolor="#E96486",
            behavior=ft.SnackBarBehavior.FLOATING,
            duration=3000
        )
        self.page.overlay.append(warning_snack)
        warning_snack.open = True
        self.page.update()

    def handle_view_change(self, doc_type: str):
        if self.current_conversation_id in self.processing_chats and doc_type != "Document":
            self.show_locked_warning(None)
            return
            
        if self.viewer_ref.current:
            self.viewer_ref.current.load_pdf(doc_type=doc_type)
            self.page.update()

    def show_empty_warning(self, e):
        empty_snack = ft.SnackBar(
            content=ft.Text("You haven't uploaded any documents yet!", color="white"),
            bgcolor="#E96486", 
            behavior=ft.SnackBarBehavior.FLOATING,
            duration=3000
        )
        self.page.overlay.append(empty_snack)
        empty_snack.open = True
        self.page.update()