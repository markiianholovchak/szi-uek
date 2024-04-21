import json

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QTableWidget, QTableWidgetItem, QSizePolicy, QSpacerItem, QTabWidget, QComboBox, QHeaderView

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Skateboard MRP")
        self.setWindowIcon(QIcon("images/icon.png"))
        self.resize(QSize(1280, 720))

        self.widget = QWidget()

        self.hlayout = QHBoxLayout()
        self.hlayout.setContentsMargins(40, 20, 40, 20)

        self.widget.setLayout(self.hlayout)
        self.setCentralWidget(self.widget)

        self.init_ui()

    def init_ui(self):
        vleft_layout = QVBoxLayout()
        vright_layout = QVBoxLayout()

        vleft_layout.setContentsMargins(30, 10, 30, 10)
        vright_layout.setContentsMargins(30, 10, 30, 10)

        preset_dropdown_menu = QComboBox()

        materials_label = QLabel("Materiały")
        orders_label = QLabel("Zamówienia")

        materials_table = self.init_materials_table()
        orders_table = self.init_orders_table()

        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        vleft_layout.addWidget(preset_dropdown_menu)
        vleft_layout.addWidget(materials_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        vleft_layout.addWidget(materials_table)
        vleft_layout.addWidget(orders_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        vleft_layout.addWidget(orders_table)
        vleft_layout.addItem(spacer)

        ghp_label = QLabel("Główny harmonogram producji")
        ghp_table, ghp_on_storage_label = self.init_ghp_table()

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.South)

        skateboard_tab = QWidget()
        wheel_tab = QWidget()
        axle_tab = QWidget()
        truck_tab = QWidget()
        board_tab = QWidget()

        tabs.addTab(skateboard_tab, "Deskorolka")
        tabs.addTab(wheel_tab, "Kółko")
        tabs.addTab(axle_tab, "Ośka")
        tabs.addTab(truck_tab, "Truck")
        tabs.addTab(board_tab, "Deska")

        vright_layout.addWidget(ghp_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        vright_layout.addWidget(ghp_table)
        vright_layout.addWidget(ghp_on_storage_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        vright_layout.addWidget(tabs)

        self.hlayout.addLayout(vleft_layout)
        self.hlayout.addLayout(vright_layout)

    def init_materials_table(self):
        with open("data/materials.json") as f:
            materials = json.load(f)

        table = QTableWidget(5,5)
        table.setHorizontalHeaderLabels(["Czas realizacji", "Na stanie", "Wielkość partii", "Wymagana ilość", "Poziom BOM"])
        table.setVerticalHeaderLabels(["Deskorolka", "Kółko", "Ośka", "Truck", "Deska"])

        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        table.horizontalHeader().setDisabled(True)
        table.verticalHeader().setDisabled(True)

        row = 0
        for component_name, component_data in materials.items():
            col = 0
            for key, value in component_data.items():
                item = QTableWidgetItem(str(value))
                if key == 'level':
                    item.setFlags(Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, col, item)
                col += 1
            row += 1

        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.sortByColumn(4, Qt.SortOrder.AscendingOrder)
        return table

    def init_orders_table(self):
        with open("data/orders.json") as f:
            orders_dict = json.load(f)

        table = QTableWidget(1, 7)
        table.setHorizontalHeaderLabels(["Tydzień 1", "Tydzień 2", "Tydzień 3", "Tydzień 4", "Tydzień 5", "Tydzień 6", "Tydzień 7"])
        table.setVerticalHeaderLabels(["Liczba"])

        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        table.horizontalHeader().setDisabled(True)
        table.verticalHeader().setDisabled(True)

        column = 0
        for dict in orders_dict:
            item = QTableWidgetItem(str(dict["orders"]))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(0, column, item)
            column += 1

        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table

    def init_ghp_table(self):
        on_storage_label = QLabel(f"Na stanie: {0}")

        table = QTableWidget(3, 7)
        table.setHorizontalHeaderLabels(["Tydzień 1", "Tydzień 2", "Tydzień 3", "Tydzień 4", "Tydzień 5", "Tydzień 6", "Tydzień 7"])
        table.setVerticalHeaderLabels(["Przewidywany popyt", "Produkcja", "Dostępne"])

        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        table.horizontalHeader().setDisabled(True)
        table.verticalHeader().setDisabled(True)

        for col in range(0, 7):
            for row in range(0, 3):
                item = QTableWidgetItem("0")
                item.setFlags(Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, col, item)

        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table, on_storage_label