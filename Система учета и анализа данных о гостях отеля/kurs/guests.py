# Файл guests.py

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLineEdit, QListWidget, QMessageBox, QDialog, QLabel,
                             QHBoxLayout, QDateEdit)
from PyQt6.QtCore import QDate
import sqlite3


class GuestsWidget(QWidget):
    # Класс для виджета Гости
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        # Кнопка "Добавить гостя"
        self.addButton = QPushButton("Добавить гостя")
        self.addButton.clicked.connect(self.addNewGuest)  # Подключение слота к сигналу
        self.layout.addWidget(self.addButton)

        # Поле для поиска
        self.searchEdit = QLineEdit()
        self.searchEdit.setPlaceholderText("Поиск")  # Начальный текст
        self.searchEdit.textChanged.connect(self.updateGuestList)  # Обновление при вводе текста
        self.layout.addWidget(self.searchEdit)

        # Список гостей
        self.guestsList = QListWidget()
        self.layout.addWidget(self.guestsList)

        # Загрузка данных гостей
        self.loadGuestsData()

        # Соединение сигнала itemClicked со слотом для отображения информации о госте
        self.guestsList.itemClicked.connect(self.showGuestInfo)

    def updateGuestList(self, text):
        # Функция для фильтрации списка гостей
        self.loadGuestsData(text)


    def addNewGuest(self):
        # Функция открытия окна добавления гостя
        add_guest_dialog = AddGuestDialog(parent=self)
        if add_guest_dialog.exec() == QDialog.DialogCode.Accepted:
            self.loadGuestsData()  # Обновление списка гостей после добавления

    def loadGuestsData(self, filter_text=''):
        self.guestsList.clear()  # Очистка списка перед загрузкой новых данных

        try:
            conn = sqlite3.connect("bd_hotel.db")
            cursor = conn.cursor()

            if filter_text:
                query = "SELECT first_name, last_name FROM Guests WHERE first_name LIKE ? OR last_name LIKE ?"
                filter_text = f'%{filter_text}%'
                cursor.execute(query, (filter_text, filter_text))
            else:
                query = "SELECT first_name, last_name FROM Guests"
                cursor.execute(query)

            for first_name, last_name in cursor.fetchall():
                self.guestsList.addItem(f"{first_name} {last_name}")

            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные гостей: {e}")



    def showAddGuestDialog(self, item):
        # Функция для открытия окна изменения информации о госте
        print('item clicked: ', item.text())
        dialog = AddGuestDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.loadGuestsData()  # Перезагрузка гостей

    def showGuestInfo(self, item):
        # Функция для показа окна информации о госте
        print('Показ информации о госте: ', item.text())
        try:
            guest_name = item.text()
            guest_data = self.getGuestData(guest_name.split(' ')[0], guest_name.split(' ')[1])

            if guest_data:
                details_dialog = GuestInfoDialog(guest_data, self)
                if details_dialog.exec() == QDialog.DialogCode.Accepted:
                    self.loadGuestsData()  # Обновить список гостей после закрытия диалога
        except Exception as e:
            print(f'Ошибка при показе информации о госте: {e}')
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при показе информации о госте: {e}')

    def getGuestData(self, first_name, last_name):
        try:
            conn = sqlite3.connect("bd_hotel.db")
            cursor = conn.cursor()

            query = "SELECT * FROM Guests WHERE first_name = ? AND last_name = ?"
            cursor.execute(query, (first_name, last_name))
            guest_data = cursor.fetchone()

            conn.close()

            if guest_data:
                # Создаем словарь с данными о госте
                return {
                    'id': guest_data[0],
                    'first_name': guest_data[1],
                    'last_name': guest_data[2],
                    'date_of_birth': guest_data[3],
                    'phone': guest_data[4],
                }
            else:
                QMessageBox.warning(self, "Ошибка", "Гость не найден")
                return None
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить данные о госте: {e}")
            return None


class AddGuestDialog(QDialog):
    # Класс окна для добавления и изменения информации о госте
    def __init__(self, guest_data=None, parent=None):
        super().__init__(parent)
        self.guest_data = guest_data
        self.isEditMode = guest_data is not None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Поля для ввода данных гостя
        self.firstNameEdit = QLineEdit()
        self.lastNameEdit = QLineEdit()
        self.dateOfBirthEdit = QDateEdit()
        self.dateOfBirthEdit.setMaximumDate(QDate.currentDate().addYears(-18))  # Минимальный возраст 18 лет
        self.phoneEdit = QLineEdit()

        layout.addWidget(QLabel("Имя:"))
        layout.addWidget(self.firstNameEdit)
        layout.addWidget(QLabel("Фамилия:"))
        layout.addWidget(self.lastNameEdit)
        layout.addWidget(QLabel("Дата рождения:"))
        layout.addWidget(self.dateOfBirthEdit)
        layout.addWidget(QLabel("Телефон:"))
        layout.addWidget(self.phoneEdit)

        # Если выбрано изменение информации
        if self.guest_data:
            self.firstNameEdit.setText(self.guest_data['first_name'])
            self.lastNameEdit.setText(self.guest_data['last_name'])
            date_of_birth = QDate.fromString(self.guest_data['date_of_birth'], "yyyy-MM-dd")
            self.dateOfBirthEdit.setDate(date_of_birth)
            self.phoneEdit.setText(self.guest_data['phone'])

        # Кнопки Сохранить и Отмена
        buttonsLayout = QHBoxLayout()
        self.saveButton = QPushButton("Сохранить")
        self.saveButton.clicked.connect(self.saveGuest)
        self.saveButton.setEnabled(False)  # Изначально кнопка неактивна

        cancelButton = QPushButton("Отмена")
        cancelButton.clicked.connect(self.reject)  # Закрывает диалог

        buttonsLayout.addWidget(self.saveButton)
        buttonsLayout.addWidget(cancelButton)
        layout.addLayout(buttonsLayout)

        # Обработчики изменений для активации кнопки Сохранить
        self.firstNameEdit.textChanged.connect(self.validateInput)
        self.lastNameEdit.textChanged.connect(self.validateInput)
        self.dateOfBirthEdit.dateChanged.connect(self.validateInput)
        self.phoneEdit.textChanged.connect(self.validateInput)

    def validateInput(self):
        # Проверка заполненности полей
        is_valid = all([
            self.firstNameEdit.text(),
            self.lastNameEdit.text(),
            self.phoneEdit.text(),
            self.dateOfBirthEdit.date() <= QDate.currentDate().addYears(-18)    # Проверка на возраст
        ])
        self.saveButton.setEnabled(is_valid)

    def saveGuest(self):
        # Функция Сохранения гостей
        first_name = self.firstNameEdit.text()
        last_name = self.lastNameEdit.text()
        date_of_birth = self.dateOfBirthEdit.date().toString("yyyy-MM-dd")
        phone = self.phoneEdit.text()

        try:
            conn = sqlite3.connect("bd_hotel.db")
            cursor = conn.cursor()

            if self.guest_data:
                # Обновление существующего гостя
                cursor.execute("""
                    UPDATE Guests SET first_name = ?, last_name = ?, date_of_birth = ?, phone = ? 
                    WHERE id = ?""", (first_name, last_name, date_of_birth, phone, self.guest_data['id']))
            else:
                # Добавление нового гостя
                cursor.execute("""
                    INSERT INTO Guests (first_name, last_name, date_of_birth, phone) 
                    VALUES (?, ?, ?, ?)""", (first_name, last_name, date_of_birth, phone))

            conn.commit()
            conn.close()
            QMessageBox.information(self, "Успех", "Информация о госте успешно сохранена.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить информацию о госте: {e}")


class GuestInfoDialog(QDialog):
    # Класс окна информации о госте
    def __init__(self, guest_data, parent=None):
        super().__init__(parent)
        try:
            self.guest_data = guest_data  # Данные о госте
            self.initUI()
        except Exception as e:
            print(f'Ошибка в GuestInfoDialog: {e}')
            QMessageBox.critical(self, 'Ошибка', f'Ошибка в GuestInfoDialog: {e}')

    def initUI(self):
        layout = QVBoxLayout(self)

        # Отображение информации о госте
        layout.addWidget(QLabel(f"Имя: {self.guest_data['first_name']}"))
        layout.addWidget(QLabel(f"Фамилия: {self.guest_data['last_name']}"))
        layout.addWidget(QLabel(f"Дата рождения: {self.guest_data['date_of_birth']}"))
        layout.addWidget(QLabel(f"Телефон: {self.guest_data['phone']}"))

        # Кнопка для редактирования
        editButton = QPushButton("Редактировать")
        editButton.clicked.connect(self.editGuest)
        layout.addWidget(editButton)
        # Кнопка Удалить
        deleteButton = QPushButton("Удалить")
        deleteButton.clicked.connect(self.deleteGuest)
        layout.addWidget(deleteButton)

    def editGuest(self):
        edit_guest_dialog = AddGuestDialog(self.guest_data, parent=self)
        if edit_guest_dialog.exec() == QDialog.DialogCode.Accepted:
            # Обновление данных
            pass

    def deleteGuest(self):
        # Функция удаления гостя
        reply = QMessageBox.question(self, 'Подтверждение', 'Вы уверены, что хотите удалить этого гостя?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect("bd_hotel.db")
                cursor = conn.cursor()

                # Удаляем все бронирования, связанные с этим гостем
                delete_bookings_query = "DELETE FROM Bookings WHERE guest_id = ?"
                cursor.execute(delete_bookings_query, (self.guest_data['id'],))

                query = "DELETE FROM Guests WHERE id = ?"
                cursor.execute(query, (self.guest_data['id'],))

                conn.commit()
                conn.close()

                QMessageBox.information(self, 'Успех', 'Гость и связанные бронирования успешно удалены')
                self.accept()  # Закрытие окна
            except Exception as e:
                print(f'Не удалось удалить гостя: {e}')
                QMessageBox.critical(self, 'Ошибка', f'Не удалось удалить гостя: {e}')
