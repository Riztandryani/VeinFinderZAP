import flet as ft
import psutil  # Library untuk mendapatkan informasi sistem seperti status baterai
import threading
import time


def main(page: ft.Page):

    # Fungsi untuk mendapatkan status baterai
    def get_battery_status():
        battery = psutil.sensors_battery()
        return battery.percent, battery.power_plugged

    # Membuat elemen teks untuk menampilkan status baterai
    battery_status_text = ft.Text("", size=20)

    # Membuat elemen ikon untuk menampilkan status baterai
    battery_icon = ft.Icon(name=ft.icons.BATTERY_FULL,
                           size=50, color=ft.colors.GREEN)

    # Fungsi untuk memperbarui status baterai
    def update_battery_status():
        while True:
            percent, plugged = get_battery_status()
            battery_status_text.value = f"Battery: {percent}% {'(Charging)' if plugged else '(Discharging)'}"

            # Mengatur ikon baterai berdasarkan persentase
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

            page.update()
            time.sleep(10)  # Menunggu 10 detik sebelum memperbarui kembali

    # Membuat thread untuk memperbarui status baterai secara berkala
    update_thread = threading.Thread(target=update_battery_status, daemon=True)
    update_thread.start()

    # Tombol untuk memperbarui status baterai secara manual

    # Menambahkan elemen ke halaman
    page.add(battery_icon)


# Jalankan aplikasi Flet
if __name__ == "__main__":
    ft.app(target=main)
