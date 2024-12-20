import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QComboBox, QLabel, QVBoxLayout, 
    QWidget, QPushButton, QTextEdit, QHBoxLayout, QLineEdit, QFormLayout
)
from PyQt6.QtCore import Qt, QTimer
import json
import mqtt_interaction


with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

current_server_id = 0


class StationInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stations_data = None

        self.setWindowTitle("Управление станциями")
        cp = self.screen().availableGeometry().center()
        WINDOW_WIDTH = 600
        WINDOW_HEIGHT = 400
        self.setGeometry(cp.x() - WINDOW_WIDTH // 2, cp.y() - WINDOW_HEIGHT // 2, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Основной виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Выпадающее меню для выбора режима работы
        self.server_label = QLabel(f"Текущий сервер:")
        self.server_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        server_combo_box = QComboBox()
        server_combo_box.addItems(map(lambda el: el["name"], config["servers"]))
        server_combo_box.currentTextChanged.connect(self.change_server)
        self.connect_to_server(0)

        # Поле ввода для станции
        station_input_layout = QFormLayout()
        self.station_input = QLineEdit()
        self.station_input.setPlaceholderText("Введите номер станции")
        self.station_input.textChanged.connect(self.validate_inputs)  # Сигнал для проверки ввода
        station_input_layout.addRow("Номер станции:", self.station_input)

        # Раздел состояния ячеек
        slots_label = QLabel("Состояние ячеек:")
        self.slots_display = QTextEdit()
        self.slots_display.setReadOnly(True)
        self.update_slots_display()

        # Поле ввода для ячейки
        slot_input_layout = QFormLayout()
        self.slot_input = QLineEdit()
        self.slot_input.setPlaceholderText("Введите номер ячейки")
        self.slot_input.textChanged.connect(self.validate_inputs)  # Сигнал для проверки ввода
        slot_input_layout.addRow("Номер ячейки:", self.slot_input)

        # Раздел кнопок
        button_layout = QHBoxLayout()
        self.take_umbrella_button = QPushButton("Взять зонт")
        self.put_umbrella_button = QPushButton("Положить зонт")
        self.take_umbrella_button.setEnabled(False)  # Отключаем кнопку при инициализации
        self.put_umbrella_button.setEnabled(False)
        
        self.take_umbrella_button.clicked.connect(self.take_umbrella)
        self.put_umbrella_button.clicked.connect(self.put_umbrella)

        button_layout.addWidget(self.take_umbrella_button)
        button_layout.addWidget(self.put_umbrella_button)
        
        # Добавление виджетов на главный layout
        layout.addWidget(self.server_label)
        layout.addWidget(server_combo_box)
        layout.addSpacing(10)
        layout.addLayout(station_input_layout)
        layout.addWidget(slots_label)
        layout.addWidget(self.slots_display)
        layout.addSpacing(10)
        layout.addLayout(slot_input_layout)
        layout.addLayout(button_layout)

        # Вызывать функцию self.update_slots_display() каждую секунду
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_slots_display)
        self.timer.start(500)

    def connect_to_server(self, server_id):
        """Подключение к серверу по его ID."""
        server = config["servers"][server_id]
        mqtt_interaction.connect(server["host"], server["port"], server["username"], server["password"], self.update_stations_data)

    def change_server(self, server):
        """Обновляет режим работы и выводит в консоль."""
        global current_server_id
        current_server_id = config["servers"].index(next(filter(lambda el: el["name"] == server, config["servers"])))
        print(f"Выбран сервер: {server} - {current_server_id}")


    def update_slots_display(self):
        """Обновляет текстовое поле с состоянием ячеек."""
        
        if self.stations_data is None or self.station_input.text() == "":
            self.slots_display.setText("")
            return
        if not self.station_input.text().isdigit():
            self.slots_display.setText("Некорректный номер станции")
            return
        display_text = ""
        station_id = int(self.station_input.text())
        if station_id not in self.stations_data:
            self.slots_display.setText("Данные об этой станции отсутствуют")
            return
        for slot_id in self.stations_data[station_id]:
            slot = self.stations_data[station_id][slot_id]
            lock = ""
            if slot["lock"] == "closed":
                lock = "закрыта"
            elif slot["lock"] == "opened":
                lock = "открыта"
            elif slot["lock"] == "close":
                lock = "закрывается"
            elif slot["lock"] == "open":
                lock = "открывается"
            
            display_text += f"Ячейка {slot_id}: {lock}, {'есть зонт' if slot['has_umbrella'] == 'y' else 'нет зонта'}\n"
        self.slots_display.setText(display_text)


    def validate_inputs(self):
        """Проверяет корректность ввода и включает/отключает кнопки."""
        station = self.station_input.text()
        slot = self.slot_input.text()
        
        # Проверка: оба поля должны содержать только цифры
        if station.isdigit() and slot.isdigit():
            self.take_umbrella_button.setEnabled(True)
            self.put_umbrella_button.setEnabled(True)
        else:
            self.take_umbrella_button.setEnabled(False)
            self.put_umbrella_button.setEnabled(False)

    def take_umbrella(self):
        """Обработчик кнопки 'Взять зонт'."""
        station = self.station_input.text()
        slot = self.slot_input.text()
        print(f"Попытка взять зонт: Станция {station}, Ячейка {slot}")
        # Логика обновления состояния может быть добавлена здесь
    
    def put_umbrella(self):
        """Обработчик кнопки 'Положить зонт'."""
        station = self.station_input.text()
        slot = self.slot_input.text()
        print(f"Попытка положить зонт: Станция {station}, Ячейка {slot}")
        # Логика обновления состояния может быть добавлена здесь
    
    def update_stations_data(self, data):
        """Обновляет данные о состоянии станций."""
        self.stations_data = data


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StationInterface()
    window.show()
    sys.exit(app.exec())
