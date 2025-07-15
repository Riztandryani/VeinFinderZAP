from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QSlider, QWidget, QHBoxLayout, QSpacerItem, QSizePolicy, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QEvent, QSize
from PyQt5.QtGui import QPixmap, QImage, QIcon
import sys
import cv2
import screen_brightness_control as sbc
import os
import platform


class CameraThread(QThread):
    update_frame = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)
        self.cliplimit = 10.0
        self.scale = 1.0
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 32)
        self.cap.set(cv2.CAP_PROP_CONTRAST, 43)
        self.running = True

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = self.apply_adjustments(frame)
                desired_width = 2300  # Ubah sesuai kebutuhan Anda
                desired_height = 1400  # Ubah sesuai kebutuhan Anda
                frame = cv2.resize(frame, (desired_width, desired_height))
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                qImg = QImage(frame.data, width, height,
                              bytes_per_line, QImage.Format_RGB888).rgbSwapped()
                self.update_frame.emit(qImg)
            self.msleep(100)

    def stop(self):
        self.running = False
        self.cap.release()

    def update_cliplimit(self, value):
        self.cliplimit = value

    def update_zoom(self, value):
        self.scale = value

    def update_brightness(self, value):
        try:
            sbc.set_brightness(value)
        except Exception as e:
            print(f"Error setting screen brightness: {e}")

    def apply_adjustments(self, frame):
        # Convert frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply CLAHE
        clahe = cv2.createCLAHE(clipLimit=self.cliplimit, tileGridSize=(8, 8))
        clahe_image = clahe.apply(gray_frame)

        # Apply zoom
        zoom_factor = self.scale
        if zoom_factor > 1:
            clahe_image = self.zoom_frame(clahe_image, zoom_factor)

        # Convert back to BGR for displaying
        return cv2.cvtColor(clahe_image, cv2.COLOR_GRAY2BGR)

    def zoom_frame(self, frame, zoom_factor):
        center_x, center_y = frame.shape[1] // 2, frame.shape[0] // 2
        radius_x, radius_y = int(
            center_x / zoom_factor), int(center_y / zoom_factor)

        min_x, max_x = center_x - radius_x, center_x + radius_x
        min_y, max_y = center_y - radius_y, center_y + radius_y

        cropped_frame = frame[min_y:max_y, min_x:max_x]
        frame = cv2.resize(cropped_frame, (frame.shape[1], frame.shape[0]))

        return frame


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Realtime Camera with PyQt5")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("background-color: white;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)

        # Layout for video display
        self.video_label = QLabel()
        self.main_layout.addWidget(self.video_label)

        # Layout for controls
        self.controls_widget = QWidget()
        self.controls_layout = QVBoxLayout(self.controls_widget)
        self.controls_layout.setAlignment(
            Qt.AlignTop)  # Align controls to the top

        self.create_controls()
        self.main_layout.addWidget(self.controls_widget)

        self.central_widget.setLayout(self.main_layout)

        self.camera_thread = CameraThread()
        self.camera_thread.update_frame.connect(self.set_image)
        self.camera_thread.start()

        self.installEventFilter(self)

        self.showFullScreen()  # Set to fullscreen

    def create_controls(self):
        # Battery icon
        self.battery_label = QLabel()
        self.battery_label.setPixmap(
            QPixmap("melanveer.png").scaledToHeight(200))
        self.battery_label.setFixedSize(200, 200)
        self.battery_label.setScaledContents(True)
        self.controls_layout.addWidget(
            self.battery_label, alignment=Qt.AlignCenter)  # Align center vertically

        # Jika ingin menambahkan icon terbaru
        # Additional icon below the battery
        # self.additional_icon_label = QLabel()
        # self.additional_icon_label.setPixmap(
        #     QPixmap("logo_mela.png").scaledToHeight(200))
        # self.additional_icon_label.setFixedSize(200, 200)
        # self.additional_icon_label.setScaledContents(True)
        # self.controls_layout.addWidget(
        #     self.additional_icon_label, alignment=Qt.AlignCenter)  # Align center vertically

        # Spacer item to create space between battery icon and sliders
        battery_spacer = QSpacerItem(
            10, 200, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.controls_layout.addItem(battery_spacer)

        # Sliders for brightness, CLAHE, and zoom
        self.create_slider("brightness.png", "BRIGHTNESS",
                           self.change_brightness, 0, 100, 50)
        self.create_slider("vena.png", "CONTRAS",
                           self.change_cliplimit, 1, 10, 2)
        self.create_slider("zoom.png", "ZOOM", self.change_zoom, 1, 3, 1)

        # Add a spacer before the shutdown button
        power_icon_spacer = QSpacerItem(
            20, 100, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.controls_layout.addItem(power_icon_spacer)

        # Shutdown button with icon
        self.shutdown_button = QPushButton()
        self.shutdown_button.setIcon(QIcon("power.png"))
        self.shutdown_button.setIconSize(QSize(100, 100))  # Icon size
        self.shutdown_button.setFixedSize(120, 120)  # Button size
        self.shutdown_button.setStyleSheet(
            "background-color: transparent; border: none;")
        self.shutdown_button.clicked.connect(self.confirm_shutdown)
        self.controls_layout.addWidget(
            self.shutdown_button, alignment=Qt.AlignCenter)

    def create_slider(self, icon_path, label_text, slot, min_value, max_value, default_value):
        # Vertical layout for each slider
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)  # Align contents center vertically

        # Icon label
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(icon_path).scaledToHeight(50))
        icon_label.setFixedSize(120, 120)
        icon_label.setScaledContents(True)
        layout.addWidget(icon_label, alignment=Qt.AlignCenter)

        # Label for the slider
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label, alignment=Qt.AlignCenter)

        # Horizontal layout for buttons and slider
        h_layout = QHBoxLayout()

        # Minus button
        minus_button = QPushButton("-")
        minus_button.setFixedSize(40, 40)
        minus_button.clicked.connect(lambda: slider.setValue(
            max(slider.value() - 1, min_value)))
        h_layout.addWidget(minus_button)

        # Slider
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_value, max_value)
        slider.setValue(default_value)
        # Connect slider's valueChanged signal to the slot
        slider.valueChanged.connect(slot)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 80px;
                background: #DDDDDD;
            }
            QSlider::handle:horizontal {
                width: 20px;
                height: 20px;
                background: #4CAF50;
                margin: -6px 0;
                border-radius: 10px;
            }
        """)
        h_layout.addWidget(slider)

        # Plus button
        plus_button = QPushButton("+")
        plus_button.setFixedSize(40, 40)
        plus_button.clicked.connect(lambda: slider.setValue(
            min(slider.value() + 1, max_value)))
        h_layout.addWidget(plus_button)

        layout.addLayout(h_layout)

        # Set fixed width for the layout widget
        layout_widget = QWidget()
        layout_widget.setFixedWidth(200)  # Adjust this width as needed
        layout_widget.setLayout(layout)

        # Add layout widget to main layout
        self.controls_layout.addWidget(layout_widget)

    def set_image(self, qImg):
        self.video_label.setPixmap(QPixmap.fromImage(qImg))

    def change_brightness(self, value):
        self.camera_thread.update_brightness(value)

    def change_cliplimit(self, value):
        self.camera_thread.update_cliplimit(value)

    def change_zoom(self, value):
        self.camera_thread.update_zoom(value)

    def confirm_shutdown(self):
        reply = QMessageBox.question(self, 'Shutdown',
                                     "Are you sure you want to shut down?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.shutdown_system()

    def shutdown_system(self):
        operating_system = platform.system()
        if operating_system == "Linux":
            os.system("sudo shutdown now")  # Command for Linux
        elif operating_system == "Windows":
            os.system("shutdown /s /t 1")  # Command for Windows
        else:
            QMessageBox.warning(
                self, "Unsupported OS", "Shutdown is not supported on this operating system.")

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Q:
                self.close()  # Close the application when Escape is pressed
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        self.camera_thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
