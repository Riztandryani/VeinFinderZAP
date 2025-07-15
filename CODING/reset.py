import flet as ft


def main(page: ft.Page):
    page.title = "Aplikasi Flet dengan Fitur Reset"

    # Definisikan kontrol gambar dan teks
    img = ft.Image(
        # Ganti dengan URL gambar atau path lokal
        src="tangan.jpg",
        width=300,
        height=200,
        fit=ft.ImageFit.COVER
    )
    text = ft.Text(value="Selamat datang di aplikasi Flet!", size=20)

    # Fungsi untuk mereset gambar dan teks
    def reset_content(e):
        img.src = "logo.png"  # Reset ke URL gambar awal
        text.value = "Selamat datang di aplikasi Flet!"  # Reset ke teks awal
        page.update()

    # Buat tombol reset
    reset_button = ft.ElevatedButton(text="Reset", on_click=reset_content)

    # Tambahkan kontrol ke halaman
    page.controls.extend([img, text, reset_button])

    # Update halaman untuk menampilkan perubahan
    page.update()


# Jalankan aplikasi
ft.app(target=main)
