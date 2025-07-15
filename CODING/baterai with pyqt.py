import sys
import psutil
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap


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
        layout.addWidget(self.battery_icon_label)

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
        if battery_level > 75:
            icon_path = 'batery.png'
        elif battery_level > 25:
            icon_path = 'battery_half.png'
        else:
            icon_path = 'battery_low.png'

        pixmap = QPixmap(icon_path)
        self.battery_icon_label.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BatteryIndicator()
    window.show()
    sys.exit(app.exec())
