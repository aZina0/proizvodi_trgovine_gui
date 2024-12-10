from PySide6.QtWidgets import *
from PySide6.QtCore import Signal
import sys
import os.path
import initialize_database


# Ako ne postoji baza podataka, napravi novu s nekim pocetnim podatcima
if not os.path.exists("database.db"):
	initialize_database.initialize()



app = QApplication(sys.argv)
app.setStyle("Fusion")
app.setStyleSheet(
"""
QGroupBox {
	font: bold;
	border: 1px solid rgb(53, 53, 53);
	border-radius: 6px;
	margin-top: 6px;
}

QGroupBox::title {
	subcontrol-origin: margin;
	left: 7px;
	padding: 0px 5px 0px 5px;
}

QPushButton {
	font-size: 13pt;
	height: 30;
}
"""
)



class CustomScrollList(QScrollArea):
	def __init__(self, parent):
		super().__init__(parent)

		self.setStyleSheet("""
			QPushButton {
				background-color: #292929;
				border: 1px solid #393939;
				padding: 0px 10px;
				font-size: 10pt;
				text-align: left;
			}

			QPushButton::checked {
				background-color: #393939;
			}
		""")

		self.base_widget = QWidget(self)
		self.base_layout = QGridLayout(self.base_widget)
		self.base_layout.setContentsMargins(0, 0, 0, 0)
		self.base_layout.setSpacing(0)
		self.setWidget(self.base_widget)
		self.setWidgetResizable(True)

		self.items = {}

		self.selected_item = None


	def add_item(self, text):
		self.items[text] = QPushButton(text)
		self.items[text].setCheckable(True)
		self.items[text].clicked.connect(lambda: self.item_clicked(text))
		self.base_layout.addWidget(self.items[text], len(self.items) - 1, 0)

	def item_clicked(self, clicked_item_text):
		for item_text in self.items:
			if item_text != clicked_item_text:
				self.items[item_text].setChecked(False)





class Window(QMainWindow):

	def __init__(self):
		super().__init__()
		self.setMinimumSize(794, 400)
		self.setWindowTitle("Uređivač proizvoda i njihovih svojstava")

		self.main_widget = QWidget(self)
		self.setCentralWidget(self.main_widget)
		self.base_layout = QGridLayout(self.main_widget)
		self.base_layout.setContentsMargins(0, 0, 0, 0)
		self.base_layout.setRowStretch(1, 1)
		self.base_layout.setColumnStretch(0, 1)



class ModeBar(QWidget):
	def __init__(self, parent):
		super().__init__(parent)

		self.setStyleSheet("""
			QPushButton {
				background-color: #000000;
				border: 1px solid #878787;
				padding: 0px 10px
			}

			QPushButton::checked {
				background-color: #1E1E1E;
				border-bottom: 0px
			}
		""")

		self.base_layout = QGridLayout(self)
		self.base_layout.setContentsMargins(0, 0, 0, 0)
		self.base_layout.setSpacing(0)

		self.category_edit_button = QPushButton("Dodaj/uredi kategorije")
		self.category_edit_button.setCheckable(True)
		self.category_edit_button.clicked.connect(self.category_edit_clicked)
		self.base_layout.addWidget(self.category_edit_button, 0, 0)

		self.property_edit_button = QPushButton("Dodaj/uredi grupe svojstava")
		self.property_edit_button.setCheckable(True)
		self.property_edit_button.clicked.connect(self.property_edit_clicked)
		self.base_layout.addWidget(self.property_edit_button, 0, 1)

		self.descriptor_edit_button = QPushButton("Dodaj/uredi svojstva")
		self.descriptor_edit_button.setCheckable(True)
		self.descriptor_edit_button.clicked.connect(self.descriptor_edit_clicked)
		self.base_layout.addWidget(self.descriptor_edit_button, 0, 2)

		self.item_edit_button = QPushButton("Dodaj/uredi proizvode")
		self.item_edit_button.setCheckable(True)
		self.item_edit_button.clicked.connect(self.item_edit_clicked)
		self.base_layout.addWidget(self.item_edit_button, 0, 3)


	def category_edit_clicked(self):
		self.property_edit_button.setChecked(False)
		self.descriptor_edit_button.setChecked(False)
		self.item_edit_button.setChecked(False)

	def property_edit_clicked(self):
		self.category_edit_button.setChecked(False)
		self.descriptor_edit_button.setChecked(False)
		self.item_edit_button.setChecked(False)

	def descriptor_edit_clicked(self):
		self.category_edit_button.setChecked(False)
		self.property_edit_button.setChecked(False)
		self.item_edit_button.setChecked(False)

	def item_edit_clicked(self):
		self.category_edit_button.setChecked(False)
		self.property_edit_button.setChecked(False)
		self.descriptor_edit_button.setChecked(False)



class CategoryEditWidget(QWidget):
	def __init__(self, parent):
		super().__init__(parent)
		self.base_layout = QGridLayout(self)
		self.base_layout.setRowStretch(0, 2)
		self.base_layout.setRowStretch(1, 2)
		self.base_layout.setRowStretch(2, 1)
		self.base_layout.setColumnStretch(0, 1)
		self.base_layout.setColumnStretch(1, 1)


		self.list_widget = QGroupBox("Lista kategorija", self)
		self.list_layout = QVBoxLayout(self.list_widget)
		self.base_layout.addWidget(self.list_widget, 0, 0, 3, 1)

		self.list = CustomScrollList(self.list_widget)
		self.list_layout.addWidget(self.list)
		self.list.add_item("Odjeca1")
		self.list.add_item("Odjeca2")
		self.list.add_item("Odjeca3")
		self.list.add_item("Odjeca4")
		self.list.add_item("Odjeca5")
		self.list.add_item("Odjeca6")
		self.list.add_item("Odjeca7")
		self.list.add_item("Odjeca8")
		self.list.add_item("Odjeca9")
		self.list.add_item("Odjeca10")
		self.list.add_item("Odjeca11")
		self.list.add_item("Odjeca12")
		self.list.add_item("Odjeca13")
		self.list.add_item("Odjeca14")

		self.add_widget = QGroupBox("Dodaj kategoriju", self)
		self.add_layout = QVBoxLayout(self.add_widget)
		self.base_layout.addWidget(self.add_widget, 0, 1)

		self.add_text = QLineEdit()
		self.add_text.setPlaceholderText("naziv kategorije")
		self.add_layout.addWidget(self.add_text)

		self.add_button = QPushButton("Dodaj")
		self.add_button.setStyleSheet("background-color: darkgreen; margin-left: 150")
		self.add_layout.addWidget(self.add_button)


		self.rename_widget = QGroupBox("Preimenuj kategoriju", self)
		self.rename_layout = QVBoxLayout(self.rename_widget)
		self.base_layout.addWidget(self.rename_widget, 1, 1)

		self.rename_text = QLineEdit()
		self.rename_text.setPlaceholderText("naziv kategorije")
		self.rename_layout.addWidget(self.rename_text)

		self.rename_button = QPushButton("Preimenuj")
		self.rename_button.setStyleSheet("margin-left: 150")
		self.rename_layout.addWidget(self.rename_button)


		self.remove_widget = QGroupBox("Izbriši kategoriju", self)
		self.remove_layout = QVBoxLayout(self.remove_widget)
		self.base_layout.addWidget(self.remove_widget, 2, 1)

		self.remove_button = QPushButton("Izbriši")
		self.remove_button.setStyleSheet("background-color: darkred; margin-left: 150")
		self.remove_layout.addWidget(self.remove_button)





window = Window()
mode_bar = ModeBar(window)
category_edit_widget = CategoryEditWidget(window)

window.base_layout.addWidget(mode_bar, 0, 0)
window.base_layout.addWidget(category_edit_widget, 1, 0)
window.show()

app.exec()