import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QComboBox
import sqlite3
import matplotlib.dates as mdates
import datetime


class AnalysisWidget(QWidget):
    # Класс для виджета Анализа данных
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Выпадающий список для выбора типа диаграммы
        self.chartTypeComboBox = QComboBox()
        self.chartTypeComboBox.addItem("Спрос для дней недели", "bar")
        self.chartTypeComboBox.addItem("Схема занятости номеров по датам", "gantt")
        self.chartTypeComboBox.currentIndexChanged.connect(self.updateChart)
        layout.addWidget(self.chartTypeComboBox)

        # Создание фигуры для диаграммы
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Начальное создание диаграммы
        self.updateChart(0)

    def updateChart(self, index):
        chartType = self.chartTypeComboBox.itemData(index)
        if chartType == "bar":
            self.createBarChart()
        elif chartType == "gantt":
            self.createGanttChart()

    def createBarChart(self):
        # Очистка фигуры и создание столбчатой диаграммы
        self.figure.clear()
        data = self.getBarChartData()

        ax = self.figure.add_subplot(111)

        # Конвертация данных словаря в списки для осей X и Y
        days = list(data.keys())
        counts = list(data.values())

        ax.bar(days, counts)  # Создание столбчатой диаграммы с правильными данными
        ax.set_title("Количество заездов по дням недели")
        ax.set_xlabel("День недели")
        ax.set_ylabel("Количество заездов")

        self.figure.canvas.draw()

    def createGanttChart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        data = self.getGanttChartData()

        try:
            for i, item in enumerate(data):
                start_date = datetime.datetime.strptime(item['Start'], "%Y-%m-%d")
                end_date = datetime.datetime.strptime(item['Finish'], "%Y-%m-%d")
                duration = (end_date - start_date).days
                start_num = mdates.date2num(start_date)

                ax.broken_barh([(start_num, duration)], (i - 0.4, 0.8), facecolors='tab:blue')

            ax.set_yticks(range(len(data)))
            ax.set_yticklabels([item['Room'] for item in data])
            ax.set_ylabel("Номера")

            ax.xaxis_date()
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            self.figure.autofmt_xdate()
            ax.set_title("Диаграмма Ганта бронирования номеров")

            self.figure.canvas.draw()
        except Exception as e:
            print(f"Ошибка при создании диаграммы Ганта: {e}")

    def getBarChartData(self):
        # Получение данных для столбчатой диаграммы
        conn = sqlite3.connect("bd_hotel.db")
        cursor = conn.cursor()
        query = """SELECT strftime('%w', check_in_date), COUNT(*) FROM bookings GROUP BY strftime('%w', check_in_date)"""
        cursor.execute(query)
        results = cursor.fetchall()
        data = {str(result[0]): result[1] for result in results}
        conn.close()
        return data

    def getGanttChartData(self):
        # Получение данных для диаграммы
        conn = sqlite3.connect("bd_hotel.db")
        cursor = conn.cursor()
        query = """
        SELECT room_number, check_in_date, check_out_date
        FROM bookings
        INNER JOIN rooms ON bookings.room_id = rooms.id
        """
        cursor.execute(query)
        results = cursor.fetchall()
        data = [{'Room': result[0], 'Start': result[1], 'Finish': result[2]} for result in results]
        conn.close()
        return data
