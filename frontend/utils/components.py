import math
import flet as ft
import flet.canvas as cv
from .upload_zone import UploadZone
from .panel_hover import PanelHoverButton
import flet_audio
from flet_audio import Audio, ReleaseMode


SIDEBAR_BG = "#321664"   
TOPBAR_BG = "#FFFFFF"   
MAIN_BG = "#FFFFFF"
PANEL_BG = "#DDF2F4"   
ORANGE = "#F15C22"   
ORANGE_PALE = "#FFAE8F"   
PURPLE = "#6B3FA0"
PURPLE_LIGHT = "#F4EEF9"   
TEXT_DARK = "#1A1A2E"
TEXT_GREY = "#5A6475"
TEXT_PURPLE = "#4A1587"

def dashed_box(width, height, content, border_color, border_thickness=1.5, dash_len=10, gap_len=8, bgcolor=None, border_radius=16):
    elements = []
    
    def add_dashed_line(x1, y1, x2, y2):
        length = math.hypot(x2 - x1, y2 - y1)
        if length == 0: return
        dx, dy = (x2 - x1) / length, (y2 - y1) / length
        curr = 0
        drawing = True
        elements.append(cv.Path.MoveTo(x1, y1))
        
        while curr < length:
            step = min(dash_len if drawing else gap_len, length - curr)
            next_x = x1 + dx * (curr + step)
            next_y = y1 + dy * (curr + step)
            if drawing:
                elements.append(cv.Path.LineTo(next_x, next_y))
            else:
                elements.append(cv.Path.MoveTo(next_x, next_y))
            curr += step
            drawing = not drawing

    inset = border_thickness / 2
    right = width - inset
    bottom = height - inset
    
    add_dashed_line(inset, inset, right, inset)      
    add_dashed_line(right, inset, right, bottom)     
    add_dashed_line(right, bottom, inset, bottom)    
    add_dashed_line(inset, bottom, inset, inset)     

    dashed_canvas = cv.Canvas(
        [
            cv.Path(
                elements=elements,
                paint=ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=border_thickness, color=border_color)
            )
        ],
        width=width, height=height,
    )

    return ft.Stack(
        [
            ft.Container(
                width=width, height=height,
                bgcolor=bgcolor,
                border_radius=border_radius,
                content=dashed_canvas,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS, 
            ),
            ft.Container(
                width=width, height=height,
                content=content,
                alignment=ft.Alignment.CENTER,
            )
        ],
        width=width, height=height,
    )


def step_badge(number: int, label: str, active: bool = False):
    badge = ft.Container(
        content=ft.Text(str(number), color="white", size=13, weight=ft.FontWeight.BOLD),
        width=28, height=28,
        bgcolor=ORANGE if active else ORANGE_PALE,
        border_radius=14,
        alignment=ft.Alignment.CENTER,
    )
    return ft.Row(
        [badge, ft.Text(
            label,
            size=14,
            weight=ft.FontWeight.BOLD if active else ft.FontWeight.W_500,
            color=TEXT_DARK if active else TEXT_GREY,
        )],
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

def step_connector():
    return ft.Container(width=70, height=1.5, bgcolor=TEXT_GREY, opacity=0.4)


def sidebar(on_toggle):
    return ft.Container(
        width=80, 
        bgcolor=SIDEBAR_BG,
        animate=300, 
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.MENU, color="white", size=26),
                            ft.Text("Chat History", color="white", size=15, weight=ft.FontWeight.W_600),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=50,
                    ),
                    padding=ft.Padding(left=22, right=0, top=20, bottom=0),
                    on_click=on_toggle,
                ),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.PERSON_OUTLINE, color="white", size=28),
                            ft.Text("Profile", color="white", size=15, weight=ft.FontWeight.W_600),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=30,
                    ),
                    padding=ft.Padding(left=21, right=0, top=0, bottom=24),
                ),
            ],
            spacing=0,
            expand=True,
        ),
    )

def top_bar(active_step: int = 1):
    return ft.Container(
        height=70,
        bgcolor=TOPBAR_BG,
        padding=ft.Padding(left=32, right=32, top=0, bottom=0),
        border=ft.Border(bottom=ft.BorderSide(1, "#E0E0E0")), 
        content=ft.Row(
            [
                step_badge(1, "Document Upload", active=active_step >= 1),
                step_connector(),
                step_badge(2, "Processing", active=active_step >= 2),
                step_connector(),
                step_badge(3, "Materials Ready", active=active_step >= 3),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Image(src="/logo_black.PNG", fit="contain"), 
                    width=60, height=60,
                    alignment=ft.Alignment.CENTER,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


def main_area(on_file_accepted, auth_token=None):
    def bullet(txt: str):
        return ft.Row(
            [
                ft.Container(width=4, height=4, bgcolor=TEXT_GREY, border_radius=2),
                ft.Text(txt, size=13, color=TEXT_GREY),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )

    upload_zone = UploadZone(on_file_accepted=on_file_accepted, auth_token=auth_token)

    return ft.Container(
        expand=True,
        bgcolor=MAIN_BG,
        padding=ft.Padding(left=48, right=48, top=40, bottom=40),
        content=ft.Column(
            [
                ft.Text(
                    "Upload Your Documents Below!",
                    size=28, weight=ft.FontWeight.W_700, color=TEXT_DARK, text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=10),
                ft.Container(
                    width=600,
                    content=ft.Text(
                        "Once you upload your slides, you'll be able to view them here. "
                        "Our models will then take some time to create an audio explanation "
                        "which you'll be able to listen to. You can also download a "
                        "well‑formatted, text explanation along with some model questions and answers.",
                        size=14, color=TEXT_DARK, opacity=0.8, text_align=ft.TextAlign.CENTER,
                    ),
                ),
                ft.Container(height=30),
                upload_zone,  
                ft.Container(height=16),
                ft.Container(
                    width=500, 
                    content=ft.Column(
                        [
                            bullet("Documents must be .pdf, .doc, .txt, or .pptx"),
                            bullet("Documents must not be larger than 20 MB"),
                        ],
                        spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.Alignment.CENTER,
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
    )

def right_panel(audio: Audio):
    div = ft.Divider(color="#B3D3D6", height=1, thickness=1)

    duration_ms = [0]

    def fmt(ms):
        if not ms:
            return "0:00"
        s = int(ms / 1000)
        return f"{s // 60}:{s % 60:02d}"

    def safe_get_ms(value):
        if value is None or value == "None":
            return 0
        if isinstance(value, int):
            return value
        if hasattr(value, 'in_milliseconds'):
            return value.in_milliseconds
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    # --- Player UI refs (created once, reused) ---
    play_pause_icon = ft.Ref[ft.Icon]()
    seek_slider = ft.Ref[ft.Slider]()
    time_text = ft.Ref[ft.Text]()

    def on_duration_change(e):
        val = safe_get_ms(getattr(e, 'duration', e.data))
        if val > 0:
            duration_ms[0] = val
            if seek_slider.current and seek_slider.current.page:
                seek_slider.current.max = val
                if time_text.current:
                    time_text.current.value = f"0:00 – {fmt(val)}"
                seek_slider.current.page.update()

    def on_position_change(e):
        val = safe_get_ms(getattr(e, 'position', e.data))
        if seek_slider.current and seek_slider.current.page:
            if val <= seek_slider.current.max:
                seek_slider.current.value = val
            if time_text.current:
                time_text.current.value = f"{fmt(val)} – {fmt(duration_ms[0])}"
            seek_slider.current.page.update()

    def on_state_change(e):
        if play_pause_icon.current and play_pause_icon.current.page:
            play_pause_icon.current.name = (
                ft.Icons.PAUSE_ROUNDED if e.state == "playing" else ft.Icons.PLAY_ARROW_ROUNDED
            )
            play_pause_icon.current.page.update()

    audio.on_duration_change = on_duration_change
    audio.on_position_change = on_position_change
    audio.on_state_change = on_state_change

    # --- Handlers ---
    async def on_play_pause(e):
        if play_pause_icon.current and play_pause_icon.current.name == ft.Icons.PAUSE_ROUNDED:
            await audio.pause()
        else:
            await audio.resume()

    async def on_seek(e):
        await audio.seek(ft.Duration(milliseconds=int(e.control.value)))

    # --- Player card (built once) ---
    player_card = dashed_box(
        width=260, height=110,
        content=ft.Column(
            [
                ft.Icon(ft.Icons.MIC_NONE_ROUNDED, color="#5B767C", size=28),
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.PLAY_ARROW_ROUNDED,
                                color="#304A50", size=18,
                                ref=play_pause_icon,
                            ),
                            on_click=on_play_pause,
                            width=28, height=28,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Slider(
                            ref=seek_slider,
                            min=0, max=100, value=0,
                            expand=True,
                            height=18,
                            active_color="#304A50",
                            inactive_color="#8BA3A7",
                            thumb_color="#304A50",
                            on_change_end=on_seek,
                        ),
                        ft.Text(
                            "0:00",
                            ref=time_text,
                            size=10, color="#5B767C",
                        ),
                    ],
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    width=240,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        border_color="#8BA3A7", bgcolor="#A5BCC0", border_radius=16
    )

    idle_card = dashed_box(
        width=260, height=110,
        content=ft.Column(
            [
                ft.Icon(ft.Icons.MIC_NONE_ROUNDED, color="#5B767C", size=32),
                ft.Text(
                    "Upload a document to\ngenerate audio",
                    size=11, color="#5B767C", text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
        ),
        border_color="#8BA3A7", bgcolor="#A5BCC0", border_radius=16
    )

    playback_slot = ft.Container(content=idle_card, width=260, height=110)

    async def play_audio():
        playback_slot.content = player_card
        playback_slot.update()
        await audio.play()

    def button_row(*buttons):
        return ft.Row(list(buttons), spacing=10, width=260)

    return ft.Container(
        width=300,
        bgcolor=PANEL_BG,
        padding=ft.Padding(left=20, right=20, top=24, bottom=24),
        content=ft.Column(
            [
                ft.Text("Audio Explanation", size=15, weight=ft.FontWeight.W_600, color="#304A50"),
                ft.Text("You haven't uploaded any documents yet.", size=12, color="#6B858B"),
                div,

                ft.Text("Playback", size=14, weight=ft.FontWeight.W_600, color="#304A50"),
                playback_slot,

                ft.Text("Download", size=14, weight=ft.FontWeight.W_600, color="#304A50"),
                button_row(
                    PanelHoverButton(
                        ft.Icons.MIC_NONE_ROUNDED, "Audio",
                        show_view=True,
                        on_view=play_audio,
                        on_download=lambda: print("Downloading audio..."),
                    ),
                    PanelHoverButton(
                        ft.Icons.TEXT_FIELDS_ROUNDED, "Transcript",
                        on_view=lambda: print("TODO: show transcript"),
                        on_download=lambda: print("Downloading transcript..."),
                    ),
                ),
                div,

                ft.Text("Document Overview & Quiz", size=15, weight=ft.FontWeight.W_600, color="#304A50"),
                ft.Text("You haven't uploaded any documents yet.", size=12, color="#6B858B"),

                ft.Text("View & Download", size=14, weight=ft.FontWeight.W_600, color="#304A50"),
                button_row(
                    PanelHoverButton(
                        ft.Icons.DESCRIPTION_OUTLINED, "Explanation",
                        on_view=lambda: print("TODO: show explanation PDF"),
                        on_download=lambda: print("Downloading explanation..."),
                    ),
                    PanelHoverButton(
                        ft.Icons.MENU_BOOK_ROUNDED, "Quiz",
                        on_view=lambda: print("TODO: show quiz PDF"),
                        on_download=lambda: print("Downloading quiz..."),
                    ),
                ),
                div,

                ft.Container(
                    width=260,
                    content=ft.Text(
                        "Tip: You can find all your previous explanations in your chat history!",
                        size=11, color="#5B767C",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=ft.Padding(left=12, right=12, top=12, bottom=12),
                ),
            ],
            spacing=14,
            scroll=ft.ScrollMode.AUTO,
        ),
    )

async def download_file(e):
    try:
        print("📥 Triggering direct download for dummy.pdf...")
        await e.page.launch_url("/dummy.pdf")
    except Exception as ex:
        print(f"❌ Download error: {ex}")