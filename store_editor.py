from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
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
		self.setWindowIcon(QIcon("resources/settings.png"))

		self.base_widget = QWidget(self)
		self.base_widget.setLayout(QGridLayout())
		self.base_widget.layout().setContentsMargins(0, 0, 0, 0)
		self.base_widget.layout().setRowStretch(1, 1)
		self.base_widget.layout().setColumnStretch(0, 1)
		self.setCentralWidget(self.base_widget)

		self.background_instruction = QLabel("^\nOdaberi način rada\n")
		self.background_instruction.setAlignment(Qt.AlignCenter)
		self.background_instruction.setStyleSheet("""
			QLabel {
				font: bold;
				font-size: 30pt;
				color: #3C3C3C;
			}
		""")
		self.base_widget.layout().addWidget(self.background_instruction, 1, 0)

		self.show()



class ModeBar(QWidget):
	def __init__(self, parent):
		super().__init__(parent)

		self.setStyleSheet("""
			QWidget {
				background-color: #141414;
			}
			QPushButton {
				font-size: 13pt;
				height: 30;
				background-color: #000000;
				border: 1px solid #878787;
				padding: 0px 10px;
			}

			QPushButton::checked {
				background-color: #141414;
				border-bottom: 0px;
			}
		""")

		self.selected_primary_key = ""
		self.selected_secondary_key = ""

		self.secondary_widgets = {
			"categories_properties": QWidget(self),
			"items": QWidget(self),
		}

		for widget in self.secondary_widgets.values():
			widget.setStyleSheet("""
				QPushButton {
					font-size: 13pt;
					height: 30;
					background-color: #141414;
					border: 1px solid #878787;
					margin: 10px 0 0 0;
				}

				QPushButton::checked {
					background-color: #1E1E1E;
					border-bottom: 0px;
				}
			""")


		self.primary_buttons = {
			"categories_properties": QPushButton("Kategorije/svojstva"),
			"items": QPushButton("Proizvodi"),
		}

		self.secondary_buttons = {
			"category_edit": QPushButton("Dodaj/uredi kategorije"),
			"property_edit": QPushButton("Dodaj/uredi grupe svojstava"),
			"descriptor_edit": QPushButton("Dodaj/uredi svojstva"),
			"item_add": QPushButton("Dodaj proizvod"),
			"item_edit": QPushButton("Uredi proizvod"),
			"item_delete": QPushButton("Izbriši proizvod"),
		}

		for primary_key in self.primary_buttons:
			self.primary_buttons[primary_key].setCheckable(True)
			self.primary_buttons[primary_key].setProperty("key", primary_key)
			self.primary_buttons[primary_key].clicked.connect(self.primary_button_clicked)

		for secondary_key in self.secondary_buttons:
			self.secondary_buttons[secondary_key].setCheckable(True)
			self.secondary_buttons[secondary_key].setProperty("key", secondary_key)
			self.secondary_buttons[secondary_key].clicked.connect(self.secondary_button_clicked)


		self.linked_widgets = {
			"category_edit": category_edit_widget,
			"property_edit": property_edit_widget,
			"descriptor_edit": descriptor_edit_widget,
		}


		self.setLayout(QGridLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().setSpacing(0)
		self.layout().addWidget(self.primary_buttons["categories_properties"], 0, 0)
		self.layout().addWidget(self.primary_buttons["items"], 0, 1)
		self.layout().addWidget(self.secondary_widgets["categories_properties"], 1, 0, 1, 2)
		self.layout().addWidget(self.secondary_widgets["items"], 1, 0, 1, 2)

		self.secondary_widgets["categories_properties"].setLayout(QGridLayout())
		self.secondary_widgets["categories_properties"].layout().setContentsMargins(0, 0, 0, 0)
		self.secondary_widgets["categories_properties"].layout().setSpacing(0)
		self.secondary_widgets["categories_properties"].layout().addWidget(
			self.secondary_buttons["category_edit"], 0, 0
		)
		self.secondary_widgets["categories_properties"].layout().addWidget(
			self.secondary_buttons["property_edit"], 0, 1
		)
		self.secondary_widgets["categories_properties"].layout().addWidget(
			self.secondary_buttons["descriptor_edit"], 0, 2
		)

		self.secondary_widgets["items"].setLayout(QGridLayout())
		self.secondary_widgets["items"].layout().setContentsMargins(0, 0, 0, 0)
		self.secondary_widgets["items"].layout().setSpacing(0)
		self.secondary_widgets["items"].layout().addWidget(
			self.secondary_buttons["item_add"], 0, 0
		)
		self.secondary_widgets["items"].layout().addWidget(
			self.secondary_buttons["item_edit"], 0, 1
		)
		self.secondary_widgets["items"].layout().addWidget(
			self.secondary_buttons["item_delete"], 0, 2
		)


		self.secondary_widgets["categories_properties"].hide()
		self.secondary_widgets["items"].hide()


	def primary_button_clicked(self):
		clicked_button_key = self.sender().property("key")

		if self.selected_primary_key == "":
			self.selected_primary_key = clicked_button_key
			self.secondary_widgets[clicked_button_key].show()

		elif clicked_button_key != self.selected_primary_key:
			self.secondary_widgets[self.selected_primary_key].hide()
			self.primary_buttons[self.selected_primary_key].setChecked(False)

			if self.selected_secondary_key:
				match self.selected_primary_key:
					case "categories_properties":
						self.linked_widgets[self.selected_secondary_key].close()
					case "items":
						item_edit_widget.close()

				self.secondary_buttons[self.selected_secondary_key].setChecked(False)
				self.selected_secondary_key = ""

			self.selected_primary_key = clicked_button_key
			self.secondary_widgets[clicked_button_key].show()

		elif clicked_button_key == self.selected_primary_key:
			self.secondary_widgets[self.selected_primary_key].hide()
			self.primary_buttons[self.selected_primary_key].setChecked(False)

			if self.selected_secondary_key:
				match self.selected_primary_key:
					case "categories_properties":
						self.linked_widgets[self.selected_secondary_key].close()
					case "items":
						item_edit_widget.close()

				self.secondary_buttons[self.selected_secondary_key].setChecked(False)
				self.selected_secondary_key = ""

			self.selected_primary_key = ""



	def secondary_button_clicked(self):
		clicked_button_key = self.sender().property("key")

		if self.selected_secondary_key == "":
			match clicked_button_key:
				case "category_edit" | "property_edit" | "descriptor_edit":
					self.linked_widgets[clicked_button_key].open()
				case "item_add":
					item_edit_widget.switch_to_item_add()
				case "item_edit":
					item_edit_widget.switch_to_item_edit()
				case "item_delete":
					item_edit_widget.switch_to_item_remove()
			self.selected_secondary_key = clicked_button_key
			window.background_instruction.hide()

		elif clicked_button_key != self.selected_secondary_key:
			self.secondary_buttons[self.selected_secondary_key].setChecked(False)
			match clicked_button_key:
				case "category_edit" | "property_edit" | "descriptor_edit":
					self.linked_widgets[self.selected_secondary_key].close()
					self.linked_widgets[clicked_button_key].open()
				case "item_add":
					item_edit_widget.switch_to_item_add()
				case "item_edit":
					item_edit_widget.switch_to_item_edit()
				case "item_delete":
					item_edit_widget.switch_to_item_remove()
			self.selected_secondary_key = clicked_button_key
			window.background_instruction.hide()

		elif clicked_button_key == self.selected_secondary_key:
			self.secondary_buttons[self.selected_secondary_key].setChecked(False)
			match clicked_button_key:
				case "category_edit" | "property_edit" | "descriptor_edit":
					self.linked_widgets[self.selected_secondary_key].close()
				case "item_add" | "item_edit" | "item_delete":
					item_edit_widget.close()
			self.selected_secondary_key = ""
			window.background_instruction.show()



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
			category_name = category["NAME"]
			button = self.list_widget.create_button(category_name)
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

		self.add_text.setText("")

		button = self.list_widget.create_button(new_category_name)
		button.clicked.connect(self.category_clicked)


	def rename_button_clicked(self):
		current_category_name = self.selected_category
		new_category_name = self.rename_text.text()

		if database_interaction.category_exists(new_category_name):
			return

		database_interaction.rename_category(current_category_name, new_category_name)

		self.rename_text.setText("")

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

		self.close()


	def open(self):
		self.show()

		for category in database_interaction.get_categories():
			category_name = category["NAME"]
			button = self.category_list_widget.create_button(category_name)
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
			property_name = property["NAME"]
			button = self.property_list_widget.create_button(property_name)
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

		self.add_text.setText("")

		button = self.property_list_widget.create_button(new_property_name)
		button.clicked.connect(self.property_clicked)


	def rename_button_clicked(self):
		current_property_name = self.selected_property
		new_property_name = self.rename_text.text()

		if database_interaction.property_exists(self.selected_category, new_property_name):
			return

		database_interaction.rename_property(self.selected_category, current_property_name, new_property_name)

		self.rename_text.setText("")

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



class DescriptorEditWidget(QWidget):
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


		self.descriptor_list_group = QGroupBox("Svojstva")
		self.descriptor_list_group.setLayout(QVBoxLayout())

		self.descriptor_list_widget = CustomScrollList(self.descriptor_list_group)
		self.descriptor_list_group.layout().addWidget(self.descriptor_list_widget)


		self.add_group = QGroupBox("Dodaj svojstvo")
		self.add_group.setLayout(QVBoxLayout())

		self.add_text = QLineEdit()
		self.add_text.setPlaceholderText("naziv svojstva")
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


		self.rename_group = QGroupBox("Preimenuj svojstvo")
		self.rename_group.setLayout(QVBoxLayout())

		self.rename_text = QLineEdit()
		self.rename_text.setPlaceholderText("novi naziv svojstva")
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


		self.remove_group = QGroupBox("Izbriši svojstvo")
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
		layout.setColumnStretch(0, 2)
		layout.setColumnStretch(1, 2)
		layout.setColumnStretch(2, 2)
		layout.setColumnStretch(3, 3)
		layout.addWidget(self.category_list_group, 0, 0, 3, 1)
		layout.addWidget(self.property_list_group, 0, 1, 3, 1)
		layout.addWidget(self.descriptor_list_group, 0, 2, 3, 1)
		layout.addWidget(self.add_group, 0, 3)
		layout.addWidget(self.rename_group, 1, 3)
		layout.addWidget(self.remove_group, 2, 3)
		self.setLayout(layout)

		self.selected_category = ""
		self.selected_property = ""
		self.selected_descriptor = ""

		self.close()


	def open(self):
		self.show()

		for category in database_interaction.get_categories():
			category_name = category["NAME"]
			button = self.category_list_widget.create_button(category_name)
			button.clicked.connect(self.category_clicked)


	def close(self):
		self.hide()

		self.category_list_widget.delete_all_buttons()
		self.property_list_widget.delete_all_buttons()
		self.descriptor_list_widget.delete_all_buttons()
		self.add_group.setDisabled(True)
		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)
		self.selected_category = ""
		self.selected_property = ""
		self.selected_descriptor = ""


	def category_clicked(self):
		category = self.sender().property("name")

		if self.selected_category == "" or self.selected_category != category:
			self.selected_category = category
		elif self.selected_category == category:
			self.selected_category = ""
			self.selected_property = ""
			self.selected_descriptor = ""

		self.add_group.setDisabled(True)
		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)

		self.property_list_widget.delete_all_buttons()
		self.descriptor_list_widget.delete_all_buttons()

		if self.selected_category == "":
			return

		for property in database_interaction.get_properties(self.selected_category):
			property_name = property["NAME"]
			button = self.property_list_widget.create_button(property_name)
			button.clicked.connect(self.property_clicked)


	def property_clicked(self):
		property = self.sender().property("name")

		if self.selected_property == "" or self.selected_property != property:
			self.selected_property = property
			self.add_group.setDisabled(False)
		elif self.selected_property == property:
			self.selected_property = ""
			self.add_group.setDisabled(True)

		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)

		self.descriptor_list_widget.delete_all_buttons()

		if self.selected_property == "":
			return

		for descriptor in database_interaction.get_descriptors(self.selected_category, property):
			descriptor_name = descriptor["NAME"]
			button = self.descriptor_list_widget.create_button(descriptor_name)
			button.clicked.connect(self.descriptor_clicked)


	def descriptor_clicked(self):
		descriptor = self.sender().property("name")

		if self.selected_descriptor == "" or self.selected_descriptor != descriptor:
			self.selected_descriptor = descriptor
			self.rename_group.setDisabled(False)
			self.remove_group.setDisabled(False)
		elif self.selected_descriptor == descriptor:
			self.selected_descriptor = ""
			self.rename_group.setDisabled(True)
			self.remove_group.setDisabled(True)


	def add_button_clicked(self):
		new_descriptor_name = self.add_text.text()

		if new_descriptor_name == "":
			return

		if self.selected_category == "" or self.selected_property == "":
			return

		if database_interaction.descriptor_exists(
			self.selected_category,
			self.selected_property,
			new_descriptor_name
		):
			return

		database_interaction.add_descriptor(
			self.selected_category,
			self.selected_property,
			new_descriptor_name
		)

		self.add_text.setText("")

		button = self.descriptor_list_widget.create_button(new_descriptor_name)
		button.clicked.connect(self.descriptor_clicked)


	def rename_button_clicked(self):
		current_descriptor_name = self.selected_descriptor
		new_descriptor_name = self.rename_text.text()

		if database_interaction.descriptor_exists(
			self.selected_category,
			self.selected_property,
			new_descriptor_name
		):
			return

		database_interaction.rename_descriptor(
			self.selected_category,
			self.selected_property,
			current_descriptor_name,
			new_descriptor_name
		)

		self.rename_text.setText("")

		self.descriptor_list_widget.rename_button(current_descriptor_name, new_descriptor_name)
		self.selected_descriptor = new_descriptor_name


	def remove_button_clicked(self):
		descriptor_name = self.selected_descriptor

		if not database_interaction.descriptor_exists(
			self.selected_category,
			self.selected_property,
			descriptor_name
		):
			return

		database_interaction.remove_descriptor(
			self.selected_category,
			self.selected_property,
			descriptor_name
		)
		self.descriptor_list_widget.delete_button(descriptor_name)

		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)



class ItemEditWidget(QWidget):
	def __init__(self, parent):
		super().__init__(parent)

		self.setStyleSheet(
			"""
			QPushButton {
				font-size: 13pt;
				height: 30;
			}
			"""
		)

		self.list_group = QGroupBox("Proizvodi")
		self.list_group.setLayout(QVBoxLayout())

		self.list_widget = CustomScrollList(self.list_group)
		self.list_group.layout().addWidget(self.list_widget)


		self.info_group = QGroupBox("Informacije o proizvodu")
		self.info_group.setLayout(QGridLayout())
		self.info_group.layout().setColumnStretch(2, 2)
		self.info_group.layout().setColumnStretch(4, 2)
		self.spacerH1 = QWidget()
		self.spacerH1.setFixedWidth(10)
		self.spacerH2 = QWidget()
		self.spacerH2.setFixedWidth(10)
		self.info_group.layout().addWidget(self.spacerH1, 0, 1)
		self.info_group.layout().addWidget(self.spacerH2, 0, 3)

		self.image_display = QLabel()
		self.image_display.setStyleSheet(
			"""
			QLabel {
				border: 1px solid black;
			}
			"""
		)
		self.image_display.setFixedSize(100, 100)
		self.image_display.setScaledContents(True)
		pixmap = QPixmap("resources/item_images/no_image.png")
		self.image_display.setPixmap(pixmap)
		self.info_group.layout().addWidget(self.image_display, 0, 0, 4, 1)
		self.image_button = QPushButton("Učitaj sliku")
		self.image_button.setStyleSheet(
			"""
			QPushButton {
				font-size: 9pt;
				height: 18;
			}
			"""
		)
		self.info_group.layout().addWidget(self.image_button, 4, 0)

		self.item_category_label = QLabel("Kategorija")
		self.info_group.layout().addWidget(self.item_category_label, 0, 4)
		self.item_category_edit = QComboBox()
		self.info_group.layout().addWidget(self.item_category_edit, 1, 4)

		self.item_property_label = QLabel("Svojstva")
		self.info_group.layout().addWidget(self.item_property_label, 2, 4)
		self.item_property_edit = QWidget()
		self.info_group.layout().addWidget(self.item_property_edit, 3, 4)

		self.item_name_label = QLabel("Naziv")
		self.info_group.layout().addWidget(self.item_name_label, 0, 2)
		self.item_name_edit = QPlainTextEdit()
		self.info_group.layout().addWidget(self.item_name_edit, 1, 2, 3, 1)

		self.item_description_label = QLabel("Opis")
		self.info_group.layout().addWidget(self.item_description_label, 5, 0, 1, 3)
		self.item_description_edit = QPlainTextEdit()
		self.info_group.layout().addWidget(self.item_description_edit, 6, 0, 1, 3)


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
		self.info_group.layout().addWidget(self.add_button, 7, 4)

		self.edit_button = QPushButton("Primijeni izmjene")
		self.edit_button.setStyleSheet(
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
		self.edit_button.clicked.connect(self.edit_button_clicked)
		self.info_group.layout().addWidget(self.edit_button, 7, 4)

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
		self.info_group.layout().addWidget(self.remove_button, 7, 4)





		layout = QGridLayout()
		layout.setColumnStretch(0, 2)
		layout.setColumnStretch(1, 5)
		layout.addWidget(self.list_group, 0, 0)
		layout.addWidget(self.info_group, 0, 1)
		self.setLayout(layout)

		self.close()


	def close(self):
		self.hide()


	def switch_to_item_add(self):
		self.show()

		self.edit_button.hide()
		self.remove_button.hide()
		self.add_button.show()

		self.image_display.setDisabled(False)
		self.image_button.setDisabled(False)
		self.item_name_label.setDisabled(False)
		self.item_name_edit.setDisabled(False)
		self.item_description_label.setDisabled(False)
		self.item_description_edit.setDisabled(False)
		self.item_category_label.setDisabled(False)
		self.item_category_edit.setDisabled(False)

		self.info_group.setTitle("Dodaj proizvod")
		self.item_name_edit.setPlaceholderText("naziv novog proizvoda")


	def switch_to_item_edit(self):
		self.show()

		self.add_button.hide()
		self.remove_button.hide()
		self.edit_button.show()

		self.image_display.setDisabled(False)
		self.image_button.setDisabled(False)
		self.item_name_label.setDisabled(False)
		self.item_name_edit.setDisabled(False)
		self.item_description_label.setDisabled(False)
		self.item_description_edit.setDisabled(False)
		self.item_category_label.setDisabled(False)
		self.item_category_edit.setDisabled(False)

		self.info_group.setTitle("Izmijeni detalje proizvoda")
		self.item_name_edit.setPlaceholderText("novi naziv proizvoda")


	def switch_to_item_remove(self):
		self.show()

		self.edit_button.hide()
		self.add_button.hide()
		self.remove_button.show()

		self.image_display.setDisabled(True)
		self.image_button.setDisabled(True)
		self.item_name_label.setDisabled(True)
		self.item_name_edit.setDisabled(True)
		self.item_description_label.setDisabled(True)
		self.item_description_edit.setDisabled(True)
		self.item_category_label.setDisabled(True)
		self.item_category_edit.setDisabled(True)

		self.info_group.setTitle("Izbriši proizvod")


	def add_button_clicked(self):
		pass


	def edit_button_clicked(self):
		pass


	def remove_button_clicked(self):
		pass




window = Window()
category_edit_widget = CategoryEditWidget(window)
property_edit_widget = PropertyEditWidget(window)
descriptor_edit_widget = DescriptorEditWidget(window)
item_edit_widget = ItemEditWidget(window)
mode_bar = ModeBar(window)

window.base_widget.layout().addWidget(mode_bar, 0, 0)
window.base_widget.layout().addWidget(category_edit_widget, 1, 0)
window.base_widget.layout().addWidget(property_edit_widget, 1, 0)
window.base_widget.layout().addWidget(descriptor_edit_widget, 1, 0)
window.base_widget.layout().addWidget(item_edit_widget, 1, 0)

app.exec()