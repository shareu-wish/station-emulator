import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QComboBox, QLabel, QVBoxLayout, 
    QWidget, QPushButton, QTextEdit, QHBoxLayout, QLineEdit, QFormLayout
)
from PyQt6.QtCore import Qt
import json
import mqtt_interaction


with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

current_server_id = 0


class StationInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление станциями")
        cp = self.screen().availableGeometry().center()
        WINDOW_WIDTH = 600
        WINDOW_HEIGHT = 400
        self.setGeometry(cp.x() - WINDOW_WIDTH // 2, cp.y() - WINDOW_HEIGHT // 2, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Состояние ячеек (пример данных)
        self.slots = [
            {"id": 1, "state": "открыта"},
            {"id": 2, "state": "закрыта"},
            {"id": 3, "state": "открыта"},
            {"id": 4, "state": "закрыта"}
        ]
        
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

    def connect_to_server(self, server_id):
        """Подключение к серверу по его ID."""
        server = config["servers"][server_id]
        mqtt_interaction.connect(server["host"], server["port"], server["username"], server["password"], self.update_slots_display)

    def change_server(self, server):
        """Обновляет режим работы и выводит в консоль."""
        global current_server_id
        current_server_id = config["servers"].index(next(filter(lambda el: el["name"] == server, config["servers"])))
        print(f"Выбран сервер: {server} - {current_server_id}")
    
    def update_slots_display(self, data=None):
        """Обновляет текстовое поле с состоянием ячеек."""
        # display_text = ""
        # for slot in self.slots:
        #     display_text += f"Ячейка {slot['id']}: {slot['state']}\n"
        # self.slots_display.setText(display_text)
        print(data)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StationInterface()
    window.show()
    sys.exit(app.exec())
