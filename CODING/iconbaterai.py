# import flet as ft


# def main(page: ft.Page):
#     # Contoh data persentase baterai
#     battery_percent = 75

#     # Menentukan ikon berdasarkan persentase baterai
#     if battery_percent > 75:
#         battery_icon = ft.icons.BATTERY_FULL
#         battery_color = ft.colors.GREEN
#     elif battery_percent > 50:
#         battery_icon = ft.icons.BATTERY_3_BAR
#         battery_color = ft.colors.LIGHT_GREEN
#     elif battery_percent > 25:
#         battery_icon = ft.icons.BATTERY_2_BAR
#         battery_color = ft.colors.YELLOW
#     elif battery_percent > 10:
#         battery_icon = ft.icons.BATTERY_1_BAR
#         battery_color = ft.colors.ORANGE
#     else:
#         battery_icon = ft.icons.BATTERY_ALERT
#         battery_color = ft.colors.RED

#     # Membuat elemen UI untuk indikator baterai
#     battery_indicator = ft.Row(
#         controls=[
#             ft.Icon(name=battery_icon, color=battery_color, size=50),
#             ft.Text(f"{battery_percent}%", size=24,
#                     weight=ft.FontWeight.BOLD)
#         ],
#     )

#     # Menambahkan indikator baterai ke halaman
#     page.add(battery_indicator)


# # Menjalankan aplikasi Flet
# if __name__ == "__main__":
#     ft.app(target=main)


import flet as ft
import psutil
import threading
import time


def main(page: ft.Page):
    # Fungsi untuk memperbarui status baterai
    def update_battery_status():
        while True:
            battery = psutil.sensors_battery()
            percent = battery.percent
            status = "Charging" if battery.power_plugged else "Not Charging"

            battery_label.value = f"Battery Status: {status} ({percent}%)"
            # Progress bar menerima nilai antara 0-1
            battery_progress.value = percent / 100

            page.update()
            time.sleep(5)  # Perbarui setiap 5 detik

    # Elemen UI
    battery_label = ft.Text()
    battery_progress = ft.ProgressBar(width=300, height=20)

    # Layout halaman
    page.add(
        ft.Column(
            [
                battery_label,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    # Jalankan fungsi update status baterai di thread terpisah
    threading.Thread(target=update_battery_status, daemon=True).start()


# Jalankan aplikasi
ft.app(target=main)
