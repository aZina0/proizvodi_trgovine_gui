from PySide6.QtWidgets import *
from PySide6.QtCore import Signal
import sys
import os.path
import initialize_database


# Ako ne postoji baza podataka, napravi novu s nekim pocetnim podatcima
if not os.path.exists("database.db"):
	initialize_database.initialize()




sys.argv += ['-platform', 'windows:darkmode=2']
app = QApplication(sys.argv)
app.setStyle('Fusion')
app.setStyleSheet(open('styles.css').read())


class Window(QMainWindow):
	resize_signal = Signal(int, int)

	def __init__(self):
		super().__init__()
		self.setFixedSize(1000, 750)
		self.setMinimumSize(400, 400)

	def resizeEvent(self, event):
		width = event.size().width()
		height = event.size().height()
		self.resize_signal.emit(width, height)
		super().resizeEvent(event)


class CategoryEditWidget(QWidget):
	def __init__(self, parent):
		super().__init__(parent)
		self.setMinimumSize(700, 400)
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
		self.add_button.setStyleSheet('background-color: darkgreen; margin-left: 150')
		self.add_layout.addWidget(self.add_button)


		self.rename_widget = QGroupBox("Preimenuj kategoriju", self)
		self.rename_layout = QVBoxLayout(self.rename_widget)
		self.layout.addWidget(self.rename_widget, 1, 1)

		self.rename_text = QLineEdit("Novo ime kategorije: ")
		self.rename_layout.addWidget(self.rename_text)

		self.rename_button = QPushButton("Preimenuj")
		self.rename_button.setStyleSheet('margin-left: 150')
		self.rename_layout.addWidget(self.rename_button)


		self.remove_widget = QGroupBox("Izbriši kategoriju", self)
		self.remove_layout = QVBoxLayout(self.remove_widget)
		self.layout.addWidget(self.remove_widget, 2, 1)

		self.remove_button = QPushButton("Izbriši")
		self.remove_button.setStyleSheet('background-color: darkred; margin-left: 150')
		self.remove_layout.addWidget(self.remove_button)


	def window_resized(self, width, height):
		self.setFixedSize(width, height)




window = Window()

category_edit_widget = CategoryEditWidget(window)
window.resize_signal.connect(category_edit_widget.window_resized)

window.show()

app.exec()