from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QCheckBox,
                             QDialog, QDoubleSpinBox, QLineEdit, QMessageBox, QComboBox)
import sqlite3


class RoomsWidget(QWidget):
    # Класс для виджета Номера
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        print('Инициализация для RoomsWidget')
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        # Горизонтальный макет
        buttonsLayout = QHBoxLayout()

        # Кнопки для добавления номера и создания типа номера
        addRoomButton = QPushButton("Добавить номер")
        addRoomButton.clicked.connect(self.addRoom)
        buttonsLayout.addWidget(addRoomButton)

        createRoomTypeButton = QPushButton("Создать тип номера")
        createRoomTypeButton.clicked.connect(self.createRoomType)
        buttonsLayout.addWidget(createRoomTypeButton)

        layout.addLayout(buttonsLayout)

        # Заголовок и список номеров
        layout.addWidget(QLabel("Все номера"))
        self.roomsList = QListWidget()
        layout.addWidget(self.roomsList)

        # Чекбокс для незанятых номеров
        self.showAvailableCheckbox = QCheckBox("Показать незанятые")
        self.showAvailableCheckbox.stateChanged.connect(self.updateRoomList)
        layout.addWidget(self.showAvailableCheckbox)

        # Загрузка списка номеров
        self.loadRoomList()

    def showEvent(self, event):
        super().showEvent(event)
        self.loadRoomList()  # Обновление списка номеров

    def addRoom(self):
        # Функция открытия окна добавления номера
        dialog = AddRoomDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.loadRoomList()

    def createRoomType(self):
        # Функция открытия окна создания типа комнаты
        dialog = CreateRoomTypeDialog(self)

    def updateRoomList(self):
        self.roomsList.clear()  # Очищаем текущий список

        try:
            conn = sqlite3.connect("bd_hotel.db")
            cursor = conn.cursor()

            if self.showAvailableCheckbox.isChecked():
                # Запрос для получения только незанятых номеров
                query = """
                SELECT room_number FROM Rooms 
                WHERE id NOT IN (SELECT room_id FROM Bookings WHERE check_out_date > CURRENT_DATE)
                """
            else:
                # Запрос для получения всех номеров
                query = "SELECT room_number FROM Rooms"

            cursor.execute(query)
            rooms = cursor.fetchall()

            for room in rooms:
                self.roomsList.addItem(f"Номер: {room[0]}")

            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список номеров: {e}")

    def openAddRoomDialog(self):
        # Открываем диалоговое окно для добавления номера
        addRoomDialog = AddRoomDialog(self)
        result = addRoomDialog.exec()

    def loadRoomList(self):
        self.roomsList.clear()  # Очистка текущего списка
        try:
            conn = sqlite3.connect("bd_hotel.db")
            cursor = conn.cursor()

            cursor.execute("SELECT room_number, room_type_id FROM Rooms")
            rooms = cursor.fetchall()

            for room in rooms:
                room_number, room_type_id = room
                self.roomsList.addItem(f"Номер: {room_number}, Тип: {room_type_id}")

            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список номеров: {e}")

    def onRoomSelected(self):
        selected_item = self.roomsList.currentItem()
        if selected_item is None:
            return

        room_number = selected_item.text().split(": ")[1]  # Получаем номер комнаты из текста элемента списка
        try:
            conn = sqlite3.connect("bd_hotel.db")
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM Rooms WHERE room_number = ?", (room_number,))
            room_data = cursor.fetchone()

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить информацию о номере: {e}")

    def createRoomType(self):
        # Функция открытия окна создания типа комнаты
        dialog = CreateRoomTypeDialog(self)
        dialog.exec()

    # Если этот файл запускается как главный, отобразить виджет для тестирования
#if __name__ == "__main__":
    # from PyQt6.QtWidgets import QApplication
    #import sys

    #app = QApplication(sys.argv)
    #mainWin = RoomsWidget()
    #mainWin.show()
    #sys.exit(app.exec())


class CreateRoomTypeDialog(QDialog):
    # Класс для создания типа номера
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        self.typeNameEdit = QLineEdit()
        layout.addWidget(QLabel("Название типа:"))
        layout.addWidget(self.typeNameEdit)

        self.costPerDayEdit = QDoubleSpinBox()
        self.costPerDayEdit.setRange(0, 100000)  # Диапазон цен
        layout.addWidget(QLabel("Цена за день:"))
        layout.addWidget(self.costPerDayEdit)

        saveButton = QPushButton("Сохранить")
        saveButton.clicked.connect(self.saveRoomType)
        layout.addWidget(saveButton)

    def saveRoomType(self):
        typeName = self.typeNameEdit.text()
        costPerDay = self.costPerDayEdit.value()

        # Проверка на пустое поле
        if not typeName:
            QMessageBox.warning(self, "Ошибка", "Название типа не может быть пустым")
            return

        try:
            conn = sqlite3.connect("bd_hotel.db")
            cursor = conn.cursor()

            # Проверка существования типа номера
            cursor.execute("SELECT * FROM RoomTypes WHERE type_name = ?", (typeName,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", "Тип номера с таким названием уже существует")
                return

            cursor.execute("INSERT INTO RoomTypes (type_name, cost_per_day) VALUES (?, ?)",
                           (typeName, costPerDay))
            conn.commit()
            conn.close()
            print("Тип номера успешно сохранен")
            self.accept()  # Закрытие окна после сохранения
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить тип номера: {e}")


class AddRoomDialog(QDialog):
    # Класс для создания номера
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Выпадающий список для выбора типа номера
        self.roomTypeComboBox = QComboBox()
        self.roomTypeComboBox.currentIndexChanged.connect(self.onRoomTypeChanged)
        layout.addWidget(QLabel("Тип номера:"))
        layout.addWidget(self.roomTypeComboBox)

        # Цена за день
        self.costLabel = QLabel("Цена за день: -")
        layout.addWidget(self.costLabel)

        # Поле для номера комнаты
        self.roomNumberEdit = QLineEdit()
        layout.addWidget(QLabel("Номер комнаты:"))
        layout.addWidget(self.roomNumberEdit)

        # Кнопка для добавления номера
        addButton = QPushButton("Сохранить")
        addButton.clicked.connect(self.addRoom)
        layout.addWidget(addButton)

        self.loadRoomTypes()

    def loadRoomTypes(self):
        try:
            conn = sqlite3.connect("bd_hotel.db")
            cursor = conn.cursor()

            cursor.execute("SELECT id, type_name, cost_per_day FROM RoomTypes")
            roomTypes = cursor.fetchall()

            for typeId, typeName, cost in roomTypes:
                # Сохраняем идентификатор и стоимость вместе как кортеж
                self.roomTypeComboBox.addItem(typeName, (typeId, cost))

            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить типы номеров: {e}")
            print(f"Не удалось загрузить типы номеров: {e}")

    def onRoomTypeChanged(self, index):
        if index == -1:  # Нет выбранного элемента
            return
        # Получаем кортеж (typeId, cost)
        typeId, cost = self.roomTypeComboBox.itemData(index)
        self.costLabel.setText(f"Цена за день: {cost}")

    def addRoom(self):
        roomNumber = self.roomNumberEdit.text()
        typeData = self.roomTypeComboBox.currentData()  # Это кортеж (typeId, cost)
        typeId = typeData[0] if typeData else None  # Извлекаем только typeId

        if not roomNumber:
            QMessageBox.warning(self, "Предупреждение", "Введите номер комнаты.")
            return

        try:
            conn = sqlite3.connect("bd_hotel.db")
            cursor = conn.cursor()

            # Проверка существования комнаты с таким номером
            cursor.execute("SELECT * FROM Rooms WHERE room_number = ?", (roomNumber,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", "Комната с таким номером уже существует.")
                return

            cursor.execute("INSERT INTO Rooms (room_number, room_type_id) VALUES (?, ?)",
                           (roomNumber, typeId))

            conn.commit()
            conn.close()
            QMessageBox.information(self, "Успех", "Номер успешно добавлен.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить номер: {e}")
