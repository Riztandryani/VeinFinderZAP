import cv2
import sys
import psutil
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout, QHBoxLayout, QSlider, QSpacerItem, QSizePolicy
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot, QTimer, QSize
from PyQt5.QtGui import QImage, QPixmap


class Thread(QThread):
    changePixmap = pyqtSignal(QImage)
    updateContrast = pyqtSignal(int)
    updateBrightness = pyqtSignal(int)
    updateZoom = pyqtSignal(int)
    updateCLAHE = pyqtSignal(int)

    def __init__(self, label_width, label_height, parent=None):
        super().__init__(parent)
        self.contrast = 1.0
        self.brightness = 0
        self.zoom = 1.0
        self.clahe_clip_limit = 2.0
        self.label_width = label_width
        self.label_height = label_height
        self.updateContrast.connect(self.setContrast)
        self.updateBrightness.connect(self.setBrightness)
        self.updateZoom.connect(self.setZoom)
        self.updateCLAHE.connect(self.setCLAHE)

    def run(self):
        self.isRunning = True
        cap = cv2.VideoCapture(0)

        while self.isRunning:
            ret, frame = cap.read()
            if ret:
                # Adjust contrast and brightness
                frame = cv2.convertScaleAbs(
                    frame, alpha=self.contrast, beta=self.brightness)

                # Apply CLAHE
                lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(
                    clipLimit=self.clahe_clip_limit, tileGridSize=(8, 8))
                cl = clahe.apply(l)
                limg = cv2.merge((cl, a, b))
                frame = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

                # Convert frame to grayscale
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Resize frame to fit label size
                label_height, label_width = self.label_height, self.label_width
                frame = cv2.resize(
                    gray_frame, (label_width, label_height), interpolation=cv2.INTER_LINEAR)

                # Convert grayscale frame to QImage
                bytesPerLine = label_width
                convertToQtFormat = QImage(
                    frame.data, label_width, label_height, bytesPerLine, QImage.Format_Grayscale8)
                p = convertToQtFormat.scaled(
                    label_width, label_height, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

        cap.release()

    def stop(self):
        self.isRunning = False
        self.quit()
        self.wait()

    def setContrast(self, contrast):
        self.contrast = contrast / 50.0

    def setBrightness(self, brightness):
        self.brightness = brightness - 50

    def setZoom(self, zoom):
        self.zoom = zoom / 10.0

    def setCLAHE(self, clahe):
        self.clahe_clip_limit = clahe / 10.0


class VideoContainer(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Video'
        self.left = 100
        self.top = 100
        self.label_width = 2250
        self.label_height = 1400
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top,
                         self.label_width, self.label_height)
        # Set the initial window size
        self.resize(self.label_width, self.label_height)

        # Create a label
        self.label = QLabel(self)
        # Set the size of the label
        self.label.setFixedSize(self.label_width, self.label_height)

        # Create sliders with icons
        self.contrast_slider = QSlider(Qt.Horizontal)  # Horizontal slider
        self.contrast_slider.setMinimum(0)
        self.contrast_slider.setMaximum(100)
        self.contrast_slider.setValue(50)  # Default contrast value

        self.brightness_slider = QSlider(Qt.Horizontal)  # Horizontal slider
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(50)  # Default brightness value

        self.zoom_slider = QSlider(Qt.Horizontal)  # Horizontal slider
        self.zoom_slider.setMinimum(10)  # Minimum zoom factor 1.0
        self.zoom_slider.setMaximum(50)  # Maximum zoom factor 5.0
        self.zoom_slider.setValue(10)    # Default zoom factor 1.0

        self.clahe_slider = QSlider(Qt.Horizontal)  # Horizontal slider
        self.clahe_slider.setMinimum(10)  # Minimum CLAHE clip limit 1.0
        self.clahe_slider.setMaximum(50)  # Maximum CLAHE clip limit 5.0
        self.clahe_slider.setValue(20)    # Default CLAHE clip limit 2.0

        # Create labels for icons
        self.contrast_icon_label = QLabel(self)
        self.brightness_icon_label = QLabel(self)
        self.zoom_icon_label = QLabel(self)
        self.clahe_icon_label = QLabel(self)

        # Set icons using QPixmap and resize them
        icon_size = QSize(180, 180)  # Set the desired icon size

        contrast_pixmap = QPixmap('contras.png').scaled(
            icon_size, Qt.KeepAspectRatio)
        brightness_pixmap = QPixmap('brightness.png').scaled(
            icon_size, Qt.KeepAspectRatio)
        zoom_pixmap = QPixmap('zoom.png').scaled(icon_size, Qt.KeepAspectRatio)
        clahe_pixmap = QPixmap('vena.png').scaled(
            icon_size, Qt.KeepAspectRatio)

        self.contrast_icon_label.setPixmap(contrast_pixmap)
        self.brightness_icon_label.setPixmap(brightness_pixmap)
        self.zoom_icon_label.setPixmap(zoom_pixmap)
        self.clahe_icon_label.setPixmap(clahe_pixmap)

        # Connect sliders to methods
        self.contrast_slider.valueChanged.connect(self.update_contrast)
        self.brightness_slider.valueChanged.connect(self.update_brightness)
        self.zoom_slider.valueChanged.connect(self.update_zoom)
        self.clahe_slider.valueChanged.connect(self.update_clahe)

        # Layout
        main_layout = QHBoxLayout()  # Horizontal layout

        video_layout = QVBoxLayout()  # Vertical layout for video label
        video_layout.addWidget(self.label)

        sliders_layout = QVBoxLayout()  # Vertical layout for sliders

        # Add icons and sliders to the layout with proper alignment
        self.add_icon_and_slider(
            self.contrast_icon_label, self.contrast_slider, sliders_layout)
        self.add_icon_and_slider(
            self.brightness_icon_label, self.brightness_slider, sliders_layout)
        self.add_icon_and_slider(self.zoom_icon_label,
                                 self.zoom_slider, sliders_layout)
        self.add_icon_and_slider(
            self.clahe_icon_label, self.clahe_slider, sliders_layout)

        # Add layouts to the main layout
        main_layout.addLayout(video_layout)
        main_layout.addLayout(sliders_layout)

        self.setLayout(main_layout)

        self.th = Thread(self.label_width, self.label_height, self)
        self.th.changePixmap.connect(self.setImage)
        self.th.start()
        self.show()

    def add_icon_and_slider(self, icon_label, slider, layout):
        # Create a layout for each pair of icon and slider
        pair_layout = QVBoxLayout()
        # Center align icon
        pair_layout.addWidget(icon_label, alignment=Qt.AlignHCenter)
        # Center align slider
        pair_layout.addWidget(slider, alignment=Qt.AlignHCenter)
        layout.addLayout(pair_layout)

    @pyqtSlot(int)
    def update_contrast(self, value):
        self.th.updateContrast.emit(value)

    @pyqtSlot(int)
    def update_brightness(self, value):
        self.th.updateBrightness.emit(value)

    @pyqtSlot(int)
    def update_zoom(self, value):
        self.th.updateZoom.emit(value)

    @pyqtSlot(int)
    def update_clahe(self, value):
        self.th.updateCLAHE.emit(value)


class BatteryIndicator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Battery Indicator')
        self.setGeometry(100, 100, 300, 200)

        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Battery Icon
        self.battery_icon_label = QLabel(self)
        # Align to top right
        layout.addWidget(self.battery_icon_label,
                         alignment=Qt.AlignTop | Qt.AlignRight)

        # Timer to update battery level every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_battery_level)
        self.timer.start(1000)  # Update every second

        self.update_battery_level()  # Initial update

    def update_battery_level(self):
        battery = psutil.sensors_battery()
        if battery:
            battery_level = battery.percent
            self.update_battery_icon(battery_level)
        else:
            self.battery_label.setText('Battery information not available')

    def update_battery_icon(self, battery_level):
        if battery_level > 80:
            icon_path = 'bat_full.png'
        elif battery_level > 60:
            icon_path = 'bat_1.png'
        elif battery_level > 40:
            icon_path = 'bat_2.png'
        elif battery_level > 20:
            icon_path = 'bat_3.png'
        else:
            icon_path = 'bat_low.png'

        pixmap = QPixmap(icon_path)
        # Resize the pixmap to a smaller size (e.g., 80x80 pixels)
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
        self.battery_icon_label.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create the main widget
    main_widget = QWidget()
    main_layout = QHBoxLayout(main_widget)

    # Create the video container
    video_container = VideoContainer()
    main_layout.addWidget(video_container)

    # Create the battery indicator
    battery_indicator = BatteryIndicator()
    main_layout.addWidget(battery_indicator)

    # Set layout and show main widget
    main_widget.setLayout(main_layout)
    main_widget.setWindowTitle('Video Streaming with Battery Indicator')
    main_widget.showFullScreen()  # Maximize the main window

    sys.exit(app.exec_())
