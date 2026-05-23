import flet as ft
import inspect

class PanelHoverButton(ft.Container):
    def __init__(self, main_icon, label, on_view=None, on_download=None, show_view=True):
        super().__init__(
            height=70,
            expand=True,
            border_radius=12,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )
        
        self.label = label
        self.on_view_cb = on_view
        self.on_download_cb = on_download

        def _icon_btn(icon, tooltip, on_click):
            return ft.Container(
                content=ft.Icon(icon, color="#304A50", size=22),
                width=36, height=36,
                border_radius=8,
                alignment=ft.Alignment.CENTER,
                tooltip=tooltip,
                on_click=on_click,
                ink=True,
            )

        self.hover_view = ft.Container(
            expand=True,
            bgcolor="#A5BCC0",
            opacity=0,
            animate_opacity=200,
            alignment=ft.Alignment.CENTER,
            content=ft.Row(
                [x for x in [
                    _icon_btn(ft.Icons.REMOVE_RED_EYE_OUTLINED, f"View {label}", self._view_clicked) if show_view else None,
                    _icon_btn(ft.Icons.DOWNLOAD_ROUNDED, f"Download {label}", self._download_clicked),
                ] if x is not None],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=4,
            )
        )

        self.base_view = ft.Container(
            expand=True,
            bgcolor="#C3D9DB",
            alignment=ft.Alignment.CENTER,
            content=ft.Column([
                ft.Icon(main_icon, color="#5B767C", size=24),
                ft.Text(label, size=12, color="#5B767C", weight=ft.FontWeight.W_500),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=4,
            expand=True,
            )
        )

        self.content = ft.GestureDetector(
            on_enter=self._on_enter,
            on_exit=self._on_exit,
            content=ft.Stack(
                [self.base_view, self.hover_view],
                expand=True,
            ),
        )

    def _on_enter(self, e):
        self.hover_view.opacity = 1
        self.hover_view.update()

    def _on_exit(self, e):
        self.hover_view.opacity = 0
        self.hover_view.update()

    async def _view_clicked(self, e):
        if self.on_view_cb:
            if inspect.iscoroutinefunction(self.on_view_cb):
                await self.on_view_cb(e)
            else:
                self.on_view_cb(e)

    async def _download_clicked(self, e):
        if self.on_download_cb:
            if inspect.iscoroutinefunction(self.on_download_cb):
                await self.on_download_cb(e)
            else:
                self.on_download_cb(e)