import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QCheckBox
from PyQt5.QtGui import QPixmap
import requests
import os

API_SERVER = "http://static-maps.yandex.ru/1.x/"
API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"
SCREEN_SIZE = [800, 500]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.delta = "0.02"
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
        self.adres = QLabel(self)
        self.adres.move(600, 100)
        self.adres_index = QCheckBox('Почтовый индекс', self)
        self.adres_index.move(600, 200)
        self.adres_index.toggled.connect(self.change_state)
        self.adres_index_lbl = QLabel(self)
        self.adres_index_lbl.move(600, 230)
        self.toponim_post = None

        self.search_ui()

    def get_map(self):
        lon = "64.798335"
        lat = "54.468170"
        delta = "0.01"

        params = {
            "ll": ",".join([lon, lat]),
            "spn": ",".join([delta, delta]),
            "l": "map"
        }
        response = requests.get(API_SERVER, params=params)
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def search_ui(self):
        self.search_zone = QLineEdit(self)
        self.search_zone.move(10, 475)
        self.search_zone.resize(300, 20)

        self.search_btn = QPushButton("Искать", self)
        self.search_btn.move(400, 475)
        self.search_btn.resize(50, 20)
        self.search_btn.clicked.connect(self.search)

    def search(self):
        que = self.search_zone.text()
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={que}&format=json"
        response = requests.get(geocoder_request)
        if response:
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            try:
                toponim_adres = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]
                self.toponim_post = toponim_adres["postal_code"]
            except KeyError:
                print('Выберите адрес с почтовым индексом, если хотите его увидеть!')
            toponym_coodrinates = toponym["Point"]["pos"]

            lon, lat = toponym_coodrinates.split()
            params = {
                "pt": ",".join([lon, lat]),
                "l": "map"
            }

            self.adres.setText(toponym_address)
            self.adres.resize(self.adres.sizeHint())
            if self.adres_index.isChecked():
                self.adres_index_lbl.setText(toponim_post)
                self.adres_index_lbl.resize(self.adres_index_lbl.sizeHint())
            response = requests.get(API_SERVER, params=params)
            self.map_file = "map.png"
            with open(self.map_file, "wb") as file:
                file.write(response.content)
            self.pixmap = QPixmap(self.map_file)
            self.image.setPixmap(self.pixmap)

        else:
            print("Ошибка выполнения запроса:")
            print(geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")

    def change_state(self):
        if not self.adres_index.isChecked():
            self.adres_index_lbl.setText('')
        else:
            if self.toponim_post:
                self.adres_index_lbl.setText(self.toponim_post)
                self.adres_index_lbl.resize(self.adres_index_lbl.sizeHint())

    def closeEvent(self, event):
        os.remove(self.map_file)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Example()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())