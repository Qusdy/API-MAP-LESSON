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
        self.stuf = 1
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
        self.can_edit = False
        self.image.installEventFilter(self)
        self.search_ui()

    def search_ui(self):
        self.search_zone = QLineEdit(self)
        self.search_zone.move(10, 475)
        self.search_zone.resize(300, 20)
        self.search_btn = QPushButton("Искать", self)
        self.search_btn.move(400, 475)
        self.search_btn.resize(50, 20)
        self.search_btn.clicked.connect(self.search)
        self.edit_map_btn = QPushButton("Редактировать", self)
        self.edit_map_btn.setStyleSheet("color: white; background-color: red")
        self.edit_map_btn.clicked.connect(self.edit)
        self.clear_map_btn = QPushButton("Очистить", self)
        self.clear_map_btn.setStyleSheet("color: white; background-color: red")
        self.clear_map_btn.move(100, 0)
        self.ask_info = QLabel(self)
        self.ask_info.resize(200, 60)
        self.ask_info.move(300, 0)
        self.clear_map_btn.clicked.connect(self.clear)
        btn_map = QRadioButton("карта", self)
        btn_map.setChecked(True)
        btn_map.move(50, 10)
        btn_sat = QRadioButton("спутник", self)
        btn_sat.move(120, 10)
        btn_gibrid = QRadioButton("гибрид", self)
        btn_gibrid.move(190, 10)
        self.btns = [btn_map, btn_sat, btn_gibrid]
        self.save = self.search_zone.keyPressEvent
        for el in self.btns:
            el.resize(70, 70)
            el.toggled.connect(self.change_setings)

    def clear(self):
        self.delta = 1
        self.lon = "64.798335"
        self.lat = "54.468170"
        self.params = {
            "ll": ",".join([self.lon, self.lat]),
            "z": self.delta,
            "l": "map"
        }
        self.get_map()
        self.image.setPixmap(QPixmap(self.map_file))

    def edit(self):
        if self.can_edit:
            self.can_edit = False
            for el in self.btns:
                el.setEnabled(True)
            self.search_zone.keyPressEvent = self.save
            self.edit_map_btn.setStyleSheet("color: white; background-color: red")
        else:
            self.can_edit = True
            self.edit_map_btn.setStyleSheet("color: white; background-color: green")
            self.search_zone.keyPressEvent = self.keyPressEvent
            for el in self.btns:
                el.setEnabled(False)

    def eventFilter(self, obj, e):
        if obj == self.image and e.type() == 2:
            temp = list(map(int, str(e.pos()).split('(')[1][:-1].split(',')))
            print(temp)
            self.searchByOrganization(temp)
        return super(QWidget, self).eventFilter(obj, e)

    def searchByOrganization(self, cords):
        x_size, y_size = (float(self.delta) / self.image.width(),
                          float(self.delta) / self.image.height())
        new_ask = ','.join((str((float(self.lat) - float(self.delta)) -
                                x_size * (cords[0] - 10)),
                            str((float(self.lon) - float(self.delta)) -
                                y_size * (cords[1] - 10))))
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

        search_params = {
            "apikey": api_key,
            "text": new_ask,
            "lang": "ru_RU",
            "ll": new_ask,
            "type": "biz",
        }

        response = requests.get(search_api_server, params=search_params)
        if not response:
            print('нет запроса:' + response.url)
            return
        json_response = response.json()
        print(json_response)
        organization = json_response["features"]
        org_name = organization["properties"]["CompanyMetaData"]["name"]
        org_address = organization["properties"]["CompanyMetaData"]["address"]
        self.ask_info.setPlainText(
        f'Название организации: {org_name}\nАдресс организации: {org_address}\nКоординаты организации: {org_point}')
        self.ask_info.setText('Нет организации')

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
        if self.can_edit:
            if key == Qt.Key_Right:
                if float(self.lon) + (self.stuf / self.delta) <= 180:
                    self.lon = f"{float(self.lon) + (self.stuf / self.delta):.{6}f}"
                else:
                    self.lon = f"{-180 + (float(self.lon) + (self.stuf / self.delta) - 180):.{6}f}"
            elif key == Qt.Key_Left:
                if float(self.lon) + (self.stuf / self.delta) >= -180:
                    self.lon = f"{float(self.lon) - (self.stuf / self.delta):.{6}f}"
                else:
                    self.lon = f"{180 - (float(self.lon) - (self.stuf / self.delta) + 180):.{6}f}"
            elif key == Qt.Key_Up:
                if float(self.lat) + (self.stuf / self.delta) <= 90:
                    self.lat = f"{float(self.lat) + (self.stuf / self.delta):.{6}f}"
                else:
                    self.lat = f"{-90 + (float(self.lat) + (self.stuf / self.delta) - 90):.{6}f}"
            elif key == Qt.Key_Down:
                if float(self.lat) + self.delta >= -90:
                    self.lat = f"{float(self.lat) - (self.stuf / self.delta):.{6}f}"
                else:
                    self.lat = f"{90 - (float(self.lat) - (self.stuf / self.delta) + 90):.{6}f}"
            elif key == Qt.Key_PageUp:
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
    form = Example()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
