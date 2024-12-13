from PySide6.QtWidgets import *
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
		border: 1px solid #353535;
		border-radius: 6px;
		margin-top: 6px;
	}

	QGroupBox::disabled {
		border: 1px solid #262626;
	}

	QGroupBox::title {
		subcontrol-origin: margin;
		left: 7px;
		padding: 0px 5px 0px 5px;
	}

	QGroupBox::title::disabled {
		color: #494949;
	}

	QLineEdit {
		font-size: 11pt;
	}

	QLineEdit::disabled {
		color: #494949;
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
		self.base_widget.setLayout(QVBoxLayout())
		self.base_widget.layout().setContentsMargins(0, 0, 0, 0)
		self.base_widget.layout().setSpacing(0)
		self.base_widget.layout().setSizeConstraint(QLayout.SetMaximumSize)
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
		self.base_widget.layout().addWidget(button)
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
		self.base_widget.layout().removeWidget(button)
		button.deleteLater()


	def delete_all_buttons(self):
		while len(self.buttons) > 0:
			button = list(self.buttons)[0]
			self.delete_button(button)





class Window(QMainWindow):

	def __init__(self):
		super().__init__()
		self.setMinimumSize(794, 400)
		self.setWindowTitle("Uređivač proizvoda/svojstava")

		self.base_widget = QWidget(self)
		self.base_widget.setLayout(QGridLayout())
		self.base_widget.layout().setContentsMargins(0, 0, 0, 0)
		self.base_widget.layout().setRowStretch(1, 1)
		self.base_widget.layout().setColumnStretch(0, 1)
		self.setCentralWidget(self.base_widget)

		self.show()



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

		self.selected_key = ""

		self.buttons = {
			"category_edit": QPushButton("Dodaj/uredi kategorije"),
			"property_edit": QPushButton("Dodaj/uredi grupe svojstava"),
			"descriptor_edit": QPushButton("Dodaj/uredi svojstva"),
			"item_edit": QPushButton("Dodaj/uredi proizvode"),
		}

		for key in self.buttons:
			self.buttons[key].setCheckable(True)
			self.buttons[key].setProperty("key", key)
			self.buttons[key].clicked.connect(self.button_clicked)

		self.linked_widgets = {
			"category_edit": category_edit_widget,
			"property_edit": property_edit_widget,
			"descriptor_edit": descriptor_edit_widget,
			"item_edit": item_edit_widget,
		}


		self.setLayout(QGridLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().setSpacing(0)
		self.layout().addWidget(self.buttons["category_edit"], 0, 0)
		self.layout().addWidget(self.buttons["property_edit"], 0, 1)
		self.layout().addWidget(self.buttons["descriptor_edit"], 0, 2)
		self.layout().addWidget(self.buttons["item_edit"], 0, 3)


	def button_clicked(self):
		clicked_button_key = self.sender().property("key")

		if self.selected_key == "":
			self.selected_key = clicked_button_key
			self.linked_widgets[clicked_button_key].open()

		elif clicked_button_key == self.selected_key:
			self.linked_widgets[self.selected_key].close()
			self.selected_key = ""

		elif clicked_button_key != self.selected_key:
			self.linked_widgets[self.selected_key].close()
			self.buttons[self.selected_key].setChecked(False)
			self.linked_widgets[clicked_button_key].open()
			self.selected_key = clicked_button_key



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


		self.list_group = QGroupBox("Kategorije")
		self.list_group.setLayout(QVBoxLayout())

		self.list_widget = CustomScrollList(self.list_group)
		self.list_group.layout().addWidget(self.list_widget)


		self.add_group = QGroupBox("Dodaj kategoriju")
		self.add_group.setLayout(QVBoxLayout())

		self.add_text = QLineEdit()
		self.add_text.setPlaceholderText("naziv nove kategorije")
		self.add_group.layout().addWidget(self.add_text)

		self.add_button = QPushButton("Dodaj")
		self.add_button.setStyleSheet(
			"""
			QPushButton {
				background-color: #008900;
			}
			"""
		)
		self.add_button.clicked.connect(self.add_button_clicked)
		self.add_group.layout().addWidget(self.add_button)


		self.rename_group = QGroupBox("Preimenuj kategoriju")
		self.rename_group.setLayout(QVBoxLayout())

		self.rename_text = QLineEdit()
		self.rename_text.setPlaceholderText("novi naziv kategorije")
		self.rename_group.layout().addWidget(self.rename_text)

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
		self.rename_group.layout().addWidget(self.rename_button)


		self.remove_group = QGroupBox("Izbriši kategoriju")
		self.remove_group.setLayout(QVBoxLayout())

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
		self.remove_group.layout().addWidget(self.remove_button)


		layout = QGridLayout(self)
		layout.setRowStretch(0, 2)
		layout.setRowStretch(1, 2)
		layout.setRowStretch(2, 1)
		layout.setColumnStretch(0, 1)
		layout.setColumnStretch(1, 1)
		layout.addWidget(self.list_group, 0, 0, 3, 1)
		layout.addWidget(self.add_group, 0, 1)
		layout.addWidget(self.rename_group, 1, 1)
		layout.addWidget(self.remove_group, 2, 1)
		self.setLayout(layout)

		self.selected_category = ""

		self.close()


	def open(self):
		self.show()

		for category in database_interaction.get_categories():
			button = self.list_widget.create_button(category)
			button.clicked.connect(self.category_clicked)


	def close(self):
		self.hide()

		self.list_widget.delete_all_buttons()
		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)
		self.selected_category = ""


	def category_clicked(self):
		category = self.sender().property("name")

		if self.selected_category == "" or self.selected_category != category:
			self.selected_category = category
			self.rename_group.setDisabled(False)
			self.remove_group.setDisabled(False)
		elif self.selected_category == category:
			self.selected_category = ""
			self.rename_group.setDisabled(True)
			self.remove_group.setDisabled(True)


	def add_button_clicked(self):
		new_category_name = self.add_text.text()

		if new_category_name == "":
			return

		if database_interaction.category_exists(new_category_name):
			return

		database_interaction.add_category(new_category_name)

		button = self.list_widget.create_button(new_category_name)
		button.clicked.connect(self.category_clicked)


	def rename_button_clicked(self):
		current_category_name = self.selected_category
		new_category_name = self.rename_text.text()

		if database_interaction.category_exists(new_category_name):
			return

		database_interaction.rename_category(current_category_name, new_category_name)

		self.list_widget.rename_button(current_category_name, new_category_name)
		self.selected_category = new_category_name


	def remove_button_clicked(self):
		category_name = self.selected_category

		if not database_interaction.category_exists(category_name):
			return

		database_interaction.remove_category(category_name)
		self.list_widget.delete_button(category_name)

		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)




class PropertyEditWidget(QWidget):
	def __init__(self, parent):
		super().__init__(parent)

		self.setStyleSheet(
			"""
			QPushButton {
				font-size: 13pt;
				height: 30;
				margin-left: 70;
			}
			"""
		)


		self.category_list_group = QGroupBox("Kategorije")
		self.category_list_group.setLayout(QVBoxLayout())

		self.category_list_widget = CustomScrollList(self.category_list_group)
		self.category_list_group.layout().addWidget(self.category_list_widget)


		self.property_list_group = QGroupBox("Grupe svojstava")
		self.property_list_group.setLayout(QVBoxLayout())

		self.property_list_widget = CustomScrollList(self.property_list_group)
		self.property_list_group.layout().addWidget(self.property_list_widget)


		self.add_group = QGroupBox("Dodaj grupu svojstava")
		self.add_group.setLayout(QVBoxLayout())

		self.add_text = QLineEdit()
		self.add_text.setPlaceholderText("naziv grupe svojstava")
		self.add_group.layout().addWidget(self.add_text)

		self.add_button = QPushButton("Dodaj")
		self.add_button.setStyleSheet(
			"""
			QPushButton {
				background-color: #008900;
			}

			QPushButton::disabled {
				background-color: #005600;
				color: #2D4F2D;
			}
			"""
		)
		self.add_button.clicked.connect(self.add_button_clicked)
		self.add_group.layout().addWidget(self.add_button)


		self.rename_group = QGroupBox("Preimenuj grupu svojstava")
		self.rename_group.setLayout(QVBoxLayout())

		self.rename_text = QLineEdit()
		self.rename_text.setPlaceholderText("novi naziv grupe svojstava")
		self.rename_group.layout().addWidget(self.rename_text)

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
		self.rename_group.layout().addWidget(self.rename_button)


		self.remove_group = QGroupBox("Izbriši grupu svojstava")
		self.remove_group.setLayout(QVBoxLayout())

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
		self.remove_group.layout().addWidget(self.remove_button)


		layout = QGridLayout(self)
		layout.setRowStretch(0, 2)
		layout.setRowStretch(1, 2)
		layout.setRowStretch(2, 1)
		layout.setColumnStretch(0, 1)
		layout.setColumnStretch(1, 1)
		layout.setColumnStretch(2, 1)
		layout.addWidget(self.category_list_group, 0, 0, 3, 1)
		layout.addWidget(self.property_list_group, 0, 1, 3, 1)
		layout.addWidget(self.add_group, 0, 2)
		layout.addWidget(self.rename_group, 1, 2)
		layout.addWidget(self.remove_group, 2, 2)
		self.setLayout(layout)

		self.selected_category = ""
		self.selected_property = ""

		self.hide()


	def open(self):
		self.show()

		for category in database_interaction.get_categories():
			button = self.category_list_widget.create_button(category)
			button.clicked.connect(self.category_clicked)


	def close(self):
		self.hide()

		self.category_list_widget.delete_all_buttons()
		self.property_list_widget.delete_all_buttons()
		self.add_group.setDisabled(True)
		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)
		self.selected_category = ""
		self.selected_property = ""


	def category_clicked(self):
		category = self.sender().property("name")

		if self.selected_category == "" or self.selected_category != category:
			self.selected_category = category
			self.add_group.setDisabled(False)
		elif self.selected_category == category:
			self.selected_category = ""
			self.selected_property = ""
			self.add_group.setDisabled(True)

		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)

		self.property_list_widget.delete_all_buttons()

		if self.selected_category == "":
			return

		for property in database_interaction.get_properties(self.selected_category):
			button = self.property_list_widget.create_button(property)
			button.clicked.connect(self.property_clicked)


	def property_clicked(self):
		property = self.sender().property("name")

		if self.selected_property == "" or self.selected_property != property:
			self.selected_property = property
			self.rename_group.setDisabled(False)
			self.remove_group.setDisabled(False)
		elif self.selected_property == property:
			self.selected_property = ""
			self.rename_group.setDisabled(True)
			self.remove_group.setDisabled(True)


	def add_button_clicked(self):
		new_property_name = self.add_text.text()

		if new_property_name == "":
			return

		if self.selected_category == "":
			return

		if database_interaction.property_exists(self.selected_category, new_property_name):
			return

		database_interaction.add_property(self.selected_category, new_property_name)

		button = self.property_list_widget.create_button(new_property_name)
		button.clicked.connect(self.property_clicked)


	def rename_button_clicked(self):
		current_property_name = self.selected_property
		new_property_name = self.rename_text.text()

		if database_interaction.property_exists(self.selected_category, new_property_name):
			return

		database_interaction.rename_property(self.selected_category, current_property_name, new_property_name)

		self.property_list_widget.rename_button(current_property_name, new_property_name)
		self.selected_property = new_property_name


	def remove_button_clicked(self):
		property_name = self.selected_property

		if not database_interaction.property_exists(self.selected_category, property_name):
			return

		database_interaction.remove_property(self.selected_category, property_name)
		self.property_list_widget.delete_button(property_name)

		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)





window = Window()
category_edit_widget = CategoryEditWidget(window)
property_edit_widget = PropertyEditWidget(window)
descriptor_edit_widget = PropertyEditWidget(window)
item_edit_widget = PropertyEditWidget(window)
mode_bar = ModeBar(window)

window.base_widget.layout().addWidget(mode_bar, 0, 0)
window.base_widget.layout().addWidget(category_edit_widget, 1, 0)
window.base_widget.layout().addWidget(property_edit_widget, 1, 0)
window.base_widget.layout().addWidget(descriptor_edit_widget, 1, 0)
window.base_widget.layout().addWidget(item_edit_widget, 1, 0)

app.exec()