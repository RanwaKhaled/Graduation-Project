import flet as ft
import httpx
import base64
import fitz  # PyMuPDF
import threading # 🚀 Needed to unblock the UI!

class PdfViewer(ft.Container):
    def __init__(self, document_urls: dict, **kwargs):
        super().__init__(**kwargs)
        self.expand = True
        self.bgcolor = "#FFFFFF"
        self.border_radius = 12
        self.padding = 24
        
        self.document_urls = document_urls
        self.current_doc_type = "Document"

        self.title_text = ft.Text("Uploaded Document", size=20, weight=ft.FontWeight.W_700, color="#2D2D2D")

        self.toggle_btn = ft.FilledButton(
            "Back to Uploaded Document",
            icon=ft.Icons.RESTORE_PAGE_ROUNDED,
            on_click=self.show_original,
            visible=False,
            style=ft.ButtonStyle(bgcolor="#F15C22", color="white")
        )

        self.header_row = ft.Row([self.title_text, self.toggle_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.page_list = ft.Column(expand=True, spacing=20, scroll=ft.ScrollMode.AUTO)
        
        self.viewer_container = ft.Container(
            content=self.page_list,
            expand=True,
            border=ft.Border.all(1.5, "#EBEBEB"),
            border_radius=8,
            bgcolor="#F8F9FA"
        )

        self.content = ft.Column([self.header_row, self.viewer_container], expand=True, spacing=16)

    def did_mount(self):
        self.load_pdf(doc_type="Document")

    def load_pdf(self, doc_type: str):
        target_url = self.document_urls.get(doc_type)
        if not target_url:
            return

        self.current_doc_type = doc_type
        
        if doc_type == "Document":
            self.title_text.value = "Uploaded Document"
            self.toggle_btn.visible = False
        else:
            self.title_text.value = f"Generated {doc_type}"
            self.toggle_btn.visible = True

        self.title_text.update()
        self.toggle_btn.update()

        # --- THE POLISHED LOADING SPINNER ---
        self.page_list.controls.clear()
        self.page_list.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.ProgressRing(color="#4A1587", stroke_width=4, width=40, height=40), 
                    ft.Text("Loading your document...", size=15, weight=ft.FontWeight.W_600, color="#4A1587")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                alignment=ft.Alignment.CENTER,
                expand=True,
                padding=ft.Padding(0, 150, 0, 0) # Pushes it neatly into the center of the viewer
            )
        )
        self.page_list.update()

        # 🚀 FIRE AND FORGET: Hand the heavy work to a background thread!
        threading.Thread(target=self._process_pdf_background, args=(target_url,), daemon=True).start()


    def _process_pdf_background(self, target_url):
        """This entirely runs in the background. The main UI thread is now completely free to animate the loading ring."""
        try:
            print(f"🖼️ Rendering PDF directly to Images: {target_url}")
            
            # 1. Download the PDF bytes
            response = httpx.get(target_url, follow_redirects=True)
            response.raise_for_status()
            
            # 2. Open the PDF in memory using PyMuPDF
            doc = fitz.open(stream=response.content, filetype="pdf")
            
            # Create a temporary list so we don't force Flet to redraw 50 times during the loop
            new_pages = []
            
            # 3. Take a picture of every page
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)) 
                img_bytes = pix.tobytes("png")
                b64_img = base64.b64encode(img_bytes).decode("utf-8")
                
                new_pages.append(
                    ft.Image(
                        src=f"data:image/png;base64,{b64_img}", 
                        fit="contain",
                        border_radius=4,
                    )
                )
            
            # 4. We are done! Swap the loading spinner for the images
            self.page_list.controls.clear()
            self.page_list.controls.extend(new_pages)
            
            # Safety check in case the user routed away before it finished downloading
            if self.page_list.page:
                self.page_list.update()
                
            print("✅ Native rendering complete!")
            
        except Exception as e:
            print(f"❌ Error rendering document: {e}")
            self.page_list.controls.clear()
            self.page_list.controls.append(
                ft.Container(
                    content=ft.Text(f"Failed to load document: {e}", color="red", weight=ft.FontWeight.BOLD),
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding(0, 50, 0, 0)
                )
            )
            if self.page_list.page:
                self.page_list.update()


    def show_original(self, e):
        self.load_pdf(doc_type="Document")