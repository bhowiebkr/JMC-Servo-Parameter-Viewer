import xml.etree.ElementTree as ET
import qdarktheme
import sys
import glob, os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QListWidget
from PySide6.QtWidgets import QTableWidget
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QHeaderView


# Define the main window
class MainWindow(QMainWindow):  # type: ignore
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("JMC Servo Parameters Viewer")

        self.resize(1000, 600)

        # Set the main window layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.tree = None

        # Layouts
        top_layout = QHBoxLayout()
        list_layouts = QHBoxLayout()
        help_layout = QHBoxLayout()

        # Widgets
        self.file_combo = QComboBox()
        self.category_list = QListWidget()
        self.category_list.setFixedWidth(250)
        self.param_table = QTableWidget()
        self.param_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.param_table.setSelectionMode(QAbstractItemView.SingleSelection)  # limit selection to a single row
        self.param_table.verticalHeader().setVisible(False)

        header_names = ["Code", "Name", "value", "Min-Max", "Units"]
        self.param_table.setColumnCount(len(header_names))

        self.param_table.setHorizontalHeaderLabels(header_names)
        header = self.param_table.horizontalHeader()
        # header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStretchLastSection(True)
        self.param_table.setColumnWidth(0, 60)
        self.param_table.setColumnWidth(1, 400)
        self.param_table.setColumnWidth(2, 60)
        self.param_table.setColumnWidth(3, 100)

        self.help = QTextEdit()
        self.help.setFixedHeight(100)

        # Add Widgets
        top_layout.addWidget(QLabel("Files"))
        top_layout.addWidget(self.file_combo)

        list_layouts.addWidget(self.category_list)
        list_layouts.addWidget(self.param_table)

        help_layout.addWidget(self.help)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(list_layouts)
        main_layout.addLayout(help_layout)

        # Logic
        self.file_combo.currentIndexChanged.connect(self.load_xml)
        self.category_list.itemClicked.connect(self.load_category)
        self.param_table.itemClicked.connect(self.show_help)

        # init
        self.read_XML_files()

    def read_XML_files(self):
        os.chdir(os.getcwd())

        for file in glob.glob("*.xml"):
            self.file_combo.addItem(file)

    def load_xml(self):
        # Get selected stuff
        category_sel = self.category_list.currentRow()

        param = self.param_table.currentRow()

        self.category_list.clear()
        xml_file = self.file_combo.currentText()

        self.tree = ET.parse(os.path.join(os.getcwd(), xml_file))
        root = self.tree.getroot()
        for tab in root:
            self.category_list.addItem(tab.tag)

        if category_sel == -1:
            return
        self.category_list.setCurrentRow(category_sel)
        self.load_category()
        self.param_table.selectRow(param)

    def load_category(self):
        self.param_table.setRowCount(0)
        try:
            category = self.category_list.currentItem().text()
        except AttributeError:
            # no attributes were loaded
            pass

        params = []

        root = self.tree.getroot()
        for cat in root:
            if str(cat.tag) == category:
                for param in cat:
                    params.append(param)

        rows = []

        for i, param in enumerate(params):
            name = str(param.find("Name").text).strip().lower()

            if name in ["keep", "read only"]:
                continue

            row = {}
            row["code"] = str(param.find("Code").text)
            row["name"] = str(param.find("Name").text)
            row["curr_value"] = str(param.find("Current_Value").text)
            row["setting_range"] = str(param.find("Setting_range").text)
            row["unit"] = str(param.find("Unit").text)
            row["descritpion"] = str(param.find("Descritpion").text)

            rows.append(row)

        for i, r in enumerate(rows):
            # Insert the row
            self.param_table.insertRow(self.param_table.rowCount())

            for col, p in enumerate([r["code"], r["name"], r["curr_value"], r["setting_range"], r["unit"]]):
                item = QTableWidgetItem()
                item.setText(p)

                if col == 0:
                    item.description = r["descritpion"]
                self.param_table.setItem(i, col, item)

    def show_help(self, item):
        row = item.row()
        item = self.param_table.item(row, 0)
        self.help.setText(item.description)


def start() -> None:
    app = QApplication(sys.argv)
    qdarktheme.setup_theme(additional_qss="QToolTip {color: black;}")

    window = MainWindow()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    start()

    # read()
