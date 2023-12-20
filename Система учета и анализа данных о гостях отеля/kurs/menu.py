from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QListWidget,
    QLabel, QStackedWidget, QPushButton, QVBoxLayout, QDialog, QLineEdit, QMessageBox
)
import sqlite3
from PyQt6.QtGui import QAction
import sys
from guests import GuestsWidget
from rooms import RoomsWidget
from bookings import BookingsWidget
from analysis import AnalysisWidget


class AdminMainWindow(QMainWindow):
    # Класс основного меню
    def __init__(self, admin_info):
        super().__init__()
        self.admin_info = admin_info  # Информация об администраторе

        self.setWindowTitle("Панель Администратора")
        self.setGeometry(100, 100, 800, 600)

        # Создание виджетов для различных страниц
        self.guestsWidget = GuestsWidget()
        self.roomsWidget = RoomsWidget()
        self.bookingsWidget = BookingsWidget()
        self.analysisWidget = AnalysisWidget()  # Инициализация виджетов
        self.contentStack = QStackedWidget()
        self.setCentralWidget(self.contentStack)
        self.contentStack.addWidget(self.guestsWidget)
        self.contentStack.addWidget(self.roomsWidget)
        self.contentStack.addWidget(self.bookingsWidget)
        self.contentStack.addWidget(self.analysisWidget)    # Добавление виджетов в contentStack

        # Навигационное меню
        self.dockWidget = QDockWidget("Навигация", self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockWidget)
        self.navList = QListWidget()
        self.dockWidget.setWidget(self.navList)

        # Добавление элементов в навигационное меню
        self.navList.addItem("Гости")
        self.navList.addItem("Номера")
        self.navList.addItem("Список заселений")
        self.navList.addItem("Анализ данных")

        # События клика по навигационному меню
        self.navList.currentRowChanged.connect(self.displayPage)

        # Кнопка личного аккаунта
        self.accountAction = QAction(f"{self.admin_info['first_name']} {self.admin_info['last_name']}", self)
        self.accountAction.triggered.connect(self.showAccountInfo)
        self.toolbar = self.addToolBar("Account")
        self.toolbar.addAction(self.accountAction)

    def showAccountInfo(self):
        # Функция показа информации о пользователе
        username, password = self.loadAdminCredentials()
        if username is not None and password is not None:
            self.admin_info['username'] = username
            self.admin_info['password'] = password

        self.account_dialog = QDialog(self)  # Сохранение ссылки на диалог
        self.account_dialog.setWindowTitle("Информация об аккаунте")
        layout = QVBoxLayout()

        # Информация об администраторе
        layout.addWidget(QLabel(f"Имя: {self.admin_info['first_name']}"))
        layout.addWidget(QLabel(f"Фамилия: {self.admin_info['last_name']}"))

        # Кнопка для изменения информации
        editButton = QPushButton("Изменить информацию")
        editButton.clicked.connect(self.editAccountInfo)
        layout.addWidget(editButton)

        # Кнопка выхода
        logoutButton = QPushButton("Выход")
        logoutButton.clicked.connect(self.logout)
        layout.addWidget(logoutButton)

        self.account_dialog.setLayout(layout)
        self.account_dialog.exec()

    def editAccountInfo(self):
        # Функция для окна изменения информации об администраторе
        print("admin_info содержит:", self.admin_info)

        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Редактировать информацию об аккаунте")
            layout = QVBoxLayout()

            # Поля для редактирования
            self.editFirstName = QLineEdit(self.admin_info['first_name'])
            self.editLastName = QLineEdit(self.admin_info['last_name'])
            self.editUsername = QLineEdit(self.admin_info['username'])
            self.editPassword = QLineEdit(self.admin_info['password'])

            layout.addWidget(QLabel("Имя:"))
            layout.addWidget(self.editFirstName)
            layout.addWidget(QLabel("Фамилия:"))
            layout.addWidget(self.editLastName)
            layout.addWidget(QLabel("Логин:"))
            layout.addWidget(self.editUsername)
            layout.addWidget(QLabel("Пароль:"))
            layout.addWidget(self.editPassword)

            # Кнопка для сохранения изменений
            saveButton = QPushButton("Сохранить изменения")
            saveButton.clicked.connect(self.saveAccountInfo)
            layout.addWidget(saveButton)

            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при открытии окна редактирования: {e}")

    def loadAdminCredentials(self):
        # Функция сохранения информации
        try:
            conn = sqlite3.connect("bd_hotel.db")  # Подключение к базе данных
            cursor = conn.cursor()

            cursor.execute("SELECT username, password FROM Administrators WHERE id = ?", (self.admin_info['id'],))
            username, password = cursor.fetchone()
            conn.close()
            return username, password
        except Exception as e:
            print(f"Ошибка при загрузке учетных данных: {e}")
            return None, None
    def saveAccountInfo(self):
        new_first_name = self.editFirstName.text()
        new_last_name = self.editLastName.text()
        new_username = self.editUsername.text()
        new_password = self.editPassword.text()

        try:
            conn = sqlite3.connect("bd_hotel.db")
            cursor = conn.cursor()

            query = """UPDATE Administrators 
                       SET first_name = ?, last_name = ?, username = ?, password = ?
                       WHERE id = ?"""
            cursor.execute(query, (new_first_name, new_last_name, new_username, new_password, self.admin_info['id']))

            conn.commit()
            conn.close()

            # Обновление информации в приложении
            self.admin_info['first_name'] = new_first_name
            self.admin_info['last_name'] = new_last_name
            self.admin_info['username'] = new_username

            QMessageBox.information(self, "Успех", "Информация обновлена успешно")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")

    def logout(self):
        if hasattr(self, 'account_dialog') and self.account_dialog.isVisible():
            self.account_dialog.close()  # Закрывает диалог если тот открыт

        self.hide()  # Скрывает текущее окно вместо закрытия

        from tit import LoginWindow
        login_window = LoginWindow()
        login_window.show()

    def displayPage(self, index):
        # Логика переключения страниц
        print('переключение на индекс: ', index)
        if index == 0:
            self.contentStack.setCurrentWidget(self.guestsWidget)
        elif index == 1:  # "Номера" это второй пункт в списке
            self.contentStack.setCurrentWidget(self.roomsWidget)
        elif index == 2:  # "Список заселений" это третий пункт в списке
            self.contentStack.setCurrentWidget(self.bookingsWidget)
        elif index == 3:
            self.contentStack.setCurrentWidget(self.analysisWidget)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    from tit import LoginWindow
    login_window = LoginWindow()

    login_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
