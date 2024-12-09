from PySide6.QtWidgets import *
import sys
import sqlite3
import os.path
import initialize_database


# Ako ne postoji baza podataka, napravi novu s nekim pocetnim podatcima
if not os.path.exists("database.db"):
	initialize_database.initialize()




sys.argv += ['-platform', 'windows:darkmode=2']
app = QApplication(sys.argv)
app.setStyle('Fusion')

window = QMainWindow()



class CategoryEditWidget(QWidget):
	def __init__(self, parent):
		super().__init__(parent)
		self.setGeometry(0, 0, 700, 700)
		self.setStyleSheet('background-color: darkred')

		self.add_widget = QWidget(self)
		self.add_text = QLineEdit("ime kategorije: ", self.add_widget)
		self.add_button = QPushButton("Dodaj kategoriju", self.add_widget)

		self.rename_remove_layout = QGridLayout(self)
		self.rename_remove_widget = QWidget(self)
		# self.rename_remove_widget.col
		self.rename_remove_widget.setLayout(self.rename_remove_layout)

		self.list = QScrollArea(self.rename_remove_widget)
		self.rename_remove_layout.addWidget(self.list, 0, 0, 3, 2)

		self.rename_text = QLineEdit("Novo ime kategorije: ", self.rename_remove_widget)
		self.rename_remove_layout.addWidget(self.rename_text, 0, 2, 1, 1)

		self.rename_button = QPushButton("Preimenuj kategoriju: ", self.rename_remove_widget)
		self.rename_remove_layout.addWidget(self.rename_button, 1, 2, 1, 1)

		self.remove_button = QPushButton("Ukloni kategoriju")
		self.rename_remove_layout.addWidget(self.remove_button, 2, 2, 1, 1)


		self.rename_remove_widget.setFixedSize(self.rename_remove_layout.sizeHint())


		
		self.layout = QGridLayout(self)
		self.setLayout(self.layout)
		self.layout.addWidget(self.add_widget, 0, 0)
		self.layout.addWidget(self.rename_remove_widget, 0, 1)


category_edit_widget = CategoryEditWidget(window)



window.setGeometry(0, 0, 1000, 750)
window.show()





app.exec()