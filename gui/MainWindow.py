import json

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFrame, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QTableWidget, QTableWidgetItem, QSizePolicy, QSpacerItem, QTabWidget, QComboBox, QHeaderView
import pandas as pd

import mrp.mrp as mrp
import mrp.msp as msp

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Skateboard MRP")
        self.setWindowIcon(QIcon("images/icon.png"))
        self.resize(QSize(1280, 720))

        self.widget = QWidget()

        self.main_layout = QVBoxLayout()

        self.hlayout = QHBoxLayout()
        self.hlayout.setContentsMargins(40, 20, 40, 20)

        self.widget.setLayout(self.main_layout)
        self.setCentralWidget(self.widget)

        self.vleft_layout = QVBoxLayout()
        self.vright_layout = QVBoxLayout()

        self.vleft_layout.setContentsMargins(0, 0, 30, 0)
        self.vright_layout.setContentsMargins(30, 12, 0, 0)

        self.hline = QFrame()
        self.hline.setFrameShape(QFrame.Shape.HLine)
        self.hline.setFrameShadow(QFrame.Shadow.Raised)
        self.hline.setProperty("class", "hline")

        self.vline = QFrame()
        self.vline.setFrameShape(QFrame.Shape.VLine)
        self.vline.setFrameShadow(QFrame.Shadow.Raised)

        self.preset_layout = QVBoxLayout()
        self.preset_layout.setContentsMargins(50, 0, 50, 15)

        self.preset_dropdown_menu = QComboBox()
        self.preset_dropdown_menu.setPlaceholderText("Wybierz preset")
        self.preset_layout.addWidget(self.preset_dropdown_menu)

        self.materials_label = QLabel("MATERIAŁY")
        self.orders_label = QLabel("ZAMÓWIENIA")

        self.materials_table = self.init_materials_table()
        self.orders_table = self.init_orders_table()

        self.error_label = QLabel()
        self.error_label.setObjectName("error_label")

        self.spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.vleft_layout.addWidget(self.materials_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.vleft_layout.addWidget(self.materials_table)
        self.vleft_layout.addWidget(self.orders_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.vleft_layout.addWidget(self.orders_table)

        self.ghp_label = QLabel("GŁÓWNY HARMONOGRAM PRODUKCJI")
        self.ghp_table = self.init_ghp_table()

        self.mrp_label = QLabel("MRP")

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)

        self.wheel_tab = QWidget()
        self.wheel_tab.setObjectName("wheel")
        self.axle_tab = QWidget()
        self.axle_tab.setObjectName("axle")
        self.truck_tab = QWidget()
        self.truck_tab.setObjectName("truck")
        self.board_tab = QWidget()
        self.board_tab.setObjectName("board")

        self.tabs.addTab(self.wheel_tab, "Kółko")
        self.tabs.addTab(self.axle_tab, "Ośka")
        self.tabs.addTab(self.truck_tab, "Truck")
        self.tabs.addTab(self.board_tab, "Deska")

        self.vright_layout.addWidget(self.ghp_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.vright_layout.addWidget(self.ghp_table)
        self.vright_layout.addWidget(self.mrp_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.vright_layout.addWidget(self.tabs)

        self.hlayout.addLayout(self.vleft_layout)
        self.hlayout.addWidget(self.vline)
        self.hlayout.addLayout(self.vright_layout)

        self.main_layout.addItem(self.spacer)
        self.main_layout.addLayout(self.preset_layout)
        self.main_layout.addWidget(self.hline)
        self.main_layout.addLayout(self.hlayout)
        self.main_layout.addWidget(self.error_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addItem(self.spacer)

        self.init_presets()

        self.materials_table.cellChanged.connect(self.save_changed_materials_value)
        self.orders_table.cellChanged.connect(self.save_changed_order_value)

        self.init_tabs()

        self.init_calculations()

        self.preset_dropdown_menu.currentIndexChanged.connect(self.change_preset)

    def init_materials_table(self):
        with open("data/materials.json", 'r', encoding="utf-8") as f:
            materials = json.load(f)

        table = QTableWidget(5,5)
        table.setHorizontalHeaderLabels(["Czas realizacji", "Na stanie", "Wielkość partii", "Wymagana ilość", "Poziom BOM"])
        table.setVerticalHeaderLabels(["Deskorolka", "Deska", "Truck", "Ośka", "Kółko"])

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
        return table

    def init_orders_table(self):
        with open("data/orders.json", 'r', encoding="utf-8") as f:
            orders_dict = json.load(f)

        table = QTableWidget(1, 7)
        table.setHorizontalHeaderLabels(["1", "2", "3", "4", "5", "6", "7"])
        table.setVerticalHeaderLabels(["Liczba"])

        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        table.horizontalHeader().setDisabled(True)
        table.verticalHeader().setDisabled(True)

        column = 0
        for dictionary in orders_dict:
            item = QTableWidgetItem(str(dictionary["orders"]))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(0, column, item)
            column += 1

        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table

    def init_ghp_table(self):
        table = QTableWidget(3, 7)
        table.setHorizontalHeaderLabels(["1", "2", "3", "4", "5", "6", "7"])
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
        return table

    def init_mrp_table(self):
        table = QTableWidget(6, 6)
        table.setHorizontalHeaderLabels(["1", "2", "3", "4", "5", "6", "7"])
        table.setVerticalHeaderLabels(["Całkowite zapotrzebowanie", "Planowane przyjęcia", "Przewidywane na stanie", "Zapotrzebowanie netto", "Planowane zamówienia", "Planowane przyjęcie zamówień"])

        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        table.horizontalHeader().setDisabled(True)
        table.verticalHeader().setDisabled(True)

        for col in range(0, 6):
            for row in range(0, 6):
                item = QTableWidgetItem("0")
                item.setFlags(Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, col, item)

        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table

    def init_tabs(self):
        for i in range(0, 4):
            tab = self.tabs.widget(i)
            mrp_table = self.init_mrp_table()

            vlayout = QVBoxLayout()
            vlayout.addWidget(mrp_table)
            tab.setLayout(vlayout)

    def init_presets(self):
        with open("data/presets.json", 'r', encoding="utf-8") as f:
            presets = json.load(f)

        for preset in presets:
            self.preset_dropdown_menu.addItem(preset["name"])

    def change_preset(self, index):
        print("chuj")
        with open("data/presets.json", 'r', encoding="utf-8") as f:
            presets = json.load(f)

        preset_name = self.preset_dropdown_menu.itemText(index)

        stack = presets
        preset = ""
        while stack:
            current_node = stack.pop()
            if isinstance(current_node, dict):
                if current_node.get('name') == preset_name:
                    preset = current_node
                    break
                stack.extend(current_node.values())
            elif isinstance(current_node, list):
                stack.extend(current_node)

        for x in range(0, 5):
            for y in range(0, 5):
                self.materials_table.item(x, y).setText(str(list(list(preset["values"]["materials"].values())[x].values())[y]))

        for order in preset["values"]["orders"]:
            self.orders_table.item(0, order["week"] - 1).setText(str(order["orders"]))

    def save_changed_materials_value(self, row, column):
        value = self.materials_table.item(row, column).text()

        with open("data/materials.json", 'r', encoding="utf-8") as f:
            materials = json.load(f)

        if row == 0:
            materials.get("skateboard")[list(materials.get("skateboard").keys())[column]] = int(value)
        elif row == 1:
            materials.get("board")[list(materials.get("board").keys())[column]] = int(value)
        elif row == 2:
            materials.get("truck")[list(materials.get("truck").keys())[column]] = int(value)
        elif row == 3:
            materials.get("axle")[list(materials.get("axle").keys())[column]] = int(value)
        elif row == 4:
            materials.get("wheel")[list(materials.get("wheel").keys())[column]] = int(value)

        with open("data/materials.json", 'w', encoding="utf-8") as f:
            json.dump(materials, f, indent=2)

        self.error_label.setText("")
        self.init_calculations()

    def save_changed_order_value(self, row, column):
        value = self.orders_table.item(row, column).text()

        with open("data/orders.json", 'r', encoding="utf-8") as f:
            orders_dict = json.load(f)

        orders_dict[column]["orders"] = int(value)

        with open("data/orders.json", 'w', encoding="utf-8") as f:
            json.dump(orders_dict, f, indent=1)

        self.error_label.setText("")
        self.init_calculations()

    def fill_mrp_tab(self, tab, mrp):
        for col in range(0, 6):
            for row in range(0, 6):
                item = QTableWidgetItem("0")
                item.setFlags(Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tab.layout().itemAt(0).widget().item(row, col).setText((str(mrp.iloc[row, col])))
    
    def find_tab(self, name):
         current_tab = None
         for i in range(0, self.tabs.count()):
            tab = self.tabs.widget(i)
            if tab.objectName() == name:
                current_tab = tab
         return current_tab
            

    def init_calculations(self):
        try:
            materials = pd.read_json("data/materials.json")
            msp_result =  msp.build_msp(materials.skateboard)

            for col in range(0, 7):
                for row in range(0, 3):
                    item = QTableWidgetItem("0")
                    item.setFlags(Qt.ItemFlag.ItemIsEditable)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.ghp_table.item(row, col).setText((str(msp_result.iloc[row, col])))


            skateboards_demand = msp_result.iloc[1].to_numpy().tolist()
            first_level_materials_demand = [0] * len(skateboards_demand) 
            for index, val in enumerate(skateboards_demand):
                first_level_materials_demand[index] = 0
                if(val <= 0): 
                    continue
                weekOrder = index - materials.skateboard.ready_in_weeks
                if(weekOrder < 0): 
                    first_level_materials_demand[0] = val
                    continue
                first_level_materials_demand[weekOrder] = val

            truck_demand = list(map(lambda x: x  * materials.truck.units_required, first_level_materials_demand))
            mrp_truck = mrp.build_mrp(truck_demand, materials.truck)
            truck_tab = self.find_tab(materials.truck.name)
            self.fill_mrp_tab(truck_tab, mrp_truck)

            mrp_board = mrp.build_mrp(first_level_materials_demand, materials.board)
            board_tab = self.find_tab(materials.board.name)
            self.fill_mrp_tab(board_tab, mrp_board)

            axle_demand = mrp_truck.iloc[4].to_numpy().tolist()
            mrp_axle = mrp.build_mrp(axle_demand, materials.axle)
            axle_tab = self.find_tab(materials.axle.name)
            self.fill_mrp_tab(axle_tab, mrp_axle)

            wheels_demand = list(map(lambda x: x  * materials.wheel.units_required, mrp_truck.iloc[4].to_numpy().tolist()))
            mrp_wheels = mrp.build_mrp(wheels_demand, materials.wheel)
            wheel_tab = self.find_tab(materials.wheel.name)
            self.fill_mrp_tab(wheel_tab, mrp_wheels)
        
        except Exception as e:
            self.error_label.setText(str(e))