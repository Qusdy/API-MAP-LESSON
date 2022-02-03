import sys
from PyQt5.Qt import *
import requests
import os

API_SERVER = "http://static-maps.yandex.ru/1.x/"
API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"
SCREEN_SIZE = [600, 500]
SETTINGS = ("map", "sat", "sat,skl")


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.stuf = 2
        self.delta = 1
        self.lon = "64.798335"
        self.lat = "54.468170"
        self.params = {
            "ll": ",".join([self.lon, self.lat]),
            "z": self.delta,
            "l": "map"
        }
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
        self.search_ui()

    def search_ui(self):
        self.search_zone = QLineEdit(self)
        self.search_zone.move(10, 475)
        self.search_zone.resize(300, 20)
        self.search_btn = QPushButton("Искать", self)
        self.search_btn.move(400, 475)
        self.search_btn.resize(50, 20)
        self.search_btn.clicked.connect(self.search)
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

    def change_setings(self):
        for i in range(3):
            if self.btns[i] == self.sender():
                self.params["l"] = SETTINGS[i]
                self.get_map()
                break
        self.image.setPixmap(QPixmap(self.map_file))

    def get_map(self):
        response = requests.get(API_SERVER, params=self.params)
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_PageUp:
            if self.delta - 1 > 0:
                self.delta -= 1
        elif key == Qt.Key_PageDown:
            if self.delta + 1 <= 17:
                self.delta += 1
        self.params['ll'] = ",".join([self.lon, self.lat])
        self.params["z"] = self.delta
        self.get_map()
        self.image.setPixmap(QPixmap(self.map_file))

    def search(self):
        self.search_zone.clearFocus()
        que = self.search_zone.text()
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={que}&format=json"
        response = requests.get(geocoder_request)
        if response:
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"]

            lon, lat = toponym_coodrinates.split()
            self.params["pt"] = ",".join([lon, lat])
            self.params["ll"] = ",".join([lon, lat])
            self.lon = lon
            self.lat = lat
            response = requests.get(API_SERVER, params=self.params)
            self.map_file = "map.png"
            with open(self.map_file, "wb") as file:
                file.write(response.content)
            self.pixmap = QPixmap(self.map_file)
            self.image.setPixmap(self.pixmap)
        else:
            print("Ошибка выполнения запроса:")
            print(geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")

    def closeEvent(self, event):
        os.remove(self.map_file)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
