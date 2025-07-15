import cv2
import sys
import psutil
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout, QHBoxLayout, QSlider, QSizePolicy
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtGui import QImage, QPixmap


class Thread(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.isRunning = True

    def run(self):
        cap = cv2.VideoCapture(0)
        while self.isRunning:
            ret, frame = cap.read()
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(
                    rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                # Scale to full HD resolution
                p = convertToQtFormat.scaled(1920, 1080, Qt.IgnoreAspectRatio)
                self.changePixmap.emit(p)

    def stop(self):
        self.isRunning = False
        self.quit()
        self.wait()


class VideoContainer(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Video'
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        self.setWindowTitle(self.title)
        # Set initial size to full HD resolution
        self.setGeometry(0, 0, 1920, 1080)

        # Create a label for displaying video frames
        self.label = QLabel(self)
        # Set label size to match window size
        self.label.setGeometry(0, 0, 1920, 1080)

        # Start the thread to capture and display video frames
        self.thread = Thread(self)
        self.thread.changePixmap.connect(self.setImage)
        self.thread.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = VideoContainer()
    main_window.showFullScreen()  # Show the main window in fullscreen mode
    sys.exit(app.exec_())
