import flet as ft
import asyncio
import cv2
import base64
import screen_brightness_control as sbc
import psutil

is_button_pencerahan_visible = False
is_button_zoom_visible = False
is_button_clahe_visible = False
is_button_on_visible = False

scale = 10


class RealtimeCam(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(1)
        self.cliplimit = 5
        self.scale = 1
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 180)
        self.cap.set(cv2.CAP_PROP_CONTRAST, 200)

    async def update_zoom(self):
        value = int(self.scale)
        ret, frame = self.cap.read()
        height, width, _ = frame.shape
        centerX, centerY = int(height / 2), int(width / 2)
        radiusX, radiusY = int(value * height / 100), int(value * width / 100)

        minX, maxX = centerX - radiusX, centerX + radiusX
        minY, maxY = centerY - radiusY, centerY + radiusY

        cropped = frame[minX:maxX, minY:maxY]
        resized_cropped = cv2.resize(cropped, (width, height))
        return resized_cropped

    async def update_kecerahan(self, value):
        value = int(value)
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, value)

    async def update_layar(self, layar):
        layar = int(layar)
        sbc.set_brightness(layar)

    async def did_mount_async(self):
        self.running = True
        asyncio.create_task(self.update_cam())

    async def will_unmount_async(self):
        self.running = False

    async def update_cam(self):
        while self.running:
            value = int(self.cliplimit)
            ret, frame = self.cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=value)
            final_clahe = clahe.apply(gray)
            retval, buffer = cv2.imencode('.jpg', final_clahe)
            img_base64 = base64.b64encode(buffer).decode()
            self.realtime_video.src_base64 = img_base64
            await self.update_async()
            await asyncio.sleep(0.1)

    def build(self):
        self.realtime_video = ft.Image(
            src_base64='',
            width=2000,
            height=1000,
            fit=ft.ImageFit.FILL,
        )
        return self.realtime_video


async def main(page: ft.Page):
    video_cam = RealtimeCam()

    async def get_battery_status():
        battery = psutil.sensors_battery()
        return battery.percent, battery.power_plugged

    battery_status_text = ft.Text("", size=20)
    battery_icon = ft.Icon(name=ft.icons.BATTERY_FULL,
                           size=50, color=ft.colors.GREEN)

    async def update_battery_status():
        while True:
            percent, plugged = await get_battery_status()
            battery_status_text.value = f"{percent}%"

            if percent >= 80:
                battery_icon.name = ft.icons.BATTERY_FULL
                battery_icon.color = ft.colors.GREEN
            elif percent >= 60:
                battery_icon.name = ft.icons.BATTERY_6_BAR
                battery_icon.color = ft.colors.LIGHT_GREEN
            elif percent >= 40:
                battery_icon.name = ft.icons.BATTERY_4_BAR
                battery_icon.color = ft.colors.YELLOW
            elif percent >= 20:
                battery_icon.name = ft.icons.BATTERY_2_BAR
                battery_icon.color = ft.colors.ORANGE
            else:
                battery_icon.name = ft.icons.BATTERY_0_BAR
                battery_icon.color = ft.colors.RED

            await page.update_async()
            await asyncio.sleep(10)

    asyncio.create_task(update_battery_status())

    async def button_pencerahan(e):
        global is_button_pencerahan_visible
        is_button_pencerahan_visible = not is_button_pencerahan_visible
        container_settings.visible = is_button_pencerahan_visible
        await page.update_async()

    async def button_clahe(e):
        global is_button_clahe_visible
        is_button_clahe_visible = not is_button_clahe_visible
        container_clahe.visible = is_button_clahe_visible
        await page.update_async()

    async def button_zoom(e):
        global is_button_zoom_visible
        is_button_zoom_visible = not is_button_zoom_visible
        container_zoom.visible = is_button_zoom_visible
        await page.update_async()

    async def slider_zoom(e):
        video_cam.scale = e.control.value

    async def slider_change_cliplimit(e):
        video_cam.cliplimit = e.control.value

    async def slider_kecerahan_changed(e):
        await video_cam.update_kecerahan(e.control.value)
        await page.update_async()

    async def slider_layar_changed(e):
        await video_cam.update_layar(e.control.value)
        await page.update_async()

    capture_icons_pencerahan = ft.Image(
        src="brightness.png",
        width=40,
        height=40,
        fit=ft.ImageFit.CONTAIN,
    )

    capture_icons_kontras = ft.Image(
        src="vena.png",
        width=40,
        height=40,
        fit=ft.ImageFit.CONTAIN,
    )

    capture_icons_zoom = ft.Image(
        src="zoom.png",
        width=40,
        height=40,
        fit=ft.ImageFit.CONTAIN,
    )

    page.vertical_alignment = ft.MainAxisAlignment.END

    container_settings = ft.Container(
        content=ft.Column(
            [
                ft.Column([
                    ft.Text("KECERAHAN", style=ft.TextThemeStyle.TITLE_SMALL),
                    ft.Slider(width=150, min=1, max=100,
                              divisions=100, label="{value}%", on_change=slider_layar_changed),
                ])
            ],
        ),
        visible=is_button_pencerahan_visible
    )

    container_clahe = ft.Container(
        content=ft.Column(
            [
                ft.Column([
                    ft.Text("CONTRAS", style=ft.TextThemeStyle.TITLE_SMALL),
                    ft.Slider(width=150, min=1, max=27,
                              divisions=9, label="{value}", on_change=slider_change_cliplimit),
                ])
            ],
        ),
        visible=is_button_clahe_visible
    )

    container_zoom = ft.Container(
        content=ft.Column(
            [
                ft.Column([
                    ft.Text("ZOOM", style=ft.TextThemeStyle.TITLE_SMALL),
                    ft.Slider(width=150, min=1, max=5,
                              divisions=5, label="{value}x", on_change=slider_zoom),
                ])
            ],
        ),
        visible=is_button_zoom_visible
    )

    main_stack = ft.Stack(
        [
            video_cam,
            ft.ResponsiveRow(
                [
                    ft.Container(
                        height=850,
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        battery_icon,
                                        battery_status_text,
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.Column([
                                    ft.IconButton(
                                        content=capture_icons_pencerahan,
                                        icon=capture_icons_pencerahan,
                                        icon_size=30,
                                        on_click=button_pencerahan,
                                        bgcolor="WHITE"
                                    ),
                                    container_settings,
                                    ft.IconButton(
                                        content=capture_icons_kontras,
                                        icon=capture_icons_kontras,
                                        icon_size=30,
                                        on_click=button_clahe,
                                        bgcolor="WHITE"
                                    ),
                                    container_clahe,
                                    ft.IconButton(
                                        content=capture_icons_zoom,
                                        icon=capture_icons_zoom,
                                        icon_size=30,
                                        on_click=button_zoom,
                                        bgcolor="WHITE"
                                    ),
                                    container_zoom,
                                ])
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                        )
                    ),
                ],
            )
        ],
    )

    splash = ft.Image(
        src="logosplash.png",
        width=2000,
        height=1000,
        fit=ft.ImageFit.CONTAIN,
    )

    await page.add_async(splash)
    await asyncio.sleep(3)
    await page.remove_async(splash)
    await page.add_async(main_stack)

ft.app(target=main)
