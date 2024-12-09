from PySide6.QtWidgets import *
from PySide6.QtCore import Signal
import sys
import os.path
import initialize_database


# Ako ne postoji baza podataka, napravi novu s nekim pocetnim podatcima
if not os.path.exists("database.db"):
	initialize_database.initialize()




sys.argv += ["-platform", "windows:darkmode=2"]
app = QApplication(sys.argv)
app.setStyle("Fusion")
app.setStyleSheet(open("styles.css").read())


class Window(QMainWindow):

	def __init__(self):
		super().__init__()
		self.setMinimumSize(794, 400)
		self.setWindowTitle("Uređivač proizvoda i njihovih svojstava")

		self.main_widget = QWidget(self)
		self.setCentralWidget(self.main_widget)
		self.layout = QGridLayout(self.main_widget)
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.layout.setRowStretch(1, 1)
		self.layout.setColumnStretch(0, 1)



class ModeBar(QWidget):
	def __init__(self, parent):
		super().__init__(parent)

		self.setStyleSheet("""
			QPushButton {
				background-color: #000000;
				border: 1px solid #878787;
				margin: 0;
				padding: 0px 10px
			}

			QPushButton::checked {
				background-color: #1E1E1E;
				border-bottom: 0px
			}
		""")

		self.layout = QGridLayout(self)
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.layout.setSpacing(0)

		self.category_edit_button = QPushButton("Dodaj/uredi kategorije")
		self.category_edit_button.setCheckable(True)
		self.category_edit_button.clicked.connect(self.category_edit_clicked)
		self.layout.addWidget(self.category_edit_button, 0, 0)

		self.property_edit_button = QPushButton("Dodaj/uredi grupe svojstava")
		self.property_edit_button.setCheckable(True)
		self.property_edit_button.clicked.connect(self.property_edit_clicked)
		self.layout.addWidget(self.property_edit_button, 0, 1)

		self.descriptor_edit_button = QPushButton("Dodaj/uredi svojstva")
		self.descriptor_edit_button.setCheckable(True)
		self.descriptor_edit_button.clicked.connect(self.descriptor_edit_clicked)
		self.layout.addWidget(self.descriptor_edit_button, 0, 2)

		self.item_edit_button = QPushButton("Dodaj/uredi proizvode")
		self.item_edit_button.setCheckable(True)
		self.item_edit_button.clicked.connect(self.item_edit_clicked)
		self.layout.addWidget(self.item_edit_button, 0, 3)


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
		self.layout = QGridLayout(self)
		self.layout.setRowStretch(0, 2)
		self.layout.setRowStretch(1, 2)
		self.layout.setRowStretch(2, 1)
		self.layout.setColumnStretch(0, 1)
		self.layout.setColumnStretch(1, 1)


		self.list_widget = QGroupBox("Lista kategorija", self)
		self.list_layout = QVBoxLayout(self.list_widget)
		self.layout.addWidget(self.list_widget, 0, 0, 3, 1)

		self.list = QScrollArea(self)
		self.list_layout.addWidget(self.list)


		self.add_widget = QGroupBox("Dodaj kategoriju", self)
		self.add_layout = QVBoxLayout(self.add_widget)
		self.layout.addWidget(self.add_widget, 0, 1)

		self.add_text = QLineEdit("ime kategorije: ")
		self.add_layout.addWidget(self.add_text)

		self.add_button = QPushButton("Dodaj")
		self.add_button.setStyleSheet("background-color: darkgreen; margin-left: 150")
		self.add_layout.addWidget(self.add_button)


		self.rename_widget = QGroupBox("Preimenuj kategoriju", self)
		self.rename_layout = QVBoxLayout(self.rename_widget)
		self.layout.addWidget(self.rename_widget, 1, 1)

		self.rename_text = QLineEdit("Novo ime kategorije: ")
		self.rename_layout.addWidget(self.rename_text)

		self.rename_button = QPushButton("Preimenuj")
		self.rename_button.setStyleSheet("margin-left: 150")
		self.rename_layout.addWidget(self.rename_button)


		self.remove_widget = QGroupBox("Izbriši kategoriju", self)
		self.remove_layout = QVBoxLayout(self.remove_widget)
		self.layout.addWidget(self.remove_widget, 2, 1)

		self.remove_button = QPushButton("Izbriši")
		self.remove_button.setStyleSheet("background-color: darkred; margin-left: 150")
		self.remove_layout.addWidget(self.remove_button)





window = Window()
mode_bar = ModeBar(window)
category_edit_widget = CategoryEditWidget(window)

window.layout.addWidget(mode_bar, 0, 0)
window.layout.addWidget(category_edit_widget, 1, 0)
window.show()

app.exec()