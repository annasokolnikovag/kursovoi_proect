from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QWidget, QLabel, QMessageBox
import sys
import sqlite3
from register import RegisterWindow
from menu import AdminMainWindow


class LoginWindow(QMainWindow):
    # Класс для окна входа
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Вход в систему")
        self.setGeometry(100, 100, 280, 100)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.username_label = QLabel("Имя пользователя:")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Вход")
        self.login_button.clicked.connect(self.check_login)

        self.register_button = QPushButton("Регистрация")
        self.register_button.clicked.connect(self.open_register_window)

        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.register_button)

        self.central_widget.setLayout(self.layout)

    def check_login(self):
        # Функция проверки логина и пароля
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        # Проверка на пустые поля
        if not username or not password:
            QMessageBox.warning(self, "Ошибка входа", "Необходимо ввести имя пользователя и пароль")
            return

        conn = sqlite3.connect("bd_hotel.db")
        cursor = conn.cursor()

        query = "SELECT * FROM Administrators WHERE username = ? AND password = ?"
        cursor.execute(query, (username, password))
        admin_row = cursor.fetchone()

        if admin_row:
            admin_info = {
                "id": admin_row[0],
                "first_name": admin_row[1],
                "last_name": admin_row[2]
            }

            self.main_window = AdminMainWindow(admin_info)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка входа", "Неправильное имя пользователя или пароль")

        conn.close()


    def open_register_window(self):
        # Функция для открытия окна регистрации
        try:
            self.register_window = RegisterWindow()
            self.register_window.show()
        except Exception as e:
            print(f"Произошла ошибка при открытии окна регистрации: {e}")


def main():
    app = QApplication(sys.argv)
    mainWin = LoginWindow()
    mainWin.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
