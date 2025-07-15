import sys
import cv2
import base64
import psutil
import asyncio
import screen_brightness_control as sbc
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QSlider, QPushButton, QWidget, QHBoxLayout, QStackedWidget, QGridLayout, QSizePolicy, QAction, QMenu, QMenuBar
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont


class CameraThread(QThread):
    update_frame = pyqtSignal(QImage)
    update_battery = pyqtSignal(int, bool)

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)
        self.cliplimit = 1
        self.scale = 1
        self.running = True

    def run(self):
        while self.running:
            value = int(self.cliplimit)
            ret, frame = self.cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            clahe = cv2.createCLAHE(clipLimit=value, tileGridSize=(8, 8))
            final_clahe = clahe.apply(blurred)
            height, width = final_clahe.shape
            qImg = QImage(final_clahe.data, width, height,
                          width, QImage.Format_Grayscale8)
            self.update_frame.emit(qImg)

            battery = psutil.sensors_battery()
            self.update_battery.emit(battery.percent, battery.power_plugged)
            self.msleep(100)

    def stop(self):
        self.running = False
        self.cap.release()

    def update_zoom(self, value):
        self.scale = value

    def update_kecerahan(self, value):
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, value)

    def update_kontras(self, value):
        self.cap.set(cv2.CAP_PROP_CONTRAST, value)

    def update_layar(self, value):
        sbc.set_brightness(value)

    def update_cliplimit(self, value):
        self.cliplimit = value


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Realtime Camera")
        # Set ukuran jendela utama ke 1280x720
        self.setGeometry(100, 100, 1280, 720)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.video_label = QLabel()
        self.layout.addWidget(self.video_label)

        self.camera_thread = CameraThread()
        self.camera_thread.update_frame.connect(self.set_image)
        self.camera_thread.update_battery.connect(self.update_battery_status)

        self.battery_status_text = QLabel("Battery: ")
        self.battery_icon = QLabel()
        self.charging_icon = QLabel()
        self.battery_status_text.setFont(QFont("Arial", 14))
        self.layout.addWidget(self.battery_status_text)
        self.layout.addWidget(self.battery_icon)
        self.layout.addWidget(self.charging_icon)

        self.create_controls()

        self.camera_thread.start()

    def create_controls(self):
        self.menu_layout = QVBoxLayout()
        self.menu_layout.setAlignment(Qt.AlignTop)
        self.layout.addLayout(self.menu_layout)

        self.create_menu("Brightness", self.change_brightness)
        self.create_menu("Contrast", self.change_contrast)
        self.create_menu("CLAHE Clip Limit", self.change_cliplimit)
        self.create_menu("Zoom", self.change_zoom)
        self.create_menu("Screen Brightness", self.change_screen_brightness)

    def create_menu(self, title, slot):
        menu = QVBoxLayout()
        menu.setAlignment(Qt.AlignTop)
        label = QLabel(title)
        label.setAlignment(Qt.AlignLeft)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(1, 100)
        slider.setValue(50)
        slider.valueChanged.connect(slot)
        menu.addWidget(label)
        menu.addWidget(slider)
        self.menu_layout.addLayout(menu)

    def set_image(self, qImg):
        self.video_label.setPixmap(QPixmap.fromImage(qImg))

    def update_battery_status(self, percent, plugged):
        self.battery_status_text.setText(f"Battery: {percent}%")
        if plugged:
            self.charging_icon.setPixmap(QPixmap("bolt.png"))
        else:
            self.charging_icon.clear()

        if percent >= 80:
            self.battery_icon.setPixmap(QPixmap("battery_full.png"))
        elif percent >= 60:
            self.battery_icon.setPixmap(QPixmap("battery_6_bar.png"))
        elif percent >= 40:
            self.battery_icon.setPixmap(QPixmap("battery_4_bar.png"))
        elif percent >= 20:
            self.battery_icon.setPixmap(QPixmap("battery_2_bar.png"))
        else:
            self.battery_icon.setPixmap(QPixmap("battery_0_bar.png"))

    def change_brightness(self, value):
        self.camera_thread.update_kecerahan(value)

    def change_contrast(self, value):
        self.camera_thread.update_kontras(value)

    def change_cliplimit(self, value):
        self.camera_thread.update_cliplimit(value)

    def change_zoom(self, value):
        self.camera_thread.update_zoom(value)

    def change_screen_brightness(self, value):
        self.camera_thread.update_layar(value)

    def closeEvent(self, event):
        self.camera_thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
