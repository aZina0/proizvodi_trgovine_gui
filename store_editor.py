from PySide6.QtWidgets import *
from PySide6.QtCore import Signal
import sys
import os
import database_interaction


# os.remove("database.db")
# Ako ne postoji baza podataka, napravi novu s nekim pocetnim podatcima
if not os.path.exists("database.db"):
	database_interaction.initialize()



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

	QLineEdit {
		font-size: 11pt;
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
				margin-left: 0;
			}

			QPushButton::checked {
				background-color: #393939;
			}
		""")

		self.base_widget = QWidget(self)
		self.base_layout = QVBoxLayout(self.base_widget)
		self.base_layout.setContentsMargins(0, 0, 0, 0)
		self.base_layout.setSpacing(0)
		self.base_layout.setSizeConstraint(QLayout.SetMaximumSize)
		self.setWidget(self.base_widget)
		self.setWidgetResizable(True)

		self.buttons = {}


	def button_clicked(self):
		clicked_button_text = self.sender().property("name")
		for button_text in self.buttons:
			if button_text != clicked_button_text:
				self.buttons[button_text].setChecked(False)


	def create_button(self, text):
		text = text.lower()

		button = QPushButton(text.capitalize())
		button.setCheckable(True)
		button.setProperty("name", text)
		button.clicked.connect(self.button_clicked)
		self.base_layout.addWidget(button)
		self.buttons[text] = button

		return self.buttons[text]


	def rename_button(self, current_text, new_text):
		button = self.buttons.pop(current_text)
		button.setProperty("name", new_text)
		button.setText(new_text.capitalize())
		self.buttons[new_text] = button


	def delete_button(self, text):
		button = self.buttons.pop(text)
		button.clicked.disconnect()
		self.base_layout.removeWidget(button)
		button.deleteLater()





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
				font-size: 13pt;
				height: 30;
				background-color: #000000;
				border: 1px solid #878787;
				padding: 0px 10px;
			}

			QPushButton::checked {
				background-color: #1E1E1E;
				border-bottom: 0px;
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

		self.setStyleSheet(
			"""
			QPushButton {
				font-size: 13pt;
				height: 30;
				margin-left: 150;
			}
			"""
		)



		self.base_layout = QGridLayout(self)
		self.base_layout.setRowStretch(0, 2)
		self.base_layout.setRowStretch(1, 2)
		self.base_layout.setRowStretch(2, 1)
		self.base_layout.setColumnStretch(0, 1)
		self.base_layout.setColumnStretch(1, 1)

		self.list_widget = QGroupBox("Kategorije", self)
		self.list_layout = QVBoxLayout(self.list_widget)
		self.base_layout.addWidget(self.list_widget, 0, 0, 3, 1)

		self.list = CustomScrollList(self.list_widget)
		self.list_layout.addWidget(self.list)
		for category in database_interaction.get_categories():
			button = self.list.create_button(category)
			button.clicked.connect(self.category_clicked)


		self.add_widget = QGroupBox("Dodaj kategoriju", self)
		self.add_layout = QVBoxLayout(self.add_widget)
		self.base_layout.addWidget(self.add_widget, 0, 1)

		self.add_text = QLineEdit()
		self.add_text.setPlaceholderText("naziv nove kategorije")
		self.add_layout.addWidget(self.add_text)

		self.add_button = QPushButton("Dodaj")
		self.add_button.setStyleSheet(
			"""
			QPushButton {
				background-color: #008900;
			}
			"""
		)
		self.add_button.clicked.connect(self.add_button_clicked)
		self.add_layout.addWidget(self.add_button)


		self.rename_widget = QGroupBox("Preimenuj kategoriju", self)
		self.rename_layout = QVBoxLayout(self.rename_widget)
		self.base_layout.addWidget(self.rename_widget, 1, 1)

		self.rename_text = QLineEdit()
		self.rename_text.setPlaceholderText("novi naziv kategorije")
		self.rename_layout.addWidget(self.rename_text)

		self.rename_button = QPushButton("Preimenuj")
		self.rename_button.setStyleSheet(
			"""
			QPushButton {
				background-color: #666666;
			}

			QPushButton::disabled {
				background-color: #474747;
				color: #727272;
			}
			"""
		)
		self.rename_button.clicked.connect(self.rename_button_clicked)
		self.rename_layout.addWidget(self.rename_button)


		self.remove_widget = QGroupBox("Izbriši kategoriju", self)
		self.remove_layout = QVBoxLayout(self.remove_widget)
		self.base_layout.addWidget(self.remove_widget, 2, 1)

		self.remove_button = QPushButton("Izbriši")
		self.remove_button.setStyleSheet(
			"""
			QPushButton {
				background-color: #890000;
			}

			QPushButton::disabled {
				background-color: #560000;
				color: #895959;
			}
			"""
		)
		self.remove_button.clicked.connect(self.remove_button_clicked)
		self.remove_layout.addWidget(self.remove_button)

		self.rename_widget.setDisabled(True)
		self.remove_widget.setDisabled(True)
		self.selected_category = ""


	def category_clicked(self):
		category = self.sender().property("name")

		if self.selected_category == "" or self.selected_category != category:
			self.selected_category = category
			self.rename_widget.setDisabled(False)
			self.remove_widget.setDisabled(False)
		elif self.selected_category == category:
			self.selected_category = ""
			self.rename_widget.setDisabled(True)
			self.remove_widget.setDisabled(True)


	def add_button_clicked(self):
		new_category_name = self.add_text.text()

		if database_interaction.category_exists(new_category_name):
			return

		database_interaction.add_category(new_category_name)

		button = self.list.create_button(new_category_name)
		button.clicked.connect(self.category_clicked)


	def rename_button_clicked(self):
		current_category_name = self.selected_category
		new_category_name = self.rename_text.text()

		if database_interaction.category_exists(new_category_name):
			return

		database_interaction.rename_category(current_category_name, new_category_name)

		self.list.rename_button(current_category_name, new_category_name)
		self.selected_category = new_category_name


	def remove_button_clicked(self):
		category_name = self.selected_category

		if not database_interaction.category_exists(category_name):
			return

		database_interaction.remove_category(category_name)
		self.list.delete_button(category_name)

		self.rename_widget.setDisabled(True)
		self.remove_widget.setDisabled(True)



window = Window()
mode_bar = ModeBar(window)
category_edit_widget = CategoryEditWidget(window)

window.base_layout.addWidget(mode_bar, 0, 0)
window.base_layout.addWidget(category_edit_widget, 1, 0)
window.show()

app.exec()