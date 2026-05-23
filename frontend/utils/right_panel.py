import flet as ft
from utils.components import *
from flet_audio import Audio
import flet_audio as fta
import time
import asyncio

def right_panel(audio: Audio, on_view_change=None):
    div = ft.Divider(color="#B3D3D6", height=1, thickness=1)

    is_view_clicked = [False]

    def format_time(millis):
        if not millis: return "0:00"
        seconds = int((millis / 1000) % 60)
        minutes = int((millis / (1000 * 60)) % 60)
        return f"{minutes}:{seconds:02d}"

    def safe_get_ms(value):
        if value is None or value == "None": return 0
        if isinstance(value, int): return value
        if hasattr(value, 'in_milliseconds'): return value.in_milliseconds
        try: return int(value)
        except: return 0

    # UI Components
    progress_slider = ft.Slider(
        min=0, max=100, value=0,
        expand=True, height=6,
        active_color="#304A50", inactive_color="#8BA3A7", thumb_color="#304A50"
    )

    play_pause_btn = ft.IconButton(
        icon=ft.Icons.PLAY_ARROW_ROUNDED,
        icon_size=20,
        icon_color="#304A50",
        width=28, height=28,
        style=ft.ButtonStyle(padding=0)
    )

    position_text = ft.Text("0:00", size=10, color="#5B767C")
    duration_text = ft.Text("0:00", size=10, color="#5B767C")

    player_card = dashed_box(
        width=260, height=110,
        content=ft.Column([
            ft.Icon(ft.Icons.MIC_NONE_ROUNDED, color="#5B767C", size=28),
            ft.Row([
                play_pause_btn,
                progress_slider,
                ft.Row([position_text, ft.Text("–", size=10, color="#5B767C"), duration_text], spacing=2),
            ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER, width=240),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, spacing=8),
        border_color="#8BA3A7", bgcolor="#A5BCC0", border_radius=16
    )

    idle_card = dashed_box(
        width=260, height=110,
        content=ft.Column([
            ft.Icon(ft.Icons.MIC_NONE_ROUNDED, color="#5B767C", size=32),
            ft.Text("Upload a document to\ngenerate audio", size=11, color="#5B767C", text_align=ft.TextAlign.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, spacing=6),
        border_color="#8BA3A7", bgcolor="#A5BCC0", border_radius=16
    )

    playback_slot = ft.Container(content=idle_card, width=260, height=110)
    # === STATE TRACKING ===
        # === STATE TRACKING ===
    is_playing = [False]
    is_dragging = [False]

    # === Audio Handlers ===
    def on_duration_change(e):
        val = safe_get_ms(getattr(e, 'duration', getattr(e, 'data', 0)))
        if val > 0:
            progress_slider.max = val
            duration_text.value = format_time(val)
            if is_view_clicked[0]:
                playback_slot.update()

    def on_position_change(e):
        if is_dragging[0]:
            return  # Completely ignore during drag
            
        val = safe_get_ms(getattr(e, 'position', getattr(e, 'data', 0)))
        if val <= (progress_slider.max or 100):
            progress_slider.value = val
            position_text.value = format_time(val)
            if is_view_clicked[0]:
                try:
                    playback_slot.update()
                except:
                    pass

    def on_state_change(e):
        state = str(getattr(e, 'state', getattr(e, 'data', ''))).lower()
        if "playing" in state:
            is_playing[0] = True
            play_pause_btn.icon = ft.Icons.PAUSE_ROUNDED
        else:
            is_playing[0] = False
            play_pause_btn.icon = ft.Icons.PLAY_ARROW_ROUNDED

        if is_view_clicked[0]:
            try:
                playback_slot.update()
            except:
                pass

    # Attach handlers
    audio.on_duration_change = on_duration_change
    audio.on_position_change = on_position_change
    audio.on_state_change = on_state_change
    audio.release_mode = fta.ReleaseMode.STOP

    # === FIXED TOGGLE ===
    async def toggle_play_pause(e):
        try:
            if not is_playing[0]:
                print("▶ Playing / Resuming...")
                await audio.resume()
            else:
                print("⏸ Pausing...")
                await audio.pause()
        except Exception as ex:
            print(f"❌ Audio Error: {ex}")

    # === SLIDER FIX (Most Important) ===
    # === FIXED SLIDER - Final Balanced Version ===
    async def slider_changed(e):
        is_dragging[0] = False
        try:
            new_pos = int(e.control.value)
            print(f"🔍 Seeking to: {new_pos}ms")

            was_playing = is_playing[0]

            # Pause + Seek + Resume strategy (most stable)
            if was_playing:
                await audio.pause()

            await audio.seek(ft.Duration(milliseconds=new_pos))
            await asyncio.sleep(0.12)   # Small settle time

            if was_playing:
                await audio.resume()
                print("✅ Resumed after seek")
            else:
                print("✅ Seeked (was paused)")

        except Exception as ex:
            print("Seek error:", ex)

    def on_slider_change_start(e):
        is_dragging[0] = True
        print("Dragging started")

    play_pause_btn.on_click = toggle_play_pause
    progress_slider.on_change_start = on_slider_change_start
    progress_slider.on_change_end = slider_changed

    async def view_audio(e=None):
        is_view_clicked[0] = True
        playback_slot.content = player_card
        playback_slot.update()

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
                        on_view=view_audio, 
                        on_download=download_file,
                    ),
                    PanelHoverButton(
                        ft.Icons.TEXT_FIELDS_ROUNDED, "Transcript",
                        on_view=lambda e: on_view_change("/dummy.pdf") if on_view_change else None,
                        on_download=download_file,
                    ),
                ),
                div,

                ft.Text("Document Overview & Quiz", size=15, weight=ft.FontWeight.W_600, color="#304A50"),
                ft.Text("You haven't uploaded any documents yet.", size=12, color="#6B858B"),

                ft.Text("View & Download", size=14, weight=ft.FontWeight.W_600, color="#304A50"),
                button_row(
                    PanelHoverButton(
                        ft.Icons.DESCRIPTION_OUTLINED, "Explanation",
                        on_view=lambda e: on_view_change("/dummy.pdf") if on_view_change else None,
                        on_download=download_file,
                    ),
                    PanelHoverButton(
                        ft.Icons.MENU_BOOK_ROUNDED, "Quiz",
                        on_view=lambda e: on_view_change("/dummy.pdf") if on_view_change else None,
                        on_download=download_file,
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