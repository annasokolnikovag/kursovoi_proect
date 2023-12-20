from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel, QMessageBox,
                             QComboBox, QDialog, QDateEdit, QListWidgetItem, QHBoxLayout)
from PyQt6.QtCore import QDate, Qt
from PyQt6 import QtCore
import sqlite3
from datetime import datetime


class BookingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Кнопка для создания бронирования
        createBookingButton = QPushButton("Создать бронирование")
        createBookingButton.clicked.connect(self.createBooking)
        layout.addWidget(createBookingButton)

        # Заголовок для списка бронирований
        layout.addWidget(QLabel("Список бронирований"))

        # Список бронирований
        self.bookingsList = QListWidget()
        self.bookingsList.itemDoubleClicked.connect(self.onBookingSelected)
        layout.addWidget(self.bookingsList)

        # Загрузка списка бронирований
        self.loadBookingList()

    def createBooking(self):
        dialog = CreateBookingDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.loadBookingList()  # Обновление списка бронирований

    def loadBookingList(self):
        self.bookingsList.clear()
        try:
            conn = sqlite3.connect("bd_hotel.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT Bookings.id, Guests.first_name, Guests.last_name, Rooms.room_number, Bookings.check_in_date, 
                Bookings.check_out_date 
                FROM Bookings 
                JOIN Guests ON Bookings.guest_id = Guests.id 
                JOIN Rooms ON Bookings.room_id = Rooms.id
            """)
            bookings = cursor.fetchall()

            for booking in bookings:
                item_text = (f"{booking[1]} {booking[2]}, Room: {booking[3]}, Check-in: {booking[4]}, Check-out: "
                             f"{booking[5]}")
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, booking[0])  # сохраняем ID бронирования
                self.bookingsList.addItem(item)

            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список бронирований: {e}")

    def onBookingSelected(self, item):
        booking_id = item.data(Qt.ItemDataRole.UserRole)
        bookingDialog = BookingInfoDialog(booking_id, self)
        bookingDialog.exec()
        self.loadBookingList()  # Перезагрузить список бронирований после закрытия диалога

    def getBookingData(self, booking_id):
        try:
            conn = sqlite3.connect("bd_hotel.db")
            cursor = conn.cursor()

            # Измените запрос в соответствии с вашей БД
            cursor.execute("SELECT * FROM Bookings WHERE id = ?", (booking_id,))
            booking_data = cursor.fetchone()

            conn.close()
            return booking_data
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить данные бронирования: {e}")
            return None


class CreateBookingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Выпадающий список для выбора гостя
        self.guestComboBox = QComboBox()
        layout.addWidget(QLabel("Выберите гостя:"))
        layout.addWidget(self.guestComboBox)

        # Выпадающий список для выбора номера
        self.roomComboBox = QComboBox()
        layout.addWidget(QLabel("Выберите номер:"))
        layout.addWidget(self.roomComboBox)

        # Поле для даты въезда
        self.checkInDateEdit = QDateEdit()
        self.checkInDateEdit.setDate(QDate.currentDate())
        layout.addWidget(QLabel("Дата въезда:"))
        layout.addWidget(self.checkInDateEdit)

        # Поле для даты выезда
        self.checkOutDateEdit = QDateEdit()
        self.checkOutDateEdit.setDate(QDate.currentDate().addDays(1))
        layout.addWidget(QLabel("Дата выезда:"))
        layout.addWidget(self.checkOutDateEdit)

        # Кнопка для создания бронирования
        createButton = QPushButton("Создать бронирование")
        createButton.clicked.connect(self.createBooking)
        layout.addWidget(createButton)

        self.loadGuests()
        self.loadAvailableRooms()

    def loadGuests(self):
        try:
            conn = sqlite3.connect("bd_hotel.db")
            cursor = conn.cursor()

            cursor.execute("SELECT id, first_name, last_name FROM Guests")
            guests = cursor.fetchall()

            for guest_id, first_name, last_name in guests:
                self.guestComboBox.addItem(f"{first_name} {last_name}", guest_id)

            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список гостей: {e}")

    def loadAvailableRooms(self):
        try:
            conn = sqlite3.connect("bd_hotel.db")
            cursor = conn.cursor()

            # Пример запроса, который исключает занятые номера
            query = """
            SELECT id, room_number FROM Rooms 
            WHERE id NOT IN (SELECT room_id FROM Bookings WHERE check_out_date > CURRENT_DATE)
            """
            cursor.execute(query)
            rooms = cursor.fetchall()

            for room_id, room_number in rooms:
                self.roomComboBox.addItem(f"Номер {room_number}", room_id)

            conn.close()
        except Exception as e:
            print(f"Не удалось загрузить список доступных номеров: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список доступных номеров: {e}")

    def createBooking(self):
        guest_id = self.guestComboBox.currentData()
        room_id = self.roomComboBox.currentData()
        check_in_date = self.checkInDateEdit.date().toString("yyyy-MM-dd")
        check_out_date = self.checkOutDateEdit.date().toString("yyyy-MM-dd")

        if guest_id is None or room_id is None:
            QMessageBox.warning(self, "Ошибка", "Необходимо выбрать гостя и номер.")
            return

        if self.checkOutDateEdit.date() <= self.checkInDateEdit.date():
            QMessageBox.warning(self, "Ошибка", "Дата выезда должна быть позже даты въезда.")
            return

        try:
            conn = sqlite3.connect("bd_hotel.db")
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Bookings (guest_id, room_id, check_in_date, check_out_date) 
                VALUES (?, ?, ?, ?)""",
                (guest_id, room_id, check_in_date, check_out_date))

            conn.commit()
            conn.close()
            QMessageBox.information(self, "Успех", "Бронирование успешно создано.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать бронирование: {e}")


class BookingInfoDialog(QDialog):
    def __init__(self, booking_id, parent=None):
        super().__init__(parent)
        self.booking_id = booking_id
        self.booking_data = None
        self.initUI()
        self.loadBookingData()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Создаем QLabel для отображения различных аспектов бронирования
        self.nameLabel = QLabel("Имя: Загрузка...")
        layout.addWidget(self.nameLabel)

        self.phoneLabel = QLabel("Телефон: Загрузка...")
        layout.addWidget(self.phoneLabel)

        self.roomTypeLabel = QLabel("Тип номера: Загрузка...")
        layout.addWidget(self.roomTypeLabel)

        self.costLabel = QLabel("Цена (за сутки): Загрузка...")
        layout.addWidget(self.costLabel)

        self.checkInLabel = QLabel("Дата въезда: Загрузка...")
        layout.addWidget(self.checkInLabel)

        self.checkOutLabel = QLabel("Дата выезда: Загрузка...")
        layout.addWidget(self.checkOutLabel)

        deleteButton = QPushButton("Удалить")
        deleteButton.clicked.connect(self.deleteBooking)
        layout.addWidget(deleteButton)

    def loadBookingData(self):
        try:
            print("Загрузка данных бронирования")
            conn = sqlite3.connect("bd_hotel.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Guests.first_name, Guests.last_name, Guests.phone, 
                       RoomTypes.type_name, RoomTypes.cost_per_day, 
                       Bookings.check_in_date, Bookings.check_out_date
                FROM Bookings
                JOIN Guests ON Bookings.guest_id = Guests.id
                JOIN Rooms ON Bookings.room_id = Rooms.id
                JOIN RoomTypes ON Rooms.room_type_id = RoomTypes.id
                WHERE Bookings.id = ?
            """, (self.booking_id,))
            self.booking_data = cursor.fetchone()
            print(f"Полученные данные: {self.booking_data}")
            conn.close()
            self.updateUI()
        except Exception as e:
            print(f"Ошибка при загрузке данных бронирования: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные бронирования: {e}")

    def updateUI(self):
        try:
            if self.booking_data:

                # Обновление информации на интерфейсе
                self.nameLabel.setText(f"Имя: {self.booking_data[0]} {self.booking_data[1]}")
                self.phoneLabel.setText(f"Телефон: {self.booking_data[2]}")
                self.roomTypeLabel.setText(f"Тип номера: {self.booking_data[3]}")

            # Рассчитываем общую стоимость проживания
                check_in_date = datetime.strptime(self.booking_data[5], "%Y-%m-%d")
                check_out_date = datetime.strptime(self.booking_data[6], "%Y-%m-%d")
                days_stayed = (check_out_date - check_in_date).days
                total_cost = days_stayed * self.booking_data[4]

                self.costLabel.setText(f"Цена (за сутки): {self.booking_data[4]}, Всего: {total_cost}")
                self.checkInLabel.setText(f"Дата въезда: {self.booking_data[5]}")
                self.checkOutLabel.setText(f"Дата выезда: {self.booking_data[6]}")
                print("Интерфейс успешно обновлен")
            else:
                print("Нет данных для обновления интерфейса")
        except Exception as e:
            print(f"Ошибка при обновлении интерфейса: {e}")

    def deleteBooking(self):
        try:
            reply = QMessageBox.question(self, "Удаление бронирования",
                                         "Вы уверены, что хотите удалить это бронирование?")
            if reply == QMessageBox.StandardButton.Yes:
                conn = sqlite3.connect("bd_hotel.db")
                cursor = conn.cursor()

                cursor.execute("DELETE FROM Bookings WHERE id = ?", (self.booking_id,))

                conn.commit()
                conn.close()
                QMessageBox.information(self, "Успех", "Бронирование успешно удалено.")
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить бронирование: {e}")


