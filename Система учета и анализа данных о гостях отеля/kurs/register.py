from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QWidget, QLabel, QMessageBox
import sys
import bd_hotel  # Убедитесь, что файл bd.py находится в том же каталоге


class RegisterWindow(QMainWindow):
    # Класс для окна регистрации
    def __init__(self):
        super().__init__()

        # Настройка основного окна
        self.setWindowTitle("Регистрация администратора")
        self.setGeometry(100, 100, 300, 200)

        # Создание центрального виджета и установка макета
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Создание и добавление виджетов для ввода данных
        self.first_name_label = QLabel("Имя:")
        self.first_name_input = QLineEdit()
        self.last_name_label = QLabel("Фамилия:")
        self.last_name_input = QLineEdit()
        self.username_label = QLabel("Имя пользователя:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.register_button = QPushButton("Зарегистрировать")
        self.register_button.clicked.connect(self.register_admin)

        # Добавление виджетов в макет
        self.layout.addWidget(self.first_name_label)
        self.layout.addWidget(self.first_name_input)
        self.layout.addWidget(self.last_name_label)
        self.layout.addWidget(self.last_name_input)
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.register_button)

    def check_username_exists(self, conn, username):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM administrators WHERE username = ?", (username,))
        return cursor.fetchone() is not None

    def register_admin(self):
        # Функуия реализации регистрации
        try:
            first_name = self.first_name_input.text()
            last_name = self.last_name_input.text()
            username = self.username_input.text()
            password = self.password_input.text()

            # Проверка на пустые поля
            if not first_name or not last_name or not username or not password:
                QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены.")
                return

            conn = bd_hotel.create_connection("bd_hotel.db")

            # Проверка на существования логина
            if self.check_username_exists(conn, username):
                QMessageBox.warning(self, "Ошибка", "Этот логин уже занят. Выберите другой.")
                return
            bd_hotel.add_administrator(conn, (first_name, last_name, username, password))
            conn.commit()
            conn.close()

            print("Администратор зарегистрирован")
            QMessageBox.information(self, "Успех", "Администратор зарегистрирован")
        except Exception as e:
            print(f"Произошла ошибка при регистрации: {e}")
        finally:
            conn.close()


def main():
    app = QApplication(sys.argv)
    mainWin = RegisterWindow()
    mainWin.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
