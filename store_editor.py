from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
import os
import database_interaction
from helper_classes import *


# # Resetiranje baze podataka
# if os.path.exists("database.db"):
# 	os.remove("database.db")

# Ako ne postoji baza podataka, napravi novu s nekim pocetnim podatcima
if not os.path.exists("database.db"):
	database_interaction.initialize()



app = QApplication(sys.argv)
app.setStyle("Fusion")
app.setStyleSheet(
	"""
	QGroupBox {
		font: bold;
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


# Scrollable widget koji sadrzi buttone koje je moguce izabrati
# (u bilo kojem trenutku samo jedan button moze biti izabran)
class RadioButtonScrollList(QScrollArea):
	def __init__(self):
		super().__init__()

		self.setStyleSheet("""
			QPushButton {
				padding: 0px 10px;
				font-size: 10pt;
				text-align: left;
				margin-left: 0;
			}
		""")

		self.base_widget = QWidget(self)
		self.base_widget.setLayout(QVBoxLayout())
		self.base_widget.layout().setContentsMargins(0, 0, 0, 0)
		self.base_widget.layout().setSpacing(0)
		self.base_widget.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
		self.setWidget(self.base_widget)
		self.setWidgetResizable(True)

		self.buttons = {}


	def _on_button_clicked(self):
		clicked_button_id = self.sender().property("ID")
		for button_id in self.buttons:
			if button_id != clicked_button_id:
				self.buttons[button_id].setChecked(False)


	def create_button(self, id, text):
		text = text.lower()

		button = QPushButton(text.capitalize())
		button.setCheckable(True)
		button.setProperty("ID", id)
		button.clicked.connect(self._on_button_clicked)
		self.base_widget.layout().addWidget(button)

		self.buttons[id] = button

		return button


	def rename_button(self, id, new_text):
		self.buttons[id].setText(new_text.capitalize())


	def delete_button(self, id):
		button = self.buttons.pop(id)
		button.clicked.disconnect()
		self.base_widget.layout().removeWidget(button)
		button.deleteLater()


	def delete_all_buttons(self):
		while len(self.buttons) > 0:
			button = list(self.buttons)[0]
			self.delete_button(button)


	def unselect_all_buttons(self):
		for id in self.buttons:
			self.buttons[id].setChecked(False)








class Window(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setMinimumSize(850, 500)
		self.setWindowTitle("Uređivač trgovine")
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
			}
		""")
		self.base_widget.layout().addWidget(self.background_instruction, 1, 0)

		self.show()


# Widget za odabir nacina rada (uredivanje svojstava/kategorija ili uredivanje proizvoda,
# te njihovi podnacini rada)
class ModeBar(QWidget):
	def __init__(self, parent):
		super().__init__(parent)

		self.setStyleSheet("""
			QPushButton {
				font-size: 13pt;
				height: 30;
				border: 1px solid;
				padding: 0px 10px;
			}

			QPushButton::checked {
				border-bottom: 0px;
			}
		""")

		self.selected_mode = ""
		self.selected_submode = ""

		# Buttoni za nacine rada
		self.mode_buttons = {
			"categories_properties": QPushButton("Kategorije/svojstva"),
			"items": QPushButton("Proizvodi"),
		}

		# Buttoni za podnacine rada
		self.submode_buttons = {
			"category_edit": QPushButton("Uredi kategorije"),
			"property_edit": QPushButton("Uredi grupe svojstava"),
			"descriptor_edit": QPushButton("Uredi svojstva"),
			"item_add": QPushButton("Dodaj proizvod"),
			"item_edit": QPushButton("Uredi proizvod"),
			"item_delete": QPushButton("Izbriši proizvod"),
		}

		# Widgeti koji sadrze buttone za podnacine rada
		self.submode_buttons_containers = {
			"categories_properties": QWidget(self),
			"items": QWidget(self),
		}

		for widget in self.submode_buttons_containers.values():
			widget.setStyleSheet("""
				QPushButton {
					font-size: 13pt;
					height: 30;
					border: 1px solid;
					margin: 10px 0 0 0;
				}

				QPushButton::checked {
					border-bottom: 0px;
				}
			""")


		# Inicializacija i povezivanje buttona sa "onclick" metodama
		for mode in self.mode_buttons:
			self.mode_buttons[mode].setCheckable(True)
			self.mode_buttons[mode].setProperty("name", mode)
			self.mode_buttons[mode].clicked.connect(self._on_mode_button_clicked)

		for submode in self.submode_buttons:
			self.submode_buttons[submode].setCheckable(True)
			self.submode_buttons[submode].setProperty("name", submode)
			self.submode_buttons[submode].clicked.connect(self._on_submode_button_clicked)


		self.linked_widgets = {
			"category_edit": category_edit_widget,
			"property_edit": property_edit_widget,
			"descriptor_edit": descriptor_edit_widget,
		}


		self.setLayout(QGridLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().setSpacing(0)
		self.layout().addWidget(self.mode_buttons["categories_properties"], 0, 0)
		self.layout().addWidget(self.mode_buttons["items"], 0, 1)
		self.layout().addWidget(self.submode_buttons_containers["categories_properties"], 1, 0, 1, 2)
		self.layout().addWidget(self.submode_buttons_containers["items"], 1, 0, 1, 2)

		self.submode_buttons_containers["categories_properties"].setLayout(QGridLayout())
		self.submode_buttons_containers["categories_properties"].layout().setContentsMargins(0, 0, 0, 0)
		self.submode_buttons_containers["categories_properties"].layout().setSpacing(0)
		self.submode_buttons_containers["categories_properties"].layout().addWidget(
			self.submode_buttons["category_edit"], 0, 0
		)
		self.submode_buttons_containers["categories_properties"].layout().addWidget(
			self.submode_buttons["property_edit"], 0, 1
		)
		self.submode_buttons_containers["categories_properties"].layout().addWidget(
			self.submode_buttons["descriptor_edit"], 0, 2
		)

		self.submode_buttons_containers["items"].setLayout(QGridLayout())
		self.submode_buttons_containers["items"].layout().setContentsMargins(0, 0, 0, 0)
		self.submode_buttons_containers["items"].layout().setSpacing(0)
		self.submode_buttons_containers["items"].layout().addWidget(
			self.submode_buttons["item_add"], 0, 0
		)
		self.submode_buttons_containers["items"].layout().addWidget(
			self.submode_buttons["item_edit"], 0, 1
		)
		self.submode_buttons_containers["items"].layout().addWidget(
			self.submode_buttons["item_delete"], 0, 2
		)


		self.submode_buttons_containers["categories_properties"].hide()
		self.submode_buttons_containers["items"].hide()


	def _on_mode_button_clicked(self):
		clicked_button_name = self.sender().property("name")

		if self.selected_mode == "":
			self.selected_mode = clicked_button_name
			self.submode_buttons_containers[clicked_button_name].show()

		elif clicked_button_name != self.selected_mode:
			self.submode_buttons_containers[self.selected_mode].hide()
			self.mode_buttons[self.selected_mode].setChecked(False)

			if self.selected_submode:
				match self.selected_mode:
					case "categories_properties":
						self.linked_widgets[self.selected_submode].close()
					case "items":
						item_edit_widget.close()

				self.submode_buttons[self.selected_submode].setChecked(False)
				self.selected_submode = ""

			self.selected_mode = clicked_button_name
			self.submode_buttons_containers[clicked_button_name].show()

		elif clicked_button_name == self.selected_mode:
			self.submode_buttons_containers[self.selected_mode].hide()
			self.mode_buttons[self.selected_mode].setChecked(False)

			if self.selected_submode:
				match self.selected_mode:
					case "categories_properties":
						self.linked_widgets[self.selected_submode].close()
					case "items":
						item_edit_widget.close()

				self.submode_buttons[self.selected_submode].setChecked(False)
				self.selected_submode = ""

			self.selected_mode = ""



	def _on_submode_button_clicked(self):
		clicked_button_name = self.sender().property("name")

		if self.selected_submode == "":
			match clicked_button_name:
				case "category_edit" | "property_edit" | "descriptor_edit":
					self.linked_widgets[clicked_button_name].open()
				case "item_add":
					item_edit_widget.switch_to_item_add()
				case "item_edit":
					item_edit_widget.switch_to_item_edit()
				case "item_delete":
					item_edit_widget.switch_to_item_remove()
			self.selected_submode = clicked_button_name
			window.background_instruction.hide()

		elif clicked_button_name != self.selected_submode:
			self.submode_buttons[self.selected_submode].setChecked(False)
			match clicked_button_name:
				case "category_edit" | "property_edit" | "descriptor_edit":
					self.linked_widgets[self.selected_submode].close()
					self.linked_widgets[clicked_button_name].open()
				case "item_add":
					item_edit_widget.switch_to_item_add()
				case "item_edit":
					item_edit_widget.switch_to_item_edit()
				case "item_delete":
					item_edit_widget.switch_to_item_remove()
			self.selected_submode = clicked_button_name
			window.background_instruction.hide()

		elif clicked_button_name == self.selected_submode:
			self.submode_buttons[self.selected_submode].setChecked(False)
			match clicked_button_name:
				case "category_edit" | "property_edit" | "descriptor_edit":
					self.linked_widgets[self.selected_submode].close()
				case "item_add" | "item_edit" | "item_delete":
					item_edit_widget.close()
			self.selected_submode = ""
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

		layout = QGridLayout(self)
		layout.setRowStretch(0, 2)
		layout.setRowStretch(1, 2)
		layout.setRowStretch(2, 1)
		layout.setColumnStretch(0, 1)
		layout.setColumnStretch(1, 1)
		self.setLayout(layout)


		# Widget koji sadrzi skup elemenata koji prikazuju listu kategorija
		self.list_group = QGroupBox("Kategorije")
		self.list_group.setLayout(QVBoxLayout())

		self.list_widget = RadioButtonScrollList()
		self.list_group.layout().addWidget(self.list_widget)

		layout.addWidget(self.list_group, 0, 0, 3, 1)


		# Widget koji sadrzi skup elemenata za dodavanje kategorija
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
				color: #FFFFFF;
			}
			"""
		)
		self.add_button.clicked.connect(self._on_add_button_clicked)
		self.add_group.layout().addWidget(self.add_button)

		layout.addWidget(self.add_group, 0, 1)


		# Widget koji sadrzi skup elemenata za preimenovanje kategorija
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
				color: #FFFFFF;
			}

			QPushButton::disabled {
				background-color: #474747;
				color: #727272;
			}
			"""
		)
		self.rename_button.clicked.connect(self._on_rename_button_clicked)
		self.rename_group.layout().addWidget(self.rename_button)

		layout.addWidget(self.rename_group, 1, 1)


		# Widget koji sadrzi skup elemenata za brisanje kategorija
		self.remove_group = QGroupBox("Izbriši kategoriju")
		self.remove_group.setLayout(QVBoxLayout())

		self.remove_button = QPushButton("Izbriši")
		self.remove_button.setStyleSheet(
			"""
			QPushButton {
				background-color: #890000;
				color: #FFFFFF;
			}

			QPushButton::disabled {
				background-color: #560000;
				color: #895959;
			}
			"""
		)
		self.remove_button.clicked.connect(self._on_remove_button_clicked)
		self.remove_group.layout().addWidget(self.remove_button)

		layout.addWidget(self.remove_group, 2, 1)


		self.selected_category = -1
		self.close()


	def open(self):
		self.show()

		# Popuni listu kategorija sa kategorijama iz baze podataka
		for category in database_interaction.get_categories():
			button = self.list_widget.create_button(category["ID"], category["NAME"])
			button.clicked.connect(self._on_category_clicked)


	def close(self):
		self.hide()

		self.list_widget.delete_all_buttons()
		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)
		self.selected_category = -1


	def _on_category_clicked(self):
		category_id = self.sender().property("ID")

		if self.selected_category == -1 or self.selected_category != category_id:
			self.selected_category = category_id
			self.rename_group.setDisabled(False)
			self.remove_group.setDisabled(False)
		elif self.selected_category == category_id:
			self.selected_category = -1
			self.rename_group.setDisabled(True)
			self.remove_group.setDisabled(True)


	def _on_add_button_clicked(self):
		new_category_name = self.add_text.text()

		if new_category_name == "":
			return

		if database_interaction.category_exists(new_category_name):
			return

		new_category_id = database_interaction.add_category(new_category_name)

		self.add_text.setText("")

		button = self.list_widget.create_button(new_category_id, new_category_name)
		button.clicked.connect(self._on_category_clicked)


	def _on_rename_button_clicked(self):
		category_id = self.selected_category
		category_name = database_interaction.get_category_name(category_id).lower()
		new_category_name = self.rename_text.text()

		# Odbaci pokusaj preimenovanje kategorije proizvoda "Ostalo"
		if category_name == "ostalo":
			return

		# Odbaci pokusaj preimenovanje kategorije ako novo ime vec postoji
		if database_interaction.category_exists(new_category_name):
			return

		database_interaction.rename_category(category_id, new_category_name)

		self.rename_text.setText("")
		self.list_widget.rename_button(category_id, new_category_name)


	def _on_remove_button_clicked(self):
		category_id = self.selected_category
		category_name = database_interaction.get_category_name(category_id).lower()

		# Odbaci pokusaj brisanja kategorije proizvoda "Ostalo"
		if category_name == "ostalo":
			return

		database_interaction.remove_category(category_id)
		self.list_widget.delete_button(category_id)

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

		layout = QGridLayout(self)
		layout.setRowStretch(0, 2)
		layout.setRowStretch(1, 2)
		layout.setRowStretch(2, 1)
		layout.setColumnStretch(0, 1)
		layout.setColumnStretch(1, 1)
		layout.setColumnStretch(2, 1)
		self.setLayout(layout)


		# Widget koji sadrzi skup elemenata koji prikazuju listu kategorija
		self.category_list_group = QGroupBox("Kategorije")
		self.category_list_group.setLayout(QVBoxLayout())

		self.category_list_widget = RadioButtonScrollList()
		self.category_list_group.layout().addWidget(self.category_list_widget)

		layout.addWidget(self.category_list_group, 0, 0, 3, 1)


		# Widget koji sadrzi skup elemenata koji prikazuju listu grupa svojstava
		self.property_list_group = QGroupBox("Grupe svojstava")
		self.property_list_group.setLayout(QVBoxLayout())

		self.property_list_widget = RadioButtonScrollList()
		self.property_list_group.layout().addWidget(self.property_list_widget)

		layout.addWidget(self.property_list_group, 0, 1, 3, 1)


		# Widget koji sadrzi skup elemenata za dodavanje grupa svojstava
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
				color: #FFFFFF;
			}

			QPushButton::disabled {
				background-color: #005600;
				color: #2D4F2D;
			}
			"""
		)
		self.add_button.clicked.connect(self._on_add_button_clicked)
		self.add_group.layout().addWidget(self.add_button)

		layout.addWidget(self.add_group, 0, 2)


		# Widget koji sadrzi skup elemenata za preimenovanje grupa svojstava
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
				color: #FFFFFF;
			}

			QPushButton::disabled {
				background-color: #474747;
				color: #727272;
			}
			"""
		)
		self.rename_button.clicked.connect(self._on_rename_button_clicked)
		self.rename_group.layout().addWidget(self.rename_button)

		layout.addWidget(self.rename_group, 1, 2)


		# Widget koji sadrzi skup elemenata za brisanje grupa svojstava
		self.remove_group = QGroupBox("Izbriši grupu svojstava")
		self.remove_group.setLayout(QVBoxLayout())

		self.remove_button = QPushButton("Izbriši")
		self.remove_button.setStyleSheet(
			"""
			QPushButton {
				background-color: #890000;
				color: #FFFFFF;
			}

			QPushButton::disabled {
				background-color: #560000;
				color: #895959;
			}
			"""
		)
		self.remove_button.clicked.connect(self._on_remove_button_clicked)
		self.remove_group.layout().addWidget(self.remove_button)

		layout.addWidget(self.remove_group, 2, 2)


		self.selected_category = -1
		self.selected_property = -1
		self.close()


	def open(self):
		self.show()

		# Popuni listu kategorija sa kategorijama iz baze podataka
		for category in database_interaction.get_categories():
			button = self.category_list_widget.create_button(category["ID"], category["NAME"])
			button.clicked.connect(self._on_category_clicked)


	def close(self):
		self.hide()

		self.category_list_widget.delete_all_buttons()
		self.property_list_widget.delete_all_buttons()
		self.add_group.setDisabled(True)
		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)
		self.selected_category = -1
		self.selected_property = -1


	def _on_category_clicked(self):
		clicked_category = self.sender().property("ID")

		if self.selected_category == -1 or self.selected_category != clicked_category:
			self.selected_category = clicked_category
			self.add_group.setDisabled(False)
		elif self.selected_category == clicked_category:
			self.selected_category = -1
			self.selected_property = -1
			self.add_group.setDisabled(True)

		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)

		self.property_list_widget.delete_all_buttons()

		if self.selected_category == -1:
			return

		# Popuni listu grupa svojstava sa grupama svojstava iz baze podataka
		for property in database_interaction.get_properties(self.selected_category):
			button = self.property_list_widget.create_button(property["ID"], property["NAME"])
			button.clicked.connect(self._on_property_clicked)


	def _on_property_clicked(self):
		clicked_property = self.sender().property("ID")

		if self.selected_property == -1 or self.selected_property != clicked_property:
			self.selected_property = clicked_property
			self.rename_group.setDisabled(False)
			self.remove_group.setDisabled(False)
		elif self.selected_property == clicked_property:
			self.selected_property = -1
			self.rename_group.setDisabled(True)
			self.remove_group.setDisabled(True)


	def _on_add_button_clicked(self):
		new_property_name = self.add_text.text()

		if new_property_name == "":
			return

		if self.selected_category == -1:
			return

		if database_interaction.property_exists(self.selected_category, new_property_name):
			return

		property_id = database_interaction.add_property(self.selected_category, new_property_name)

		self.add_text.setText("")

		button = self.property_list_widget.create_button(property_id, new_property_name)
		button.clicked.connect(self._on_property_clicked)


	def _on_rename_button_clicked(self):
		property_id = self.selected_property
		new_property_name = self.rename_text.text()

		if database_interaction.property_exists(self.selected_category, new_property_name):
			return

		database_interaction.rename_property(property_id, new_property_name)

		self.rename_text.setText("")

		self.property_list_widget.rename_button(property_id, new_property_name)


	def _on_remove_button_clicked(self):
		property_id = self.selected_property

		database_interaction.remove_property(property_id)
		self.property_list_widget.delete_button(property_id)

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

		layout = QGridLayout(self)
		layout.setRowStretch(0, 2)
		layout.setRowStretch(1, 2)
		layout.setRowStretch(2, 1)
		layout.setColumnStretch(0, 2)
		layout.setColumnStretch(1, 2)
		layout.setColumnStretch(2, 2)
		layout.setColumnStretch(3, 3)
		self.setLayout(layout)


		# Widget koji sadrzi skup elemenata koji prikazuju listu kategorija
		self.category_list_group = QGroupBox("Kategorije")
		self.category_list_group.setLayout(QVBoxLayout())

		self.category_list_widget = RadioButtonScrollList()
		self.category_list_group.layout().addWidget(self.category_list_widget)

		layout.addWidget(self.category_list_group, 0, 0, 3, 1)


		# Widget koji sadrzi skup elemenata koji prikazuju listu grupa svojstava
		self.property_list_group = QGroupBox("Grupe svojstava")
		self.property_list_group.setLayout(QVBoxLayout())

		self.property_list_widget = RadioButtonScrollList()
		self.property_list_group.layout().addWidget(self.property_list_widget)

		layout.addWidget(self.property_list_group, 0, 1, 3, 1)


		# Widget koji sadrzi skup elemenata koji prikazuju listu svojstava
		self.descriptor_list_group = QGroupBox("Svojstva")
		self.descriptor_list_group.setLayout(QVBoxLayout())

		self.descriptor_list_widget = RadioButtonScrollList()
		self.descriptor_list_group.layout().addWidget(self.descriptor_list_widget)

		layout.addWidget(self.descriptor_list_group, 0, 2, 3, 1)


		# Widget koji sadrzi skup elemenata za dodavanje svojstava
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
				color: #FFFFFF;
			}

			QPushButton::disabled {
				background-color: #005600;
				color: #2D4F2D;
			}
			"""
		)
		self.add_button.clicked.connect(self._on_add_button_clicked)
		self.add_group.layout().addWidget(self.add_button)

		layout.addWidget(self.add_group, 0, 3)


		# Widget koji sadrzi skup elemenata za preimenovanje svojstava
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
				color: #FFFFFF;
			}

			QPushButton::disabled {
				background-color: #474747;
				color: #727272;
			}
			"""
		)
		self.rename_button.clicked.connect(self._on_rename_button_clicked)
		self.rename_group.layout().addWidget(self.rename_button)

		layout.addWidget(self.rename_group, 1, 3)


		# Widget koji sadrzi skup elemenata za brisanje svojstava
		self.remove_group = QGroupBox("Izbriši svojstvo")
		self.remove_group.setLayout(QVBoxLayout())

		self.remove_button = QPushButton("Izbriši")
		self.remove_button.setStyleSheet(
			"""
			QPushButton {
				background-color: #890000;
				color: #FFFFFF;
			}

			QPushButton::disabled {
				background-color: #560000;
				color: #895959;
			}
			"""
		)
		self.remove_button.clicked.connect(self._on_remove_button_clicked)
		self.remove_group.layout().addWidget(self.remove_button)

		layout.addWidget(self.remove_group, 2, 3)


		self.selected_category = -1
		self.selected_property = -1
		self.selected_descriptor = -1
		self.close()


	def open(self):
		self.show()

		# Popuni listu kategorija sa kategorijama iz baze podataka
		for category in database_interaction.get_categories():
			button = self.category_list_widget.create_button(category["ID"], category["NAME"])
			button.clicked.connect(self._on_category_clicked)


	def close(self):
		self.hide()

		self.category_list_widget.delete_all_buttons()
		self.property_list_widget.delete_all_buttons()
		self.descriptor_list_widget.delete_all_buttons()
		self.add_group.setDisabled(True)
		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)
		self.selected_category = -1
		self.selected_property = -1
		self.selected_descriptor = -1


	def _on_category_clicked(self):
		clicked_category = self.sender().property("ID")

		if self.selected_category == -1 or self.selected_category != clicked_category:
			self.selected_category = clicked_category
		elif self.selected_category == clicked_category:
			self.selected_category = -1
			self.selected_property = -1
			self.selected_descriptor = -1

		self.add_group.setDisabled(True)
		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)

		self.property_list_widget.delete_all_buttons()
		self.descriptor_list_widget.delete_all_buttons()

		if self.selected_category == -1:
			return

		# Popuni listu grupa svojstava sa grupama svojstava iz baze podataka
		for property in database_interaction.get_properties(self.selected_category):
			button = self.property_list_widget.create_button(property["ID"], property["NAME"])
			button.clicked.connect(self._on_property_clicked)


	def _on_property_clicked(self):
		clicked_property = self.sender().property("ID")

		if self.selected_property == -1 or self.selected_property != clicked_property:
			self.selected_property = clicked_property
			self.add_group.setDisabled(False)
		elif self.selected_property == clicked_property:
			self.selected_property = -1
			self.add_group.setDisabled(True)

		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)

		self.descriptor_list_widget.delete_all_buttons()

		if self.selected_property == -1:
			return

		# Popuni listu svojstava sa svojstvima iz baze podataka
		for descriptor in database_interaction.get_descriptors(clicked_property):
			button = self.descriptor_list_widget.create_button(descriptor["ID"],descriptor["NAME"])
			button.clicked.connect(self._on_descriptor_clicked)


	def _on_descriptor_clicked(self):
		clicked_descriptor = self.sender().property("ID")

		if self.selected_descriptor == -1 or self.selected_descriptor != clicked_descriptor:
			self.selected_descriptor = clicked_descriptor
			self.rename_group.setDisabled(False)
			self.remove_group.setDisabled(False)
		elif self.selected_descriptor == clicked_descriptor:
			self.selected_descriptor = -1
			self.rename_group.setDisabled(True)
			self.remove_group.setDisabled(True)


	def _on_add_button_clicked(self):
		new_descriptor_name = self.add_text.text()

		if new_descriptor_name == "":
			return

		if self.selected_category == -1 or self.selected_property == -1:
			return

		if database_interaction.descriptor_exists(self.selected_property, new_descriptor_name):
			return

		descriptor_id = database_interaction.add_descriptor(
			self.selected_property,
			new_descriptor_name
		)

		self.add_text.setText("")

		button = self.descriptor_list_widget.create_button(descriptor_id, new_descriptor_name)
		button.clicked.connect(self._on_descriptor_clicked)


	def _on_rename_button_clicked(self):
		new_descriptor_name = self.rename_text.text()

		if database_interaction.descriptor_exists(self.selected_property, new_descriptor_name):
			return

		database_interaction.rename_descriptor(self.selected_descriptor, new_descriptor_name)

		self.rename_text.setText("")

		self.descriptor_list_widget.rename_button(self.selected_descriptor, new_descriptor_name)


	def _on_remove_button_clicked(self):
		database_interaction.remove_descriptor(self.selected_descriptor)
		self.descriptor_list_widget.delete_button(self.selected_descriptor)

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

		layout = QGridLayout()
		layout.setColumnStretch(0, 1)
		layout.setColumnStretch(1, 4)
		self.setLayout(layout)


		# Widget koji sadrzi skup elemenata koji prikazuju listu proizvoda
		self.list_group = QGroupBox("Proizvodi")
		self.list_group.setLayout(QVBoxLayout())

		self.list_widget = RadioButtonScrollList()
		self.list_group.layout().addWidget(self.list_widget)

		layout.addWidget(self.list_group, 0, 0)


		# Widget koji sadrzi skup elemenata za izmjenu i prikaz informacija o izabranom proizvodu
		self.info_group = QGroupBox("Informacije o proizvodu")
		self.info_group.setLayout(QGridLayout())
		self.info_group.layout().setColumnStretch(0, 1)
		self.info_group.layout().setColumnStretch(1, 2)
		self.info_group.layout().setColumnStretch(2, 2)
		self.info_group.layout().setRowStretch(1, 2)
		self.info_group.layout().setContentsMargins(11, 17, 11, 11)
		self.info_group.layout().setSpacing(20)

		layout.addWidget(self.info_group, 0, 1)


		# Widget koji sadrzi skup elemenata za izmjenu i prikaz slike proizvoda
		self.image_group = QWidget()
		self.image_group.setLayout(QGridLayout())
		self.image_group.layout().setContentsMargins(0, 0, 0, 0)
		self.image_group.layout().setRowStretch(100, 10)

		self.image_title = QLabel("<b>Slika</b>")
		self.image_group.layout().addWidget(self.image_title, 0, 0)

		self.image_display = QLabel()
		self.image_display.setStyleSheet("border: 1px solid black;")
		self.image_display.setFixedSize(100, 100)
		self.image_display.setScaledContents(True)
		pixmap = QPixmap("resources/item_images/no_image.png")
		self.image_display.setPixmap(pixmap)
		self.image_group.layout().addWidget(self.image_display, 1, 0)

		self.image_button = QPushButton("Učitaj sliku")
		self.image_button.clicked.connect(self._on_load_image_clicked)
		self.image_button.setStyleSheet("font-size: 9pt; height: 18;")
		self.image_group.layout().addWidget(self.image_button, 2, 0)

		self.info_group.layout().addWidget(self.image_group, 0, 0, 4, 1)


		# Widget koji sadrzi skup elemenata za izmjenu i prikaz naziva proizvoda
		self.name_group = QWidget()
		self.name_group.setLayout(QVBoxLayout())
		self.name_group.layout().setContentsMargins(0, 0, 0, 0)

		self.name_title = QLabel("<b>Naziv</b>")
		self.name_group.layout().addWidget(self.name_title)

		self.name_edit = QPlainTextEdit()
		self.name_edit.setMinimumHeight(43)
		self.name_edit.textChanged.connect(self._on_name_changed)
		self.name_group.layout().addWidget(self.name_edit)

		self.info_group.layout().addWidget(self.name_group, 0, 1, 2, 1)


		# Widget koji sadrzi skup elemenata za izmjenu i prikaz cijene proizvoda
		self.price_group = QWidget()
		self.price_group.setLayout(QGridLayout())
		self.price_group.layout().setContentsMargins(0, 0, 0, 0)

		self.price_title = QLabel("<b>Cijena</b>")
		self.price_group.layout().addWidget(self.price_title, 0, 0)

		self.price_edit = QLineEdit()
		self.price_edit.setAlignment(Qt.AlignRight)
		self.price_validator = QDoubleValidator(0, 9999999, 2)
		self.price_validator.setNotation(QDoubleValidator.StandardNotation)
		self.price_edit.setValidator(self.price_validator)
		self.price_group.layout().addWidget(self.price_edit, 1, 0)

		self.price_currency_label = QLabel("€")
		self.price_group.layout().addWidget(self.price_currency_label, 1, 1)
		self.info_group.layout().addWidget(self.price_group, 2, 1)


		# Widget koji sadrzi skup elemenata za izmjenu i prikaz kolicine proizvoda
		self.amount_group = QWidget()
		self.amount_group.setLayout(QGridLayout())
		self.amount_group.layout().setContentsMargins(0, 0, 0, 0)
		self.amount_group.layout().setSpacing(0)
		self.amount_group.layout().setColumnStretch(2, 10)
		self.amount_group.setStyleSheet(
			"""
			QPushButton {
				padding: 0px 0px;
				width: 32px;
				height: 26px
			}
			"""
		)

		self.amount_title = QLabel("<b>Količina</b>")
		self.amount_group.layout().addWidget(self.amount_title, 0, 0, 1, 5)

		self.amount_minus10_button = QPushButton("-10")
		self.amount_minus10_button.clicked.connect(self._on_minus_10_clicked)
		self.amount_group.layout().addWidget(self.amount_minus10_button, 1, 0)

		self.amount_minus1_button = QPushButton("-1")
		self.amount_minus1_button.clicked.connect(self._on_minus_1_clicked)
		self.amount_group.layout().addWidget(self.amount_minus1_button, 1, 1)

		self.amount_edit = QLineEdit()
		self.amount_edit.setAlignment(Qt.AlignHCenter)
		self.amount_group.layout().addWidget(self.amount_edit, 1, 2)
		self.amount_validator = QIntValidator(0, 99999999)
		self.amount_edit.setValidator(self.amount_validator)

		self.amount_plus1_button = QPushButton("+1")
		self.amount_plus1_button.clicked.connect(self._on_plus_1_clicked)
		self.amount_group.layout().addWidget(self.amount_plus1_button, 1, 3)

		self.amount_plus10_button = QPushButton("+10")
		self.amount_plus10_button.clicked.connect(self._on_plus_10_clicked)
		self.amount_group.layout().addWidget(self.amount_plus10_button, 1, 4)

		self.info_group.layout().addWidget(self.amount_group, 3, 1)


		# Widget koji sadrzi skup elemenata za izmjenu i prikaz kategorije proizvoda
		self.category_group = QWidget()
		self.category_group.setLayout(QVBoxLayout())
		self.category_group.layout().setContentsMargins(0, 0, 0, 0)

		self.category_title = QLabel("<b>Kategorija</b>")
		self.category_group.layout().addWidget(self.category_title)

		self.category_edit = QComboBox()
		self.category_edit.currentTextChanged.connect(self._on_category_changed)
		self.category_group.layout().addWidget(self.category_edit)

		self.category_group.layout().addStretch()
		self.info_group.layout().addWidget(self.category_group, 0, 2)


		# Widget koji sadrzi skup elemenata za izmjenu i prikaz svojstava proizvoda
		self.property_group = QWidget()
		self.property_group.setLayout(QVBoxLayout())
		self.property_group.layout().setContentsMargins(0, 0, 0, 0)

		self.property_title = QLabel("<b>Svojstva</b>")
		self.property_group.layout().addWidget(self.property_title)

		self.property_edit = FoldableSectionsCheckboxesScrollList()
		self.property_group.layout().addWidget(self.property_edit)

		empty_space = QWidget()
		empty_space.setMinimumHeight(18)

		self.property_group.layout().addWidget(empty_space)
		self.info_group.layout().addWidget(self.property_group, 1, 2, 4, 1)


		# Widget koji sadrzi skup elemenata za izmjenu i prikaz opisa proizvoda
		self.description_group = QWidget()
		self.description_group.setLayout(QVBoxLayout())
		self.description_group.layout().setContentsMargins(0, 0, 0, 0)

		self.description_title = QLabel("<b>Opis</b>")
		self.description_group.layout().addWidget(self.description_title)

		self.description_edit = QPlainTextEdit()
		self.description_group.layout().addWidget(self.description_edit)

		self.info_group.layout().addWidget(self.description_group, 4, 0, 2, 2)


		# Button za dodavanje proizvoda u bazu podataka
		self.add_button = QPushButton("Dodaj")
		self.add_button.setStyleSheet(
			"""
			QPushButton {
				background-color: #008900;
				color: #FFFFFF;
			}

			QPushButton::disabled {
				background-color: #005600;
				color: #2D4F2D;
			}
			"""
		)
		self.add_button.clicked.connect(self._on_add_button_clicked)
		self.info_group.layout().addWidget(self.add_button, 5, 2)


		# Button za primjenu unesenih detalja o proizvodu
		self.edit_button = QPushButton("Primijeni izmjene")
		self.edit_button.setStyleSheet(
			"""
			QPushButton {
				background-color: #666666;
				color: #FFFFFF;
			}

			QPushButton::disabled {
				background-color: #474747;
				color: #727272;
			}
			"""
		)
		self.edit_button.clicked.connect(self._on_edit_button_clicked)
		self.info_group.layout().addWidget(self.edit_button, 5, 2)


		# Button za brisanje proizvoda iz baze podataka
		self.remove_button = QPushButton("Izbriši")
		self.remove_button.setStyleSheet(
			"""
			QPushButton {
				background-color: #890000;
				color: #FFFFFF;
			}

			QPushButton::disabled {
				background-color: #560000;
				color: #895959;
			}
			"""
		)
		self.remove_button.clicked.connect(self._on_remove_button_clicked)
		self.info_group.layout().addWidget(self.remove_button, 5, 2)


		self.chosen_image_filename = ""
		self.selected_item_id = -1
		self.selected_mode = ""
		self.reset_item_list()
		self.close()


	def reset_item_list(self):
		self.list_widget.delete_all_buttons()

		# Popuni listu proizvoda sa proizvodima iz baze podataka
		for item in database_interaction.get_items():
			button = self.list_widget.create_button(item["ID"], item["NAME"])
			button.clicked.connect(self._on_item_clicked)


	def open(self):
		self.update_category_list()
		self.show()


	def close(self):
		self.selected_mode = ""
		self.hide()


	# Toggle za interakciju s elementima koji prikazuju detalje o proizvodu
	def set_info_interaction_state(self, state):
		self.image_group.setDisabled(not state)
		self.name_group.setDisabled(not state)
		self.price_group.setDisabled(not state)
		self.amount_group.setDisabled(not state)
		self.category_group.setDisabled(not state)
		self.property_group.setDisabled(not state)
		self.description_group.setDisabled(not state)


	def update_category_list(self):
		# Izbrisi sve kategorije iz widgeta
		while self.category_edit.count() > 0:
			self.category_edit.removeItem(0)

		# Dodaj iznova nabavljene kategorije u widget
		for category in database_interaction.get_categories():
			category_name = category["NAME"]
			self.category_edit.addItem(category_name.capitalize())

		self.category_edit.setCurrentIndex(-1)


	def update_property_list(self):
		# Izbrisi sva svojstva iz widgeta
		self.property_edit.clear()

		item_category_name = self.category_edit.currentText()
		if not item_category_name:
			return

		# Dodaj iznova svojstva i grupe svojstava iz baze podataka
		item_category_id = database_interaction.get_category_id(item_category_name)
		for property in database_interaction.get_properties(item_category_id):
			descriptors = []

			for descriptor in database_interaction.get_descriptors(property["ID"]):
				descriptor_id = descriptor["ID"]
				descriptor_name = descriptor["NAME"]
				descriptors.append(
					{"ID": descriptor_id, "NAME": descriptor_name.capitalize()}
				)

			self.property_edit.add_section(property["NAME"], descriptors)


	def update_selected_descriptors(self):
		for checkbox in self.property_edit.checkboxes.values():
			checkbox.setChecked(False)
		if self.selected_item_id > -1:
			selected_item_descriptor_ids = \
				database_interaction.get_item_descriptors(self.selected_item_id)
			for descriptor_id in selected_item_descriptor_ids:
				self.property_edit.checkboxes[descriptor_id].setChecked(True)


	# Predi u submode dodavanja proizvoda
	def switch_to_item_add(self):
		self.open()
		self.info_group.setTitle("Dodaj proizvod")
		self.selected_mode = "add"

		self.edit_button.hide()
		self.remove_button.hide()
		self.add_button.show()

		# Unselectaj odprije izabrani proizvod s liste
		self.list_widget.unselect_all_buttons()
		self.selected_item_id = -1

		self.list_group.hide()
		self.layout().setColumnStretch(0, 0)

		# Izbrisi sav info proizvoda iz elemenata
		self.set_item_info()

		self.set_info_interaction_state(True)


	# Predi u submode izmjene detalja proizvoda
	def switch_to_item_edit(self):
		self.open()
		self.info_group.setTitle("Izmijeni detalje proizvoda")
		self.selected_mode = "edit"

		self.add_button.hide()
		self.remove_button.hide()
		self.edit_button.show()

		# Unselectaj odprije izabrani proizvod s liste
		self.list_widget.unselect_all_buttons()
		self.selected_item_id = -1

		self.list_group.show()
		self.layout().setColumnStretch(0, 2)

		# Izbrisi sve info proizvoda iz input elemenata
		self.set_item_info()

		self.set_info_interaction_state(False)


	# Predi u submode brisanja proizvoda
	def switch_to_item_remove(self):
		self.open()
		self.info_group.setTitle("Izbriši proizvod")
		self.selected_mode = "remove"

		self.edit_button.hide()
		self.add_button.hide()
		self.remove_button.show()

		# Unselectaj odprije izabrani proizvod s liste
		self.list_widget.unselect_all_buttons()
		self.selected_item_id = -1

		# Disableaj remove button jer nijedan proizvod nije izabran
		self.remove_button.setDisabled(True)

		self.list_group.show()
		self.layout().setColumnStretch(0, 2)

		# Izbrisi sve info proizvoda iz input elemenata
		self.set_item_info()

		self.set_info_interaction_state(False)


	def set_item_info(self, item_id = "undefined"):
		# Ako nije definiran item_id, izbrisi info
		if item_id == "undefined":
			self.image_display.setPixmap(QPixmap())
			self.chosen_image_filename = ""
			self.name_edit.setPlainText("")
			self.price_edit.setText("")
			self.amount_edit.setText("0")
			self.description_edit.setPlainText("")
			self.category_edit.setCurrentIndex(-1)

		# Ako je definiran item_id, popuni info polja s informacijama iz baze podataka
		else:
			item = database_interaction.get_item(item_id)

			if item['IMAGE']:
				pixmap = QPixmap(f"resources/item_images/{item['IMAGE']}")
				self.chosen_image_filename = item['IMAGE']
			else:
				pixmap = QPixmap(f"resources/item_images/no_image.png")
				self.chosen_image_filename = ""

			self.image_display.setPixmap(pixmap)
			self.name_edit.setPlainText(item["NAME"])
			self.price_edit.setText(item["PRICE"])
			self.amount_edit.setText(str(item["AMOUNT"]))
			self.description_edit.setPlainText(item["DETAILS"])

			category_name = database_interaction.get_category_name(item["CATEGORY_ID"])
			self.category_edit.setCurrentText(category_name.capitalize())

		self.update_selected_descriptors()


	def _on_item_clicked(self):
		clicked_item_id = self.sender().property("ID")

		# Ako vec nije bio izabran proizvod ili je drugaciji od kliknutog,
		# izaberi kliknutog
		if self.selected_item_id == -1 or self.selected_item_id != clicked_item_id:
			self.selected_item_id = clicked_item_id
			self.set_item_info(clicked_item_id)

			if self.selected_mode == "edit":
				self.set_info_interaction_state(True)
			elif self.selected_mode == "remove":
				self.remove_button.setDisabled(False)

		# Ako je vec izabrani proizvod isti kao kliknuti, unselectaj ga
		elif self.selected_item_id == clicked_item_id:
			self.list_widget.unselect_all_buttons()
			self.selected_item_id = -1
			self.set_item_info()

			if self.selected_mode == "edit":
				self.set_info_interaction_state(False)
			elif self.selected_mode == "remove":
				self.remove_button.setDisabled(True)


	def _on_name_changed(self):
		item_name = self.name_edit.toPlainText()
		item_category_name = self.category_edit.currentText()

		if item_name and item_category_name:
			self.add_button.setDisabled(False)
			self.edit_button.setDisabled(False)
		else:
			self.add_button.setDisabled(True)
			self.edit_button.setDisabled(True)


	def _on_category_changed(self):
		item_name = self.name_edit.toPlainText()
		item_category_name = self.category_edit.currentText()

		if item_name and item_category_name:
			self.add_button.setDisabled(False)
			self.edit_button.setDisabled(False)
		else:
			self.add_button.setDisabled(True)
			self.edit_button.setDisabled(True)

		if item_category_name:
			if self.selected_mode == "add" or self.selected_mode == "edit":
				self.property_group.setDisabled(False)
		else:
			self.property_group.setDisabled(True)

		self.update_property_list()


	def _on_load_image_clicked(self):
		image_file_absolute_path = QFileDialog.getOpenFileName(
			self,
			caption = "Choose image from this directory",
			dir = "resources/item_images",
			filter = "Image Files (*.png *.jpg *.bmp)"
		)[0]

		image_file_name = image_file_absolute_path.split("/")[-1]

		if image_file_name:
			pixmap = QPixmap(f"resources/item_images/{image_file_name}")
			self.chosen_image_filename = image_file_name
		else:
			pixmap = QPixmap(f"resources/item_images/no_image.png")
			self.chosen_image_filename = ""
		self.image_display.setPixmap(pixmap)


	def _on_minus_10_clicked(self):
		current_value = int(self.amount_edit.text())
		if current_value > 10:
			new_value = current_value - 10
		else:
			new_value = 0
		self.amount_edit.setText(str(new_value))


	def _on_minus_1_clicked(self):
		current_value = int(self.amount_edit.text())
		if current_value > 1:
			new_value = current_value - 1
		else:
			new_value = 0
		self.amount_edit.setText(str(new_value))


	def _on_plus_1_clicked(self):
		current_value = int(self.amount_edit.text())
		self.amount_edit.setText(str(current_value + 1))


	def _on_plus_10_clicked(self):
		current_value = int(self.amount_edit.text())
		self.amount_edit.setText(str(current_value + 10))


	def _on_add_button_clicked(self):
		item_id = database_interaction.add_item(
			self.name_edit.toPlainText(),
			self.price_edit.text().replace(".", ""),
			int(self.amount_edit.text()),
			self.category_edit.currentText(),
			self.chosen_image_filename,
			self.description_edit.toPlainText(),
			self.property_edit.get_checked_checkbox_ids()
		)

		button = self.list_widget.create_button(item_id, self.name_edit.toPlainText())
		button.clicked.connect(self._on_item_clicked)
		self.set_item_info()


	def _on_edit_button_clicked(self):
		database_interaction.edit_item(
			self.selected_item_id,
			self.name_edit.toPlainText(),
			self.price_edit.text().replace(".", ""),
			int(self.amount_edit.text()),
			self.category_edit.currentText(),
			self.chosen_image_filename,
			self.description_edit.toPlainText(),
			self.property_edit.get_checked_checkbox_ids()
		)

		self.list_widget.rename_button(self.selected_item_id, self.name_edit.toPlainText())


	def _on_remove_button_clicked(self):
		database_interaction.remove_item(self.selected_item_id)

		self.set_item_info()
		self.list_widget.delete_button(self.selected_item_id)

		self.remove_button.setDisabled(True)



# Instanciranje klasa
window = Window()
category_edit_widget = CategoryEditWidget(window)
property_edit_widget = PropertyEditWidget(window)
descriptor_edit_widget = DescriptorEditWidget(window)
item_edit_widget = ItemEditWidget(window)
mode_bar = ModeBar(window)


# Smjestanje widgeta u window
window.base_widget.layout().addWidget(mode_bar, 0, 0)
window.base_widget.layout().addWidget(category_edit_widget, 1, 0)
window.base_widget.layout().addWidget(property_edit_widget, 1, 0)
window.base_widget.layout().addWidget(descriptor_edit_widget, 1, 0)
window.base_widget.layout().addWidget(item_edit_widget, 1, 0)

app.exec()