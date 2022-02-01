import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QRadioButton
from PyQt5.QtGui import QPixmap
import requests
import os

API_SERVER = "http://static-maps.yandex.ru/1.x/"
API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"
SCREEN_SIZE = [600, 450]
SETTINGS = ("map", "sat", "sat,skl")


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
        btn_map = QRadioButton("карта", self)
        btn_map.setChecked(True)
        btn_map.move(50, 10)
        btn_sat = QRadioButton("спутник", self)
        btn_sat.move(120, 10)
        btn_gibrid = QRadioButton("гибрид", self)
        btn_gibrid.move(190, 10)

        self.btns = [btn_map, btn_sat, btn_gibrid]
        for el in self.btns:
            el.resize(70, 70)
            el.toggled.connect(self.change_setings)

    def get_map(self, setting="map"):
        lon = "64.798335"
        lat = "54.468170"
        delta = "0.01"

        params = {
            "ll": ",".join([lon, lat]),
            "spn": ",".join([delta, delta]),
            "l": setting
        }
        response = requests.get(API_SERVER, params=params)
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def change_setings(self):
        for i in range(3):
            if self.btns[i] == self.sender():
                self.get_map(SETTINGS[i])
                break
        self.image.setPixmap(QPixmap(self.map_file))

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())