import sqlite3
from datetime import datetime


def create_connection(db_file):
    """Создать подключение к базе данных."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("SQLite база данных успешно подключена")
    except sqlite3.Error as e:
        print(e)
    return conn


def create_table(conn, create_table_sql):
    """Создать таблицу с использованием предоставленного SQL запроса."""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        print("Таблица успешно создана")
    except sqlite3.Error as e:
        print(e)


def add_administrator(conn, admin):
    """ Добавление нового администратора в базу данных. """
    sql = ''' INSERT INTO Administrators(first_name, last_name, username, password)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, admin)
    return cur.lastrowid


def add_guest(conn, guest):
    """ Добавление нового гостя в базу данных. """
    sql = ''' INSERT INTO Guests(first_name, last_name, check_in_date, check_out_date)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, guest)
    return cur.lastrowid


def __main__():
    database = "bd_hotel.db"

    sql_create_guests_table = """ CREATE TABLE IF NOT EXISTS Guests (
                                        id INTEGER PRIMARY KEY,
                                        first_name TEXT NOT NULL,
                                        last_name TEXT NOT NULL,
                                        date_of_birth TEXT NOT NULL,
                                        phone TEXT NOT NULL
                                    ); """

    sql_create_administrators_table = """CREATE TABLE IF NOT EXISTS Administrators (
                                            id INTEGER PRIMARY KEY,
                                            first_name TEXT NOT NULL,
                                            last_name TEXT NOT NULL,
                                            username TEXT NOT NULL UNIQUE,
                                            password TEXT NOT NULL
                                        );"""

    sql_create_room_types_table = """CREATE TABLE IF NOT EXISTS RoomTypes (
                                            id INTEGER PRIMARY KEY,
                                            type_name TEXT NOT NULL UNIQUE,
                                            cost_per_day REAL NOT NULL
                                        );"""

    sql_create_rooms_table = """CREATE TABLE IF NOT EXISTS Rooms (
                                        id INTEGER PRIMARY KEY,
                                        room_number TEXT NOT NULL,
                                        room_type_id INTEGER NOT NULL,
                                        FOREIGN KEY (room_type_id) REFERENCES RoomTypes (id)
                                    );"""

    sql_create_bookings_table = """ CREATE TABLE IF NOT EXISTS Bookings (
                                        id INTEGER PRIMARY KEY,
                                        guest_id INTEGER NOT NULL,
                                        room_id INTEGER NOT NULL,
                                        check_in_date TEXT NOT NULL,
                                        check_out_date TEXT NOT NULL,
                                        FOREIGN KEY (guest_id) REFERENCES Guests (id) ON DELETE CASCADE,
                                        FOREIGN KEY (room_id) REFERENCES Rooms (id) ON DELETE CASCADE
                                    );"""

    # Создаем подключение к базе данных
    conn = create_connection(database)

    # Создаем таблицы
    if conn is not None:
        create_table(conn, sql_create_guests_table)
        create_table(conn, sql_create_administrators_table)
        create_table(conn, sql_create_room_types_table)
        create_table(conn, sql_create_rooms_table)
        create_table(conn, sql_create_bookings_table)
        conn.close()
    else:
        print("Ошибка! Не удалось создать подключение к базе данных.")


if __name__ == '__main__':
    __main__()
