import sys
from PyQt5.Qt import *
import requests
import os

API_SERVER = "http://static-maps.yandex.ru/1.x/"
API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"
SCREEN_SIZE = [600, 450]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.get_map()
        self.initUI()

    def initUI(self):

        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')
        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)
        self.delta = 0.01

    def get_map(self, delta="0.01"):
        lon = "64.798335"
        lat = "54.468170"

        params = {
            "ll": ",".join([lon, lat]),
            "spn": ",".join([delta, delta]),
            "l": "map"
        }
        response = requests.get(API_SERVER, params=params)
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_PageUp:
            if self.delta > 0.01:
                self.delta -= 0.01
        elif key == Qt.Key_PageDown:
            if self.delta <= 1:
                self.delta += 0.01
        self.get_map(str(self.delta))
        self.image.setPixmap(QPixmap(self.map_file))

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
