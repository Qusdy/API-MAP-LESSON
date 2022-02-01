import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PyQt5.QtGui import QPixmap
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
        self.btn_up = QPushButton('PgUp', self)
        self.btn_up.resize(50, 50)
        self.btn_up.move(530, 30)
        self.btn_down = QPushButton('PgDown', self)
        self.btn_down.resize(50, 50)
        self.btn_down.move(530, 110)
        self.btn_up.clicked.connect(self.scale)
        self.btn_down.clicked.connect(self.scale)

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

    def scale(self):
        if self.sender().text() == "PgUp":
            if self.delta > 0.001:
                self.delta -= 0.01
        else:
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