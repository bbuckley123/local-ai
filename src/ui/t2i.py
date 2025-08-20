import flet as ft

class T2IView:
    def __init__(self, page: ft.Page, notify) -> None:
        self.page = page
        self.notify = notify

        self.prompt = ft.TextField(label="Prompt", multiline=True, min_lines=4, expand=True)
        self.steps = ft.Slider(label="Steps", min=5, max=50, divisions=45, value=20, width=250)
        self.guidance = ft.Slider(label="Guidance (CFG)", min=1.0, max=15.0, divisions=28, value=7.5, width=250)
        self.status = ft.Text("Not wired yet.")
        self.placeholder = ft.Container(content=ft.Text("Image will appear here"), height=360, border_radius=8)
        self.btn_go = ft.ElevatedButton("Generate", on_click=self._on_go)
        self.btn_cancel = ft.OutlinedButton("Cancel", disabled=True)

        self.container = ft.Column(
            [
                self.prompt,
                ft.Row([self.steps, self.guidance], spacing=24),
                ft.Row([self.btn_go, self.btn_cancel, self.status], spacing=12),
                self.placeholder,
            ],
            expand=True,
            visible=False,
        )

    def control(self) -> ft.Control:
        return self.container

    def set_visible(self, visible: bool) -> None:
        self.container.visible = visible
        self.page.update()

    def _on_go(self, _: ft.ControlEvent) -> None:
        self.notify("Text→Image not wired yet.")
