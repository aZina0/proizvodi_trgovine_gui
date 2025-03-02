from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
import os
import database_interaction


# Resetiranje baze podataka
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



class RadioButtonScrollList(QScrollArea):
	def __init__(self):
		super().__init__()

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
		self.base_widget.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
		self.setWidget(self.base_widget)
		self.setWidgetResizable(True)

		self.buttons = {}


	def button_clicked(self):
		clicked_button_id = self.sender().property("ID")
		for button_id in self.buttons:
			if button_id != clicked_button_id:
				self.buttons[button_id].setChecked(False)


	def create_button(self, id, text):
		text = text.lower()

		button = QPushButton(text.capitalize())
		button.setCheckable(True)
		button.setProperty("ID", id)
		button.clicked.connect(self.button_clicked)
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



class FoldableSectionsCheckboxesScrollList(QScrollArea):
	def __init__(self):
		super().__init__()

		self.setStyleSheet("""
			QScrollArea {
				border: 1px solid black;
			}

			QToolButton {
				background-color: #292929;
				border: 1px solid #393939;
				font-size: 10pt;
				text-align: left;
			}

			QCheckBox::indicator {
				margin-left: 20px;
				border: 1px solid gray;
			}

			QCheckBox::indicator:unchecked {
				image: url(resources/no_checkmark.png);
			}

			QCheckBox::indicator:checked {
				image: url(resources/checkmark.png);
			}
		""")

		self.base_widget = QWidget(self)
		self.base_widget.setLayout(QVBoxLayout())
		self.base_widget.layout().setContentsMargins(0, 0, 0, 0)
		self.base_widget.layout().setSpacing(0)
		self.base_widget.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
		self.setWidget(self.base_widget)
		self.setWidgetResizable(True)

		self.disabled = False
		self.section_widgets = {}
		self.checkboxes = {}


	def add_section(self, section_name, checkbox_infos):
		section_button = QToolButton()
		section_button.setArrowType(Qt.RightArrow)
		section_button.setText(section_name)
		section_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		section_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		section_button.clicked.connect(self.section_clicked)
		self.base_widget.layout().addWidget(section_button)

		checkboxes_widget = QWidget()
		checkboxes_widget.setLayout(QVBoxLayout())
		checkboxes_widget.layout().setContentsMargins(0, 0, 0, 0)
		checkboxes_widget.layout().setSpacing(0)
		checkboxes_widget.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
		checkboxes_widget.hide()
		self.section_widgets[section_name] = checkboxes_widget

		for checkbox_info in checkbox_infos:
			checkbox_name = checkbox_info["NAME"]
			checkbox_id = checkbox_info["ID"]

			checkbox = QCheckBox(checkbox_name)
			checkbox.setProperty("ID", checkbox_id)
			if self.disabled:
				checkbox.setDisabled(True)
			self.checkboxes[checkbox_id] = checkbox
			checkboxes_widget.layout().addWidget(checkbox)

		self.base_widget.layout().addWidget(checkboxes_widget)


	def clear(self):
		while self.base_widget.layout().count() > 0:
			widget = self.base_widget.layout().itemAt(0).widget()
			self.base_widget.layout().removeWidget(widget)
			widget.deleteLater()

		self.section_widgets.clear()
		self.checkboxes.clear()


	def section_clicked(self):
		section_button = self.sender()
		clicked_section_name = self.sender().text()

		section_widget = self.section_widgets[clicked_section_name]
		# Ako je sekcija skrivena, prikazi ju i promjeni strelicu
		if section_widget.isHidden():
			section_button.setArrowType(Qt.DownArrow)
			section_widget.show()
		# Ako je sekcija prikazana, sakrij ju i promjeni strelicu
		else:
			section_button.setArrowType(Qt.RightArrow)
			section_widget.hide()


	def setDisabled(self, state):
		# Ako disable, samo disableaj interakciju s checkboxevima (dozvoli scrollanje)
		if state:
			self.disabled = True
			super().setDisabled(False)
			for checkbox in self.checkboxes.values():
				checkbox.setDisabled(True)

		# Inače ako enable, omogući sve
		else:
			self.disabled = False
			super().setDisabled(False)
			for checkbox in self.checkboxes.values():
				checkbox.setDisabled(False)


	def get_checked_checkbox_ids(self):
		checked_checkbox_ids = []

		for id in self.checkboxes:
			checkbox = self.checkboxes[id]
			if checkbox.checkState() == Qt.Checked:
				checked_checkbox_ids.append(id)

		return checked_checkbox_ids




class Window(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setMinimumSize(850, 450)
		self.setWindowTitle("Uređivač proizvoda")
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
			"category_edit": QPushButton("Uredi kategorije"),
			"property_edit": QPushButton("Uredi grupe svojstava"),
			"descriptor_edit": QPushButton("Uredi svojstva"),
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

		self.list_widget = RadioButtonScrollList()
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

		self.selected_category = -1

		self.close()


	def open(self):
		self.show()

		for category in database_interaction.get_categories():
			button = self.list_widget.create_button(category["ID"], category["NAME"])
			button.clicked.connect(self.category_clicked)


	def close(self):
		self.hide()

		self.list_widget.delete_all_buttons()
		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)
		self.selected_category = -1


	def category_clicked(self):
		category_id = self.sender().property("ID")

		if self.selected_category == -1 or self.selected_category != category_id:
			self.selected_category = category_id
			self.rename_group.setDisabled(False)
			self.remove_group.setDisabled(False)
		elif self.selected_category == category_id:
			self.selected_category = -1
			self.rename_group.setDisabled(True)
			self.remove_group.setDisabled(True)


	def add_button_clicked(self):
		new_category_name = self.add_text.text()

		if new_category_name == "":
			return

		if database_interaction.category_exists(new_category_name):
			return

		new_category_id = database_interaction.add_category(new_category_name)

		self.add_text.setText("")

		button = self.list_widget.create_button(new_category_id, new_category_name)
		button.clicked.connect(self.category_clicked)


	def rename_button_clicked(self):
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


	def remove_button_clicked(self):
		category_id = self.selected_category
		category_name = database_interaction.get_category_name(category_id).lower()

		# Odbaci pokušaj brisanja kategorije proizvoda "Ostalo"
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


		self.category_list_group = QGroupBox("Kategorije")
		self.category_list_group.setLayout(QVBoxLayout())

		self.category_list_widget = RadioButtonScrollList()
		self.category_list_group.layout().addWidget(self.category_list_widget)


		self.property_list_group = QGroupBox("Grupe svojstava")
		self.property_list_group.setLayout(QVBoxLayout())

		self.property_list_widget = RadioButtonScrollList()
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

		self.selected_category = -1
		self.selected_property = -1

		self.close()


	def open(self):
		self.show()

		for category in database_interaction.get_categories():
			button = self.category_list_widget.create_button(category["ID"], category["NAME"])
			button.clicked.connect(self.category_clicked)


	def close(self):
		self.hide()

		self.category_list_widget.delete_all_buttons()
		self.property_list_widget.delete_all_buttons()
		self.add_group.setDisabled(True)
		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)
		self.selected_category = -1
		self.selected_property = -1


	def category_clicked(self):
		category_id = self.sender().property("ID")

		if self.selected_category == -1 or self.selected_category != category_id:
			self.selected_category = category_id
			self.add_group.setDisabled(False)
		elif self.selected_category == category_id:
			self.selected_category = -1
			self.selected_property = -1
			self.add_group.setDisabled(True)

		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)

		self.property_list_widget.delete_all_buttons()

		if self.selected_category == -1:
			return

		for property in database_interaction.get_properties(self.selected_category):
			button = self.property_list_widget.create_button(property["ID"], property["NAME"])
			button.clicked.connect(self.property_clicked)


	def property_clicked(self):
		property_id = self.sender().property("ID")

		if self.selected_property == -1 or self.selected_property != property_id:
			self.selected_property = property_id
			self.rename_group.setDisabled(False)
			self.remove_group.setDisabled(False)
		elif self.selected_property == property_id:
			self.selected_property = -1
			self.rename_group.setDisabled(True)
			self.remove_group.setDisabled(True)


	def add_button_clicked(self):
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
		button.clicked.connect(self.property_clicked)


	def rename_button_clicked(self):
		property_id = self.selected_property
		new_property_name = self.rename_text.text()

		if database_interaction.property_exists(self.selected_category, new_property_name):
			return

		database_interaction.rename_property(property_id, new_property_name)

		self.rename_text.setText("")

		self.property_list_widget.rename_button(property_id, new_property_name)


	def remove_button_clicked(self):
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


		self.category_list_group = QGroupBox("Kategorije")
		self.category_list_group.setLayout(QVBoxLayout())

		self.category_list_widget = RadioButtonScrollList()
		self.category_list_group.layout().addWidget(self.category_list_widget)


		self.property_list_group = QGroupBox("Grupe svojstava")
		self.property_list_group.setLayout(QVBoxLayout())

		self.property_list_widget = RadioButtonScrollList()
		self.property_list_group.layout().addWidget(self.property_list_widget)


		self.descriptor_list_group = QGroupBox("Svojstva")
		self.descriptor_list_group.setLayout(QVBoxLayout())

		self.descriptor_list_widget = RadioButtonScrollList()
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

		self.selected_category = -1
		self.selected_property = -1
		self.selected_descriptor = -1

		self.close()


	def open(self):
		self.show()

		for category in database_interaction.get_categories():
			button = self.category_list_widget.create_button(category["ID"], category["NAME"])
			button.clicked.connect(self.category_clicked)


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


	def category_clicked(self):
		category_id = self.sender().property("ID")

		if self.selected_category == -1 or self.selected_category != category_id:
			self.selected_category = category_id
		elif self.selected_category == category_id:
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

		for property in database_interaction.get_properties(self.selected_category):
			button = self.property_list_widget.create_button(property["ID"], property["NAME"])
			button.clicked.connect(self.property_clicked)


	def property_clicked(self):
		property_id = self.sender().property("ID")

		if self.selected_property == -1 or self.selected_property != property_id:
			self.selected_property = property_id
			self.add_group.setDisabled(False)
		elif self.selected_property == property_id:
			self.selected_property = -1
			self.add_group.setDisabled(True)

		self.rename_group.setDisabled(True)
		self.remove_group.setDisabled(True)

		self.descriptor_list_widget.delete_all_buttons()

		if self.selected_property == -1:
			return

		for descriptor in database_interaction.get_descriptors(property_id):
			button = self.descriptor_list_widget.create_button(descriptor["ID"],descriptor["NAME"])
			button.clicked.connect(self.descriptor_clicked)


	def descriptor_clicked(self):
		descriptor_id = self.sender().property("ID")

		if self.selected_descriptor == -1 or self.selected_descriptor != descriptor_id:
			self.selected_descriptor = descriptor_id
			self.rename_group.setDisabled(False)
			self.remove_group.setDisabled(False)
		elif self.selected_descriptor == descriptor_id:
			self.selected_descriptor = -1
			self.rename_group.setDisabled(True)
			self.remove_group.setDisabled(True)


	def add_button_clicked(self):
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
		button.clicked.connect(self.descriptor_clicked)


	def rename_button_clicked(self):
		new_descriptor_name = self.rename_text.text()

		if database_interaction.descriptor_exists(self.selected_property, new_descriptor_name):
			return

		database_interaction.rename_descriptor(self.selected_descriptor, new_descriptor_name)

		self.rename_text.setText("")

		self.descriptor_list_widget.rename_button(self.selected_descriptor, new_descriptor_name)


	def remove_button_clicked(self):
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

		self.list_group = QGroupBox("Proizvodi")
		self.list_group.setLayout(QVBoxLayout())

		self.list_widget = RadioButtonScrollList()
		self.list_group.layout().addWidget(self.list_widget)


		self.info_group = QGroupBox("Informacije o proizvodu")
		self.info_group.setLayout(QGridLayout())
		self.info_group.layout().setColumnStretch(0, 1)
		self.info_group.layout().setColumnStretch(1, 2)
		self.info_group.layout().setColumnStretch(2, 2)
		self.info_group.layout().setContentsMargins(11, 17, 11, 11)
		self.info_group.layout().setVerticalSpacing(0)
		self.info_group.layout().setHorizontalSpacing(20)

		self.item_image_label = QLabel("<b>Slika</b>")
		self.info_group.layout().addWidget(self.item_image_label, 0, 0)
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
		self.info_group.layout().addWidget(self.image_display, 1, 0, 4, 1)
		self.image_button = QPushButton("Učitaj sliku")
		self.image_button.clicked.connect(self.load_image_clicked)
		self.image_button.setStyleSheet(
			"""
			QPushButton {
				font-size: 9pt;
				height: 18;
			}
			"""
		)
		self.info_group.layout().addWidget(self.image_button, 5, 0)


		empty_space = QWidget()
		empty_space.setFixedHeight(15)
		self.info_group.layout().addWidget(empty_space, 6, 0)


		self.item_name_label = QLabel("<b>Naziv</b>")
		self.info_group.layout().addWidget(self.item_name_label, 0, 1)
		self.item_name_edit = QPlainTextEdit()
		self.item_name_edit.setMaximumHeight(75)
		self.item_name_edit.textChanged.connect(self.item_name_changed)
		self.info_group.layout().addWidget(self.item_name_edit, 1, 1, 3, 1)

		self.item_category_label = QLabel("<b>Kategorija</b>")
		self.info_group.layout().addWidget(self.item_category_label, 0, 2)
		self.item_category_edit = QComboBox()
		self.item_category_edit.currentTextChanged.connect(self.item_category_changed)
		self.info_group.layout().addWidget(self.item_category_edit, 1, 2)

		self.item_property_label = QLabel("<b>Svojstva</b>")
		self.info_group.layout().addWidget(self.item_property_label, 3, 2)
		self.item_property_edit = FoldableSectionsCheckboxesScrollList()
		self.info_group.layout().addWidget(self.item_property_edit, 4, 2, 5, 1)

		self.item_description_label = QLabel("<b>Opis</b>")
		self.info_group.layout().addWidget(self.item_description_label, 7, 0, 1, 3)
		self.item_description_edit = QPlainTextEdit()
		self.info_group.layout().addWidget(self.item_description_edit, 8, 0, 3, 2)


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
		self.info_group.layout().addWidget(self.add_button, 10, 2)

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
		self.info_group.layout().addWidget(self.edit_button, 10, 2)

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
		self.info_group.layout().addWidget(self.remove_button, 10, 2)



		layout = QGridLayout()
		layout.setColumnStretch(0, 1)
		layout.setColumnStretch(1, 4)
		layout.addWidget(self.list_group, 0, 0)
		layout.addWidget(self.info_group, 0, 1)
		self.setLayout(layout)

		self.reset_item_list()
		self.close()

		self.chosen_image_filename = ""
		self.selected_item_id = -1
		self.selected_mode = ""


	def reset_item_list(self):
		self.list_widget.delete_all_buttons()

		for item in database_interaction.get_items():
			button = self.list_widget.create_button(item["ID"], item["NAME"])
			button.clicked.connect(self.item_clicked)


	def open(self):
		self.update_category_list()
		self.show()


	def close(self):
		self.selected_mode = ""
		self.hide()


	def set_info_interaction_state(self, state):
		self.image_display.setDisabled(not state)
		self.image_button.setDisabled(not state)
		self.item_name_label.setDisabled(not state)
		self.item_name_edit.setDisabled(not state)
		self.item_description_label.setDisabled(not state)
		self.item_description_edit.setDisabled(not state)
		self.item_category_label.setDisabled(not state)
		self.item_category_edit.setDisabled(not state)
		self.item_property_label.setDisabled(not state)
		self.item_property_edit.setDisabled(not state)


	def update_category_list(self):
		# Izbrisi sve kategorije iz widgeta
		while self.item_category_edit.count() > 0:
			self.item_category_edit.removeItem(0)

		# Dodaj iznova nabavljene kategorije u widget
		for category in database_interaction.get_categories():
			category_name = category["NAME"]
			self.item_category_edit.addItem(category_name.capitalize())

		# Namjesti da nijedna kategorija nije izabrana
		self.item_category_edit.setCurrentIndex(-1)


	def update_property_list(self):
		self.item_property_edit.clear()

		item_category_name = self.item_category_edit.currentText()
		if not item_category_name:
			return

		item_category_id = database_interaction.get_category_id(item_category_name)
		for property in database_interaction.get_properties(item_category_id):
			descriptors = []

			for descriptor in database_interaction.get_descriptors(property["ID"]):
				descriptor_id = descriptor["ID"]
				descriptor_name = descriptor["NAME"]
				descriptors.append(
					{"ID": descriptor_id, "NAME": descriptor_name.capitalize()}
				)

			self.item_property_edit.add_section(property["NAME"], descriptors)


	def update_selected_descriptors(self):
		for checkbox in self.item_property_edit.checkboxes.values():
			checkbox.setChecked(False)
		if self.selected_item_id > -1:
			selected_item_descriptor_ids = \
				database_interaction.get_item_descriptors(self.selected_item_id)
			for descriptor_id in selected_item_descriptor_ids:
				self.item_property_edit.checkboxes[descriptor_id].setChecked(True)


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

		# Sakrij listu s proizvodima
		self.list_group.hide()
		self.layout().setColumnStretch(0, 0)

		# Izbrisi sve info proizvoda iz input elemenata
		self.set_item_info()

		# Omoguci interakciju s info elementima
		self.set_info_interaction_state(True)


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

		# Prikazi listu s proizvodima
		self.list_group.show()
		self.layout().setColumnStretch(0, 2)

		# Izbrisi sve info proizvoda iz input elemenata
		self.set_item_info()

		# Onemoguci interakciju s info elementima
		self.set_info_interaction_state(False)


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

		# Prikazi listu s proizvodima
		self.list_group.show()
		self.layout().setColumnStretch(0, 2)

		# Izbrisi sve info proizvoda iz input elemenata
		self.set_item_info()

		# Onemoguci interakciju s info elementima
		self.set_info_interaction_state(False)


	def set_item_info(self, item_id = "undefined"):
		# Ako nije definiran item_id, izbrisi info
		if item_id == "undefined":
			self.image_display.setPixmap(QPixmap())
			self.chosen_image_filename = ""
			self.item_name_edit.setPlainText("")
			self.item_description_edit.setPlainText("")
			self.item_category_edit.setCurrentIndex(-1)

		# Ako je definiran item_id, uzmi informacije iz baze podataka i popuni polja
		else:
			item = database_interaction.get_item(item_id)

			if item['IMAGE']:
				pixmap = QPixmap(f"resources/item_images/{item['IMAGE']}")
				self.chosen_image_filename = item['IMAGE']
			else:
				pixmap = QPixmap(f"resources/item_images/no_image.png")
				self.chosen_image_filename = ""
			self.image_display.setPixmap(pixmap)
			self.item_name_edit.setPlainText(item["NAME"])
			self.item_description_edit.setPlainText(item["DETAILS"])

			category_name = database_interaction.get_category_name(item["CATEGORY_ID"])
			self.item_category_edit.setCurrentText(category_name.capitalize())

		self.update_selected_descriptors()


	def item_clicked(self):
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


	def item_name_changed(self):
		item_name = self.item_name_edit.toPlainText()
		item_category_name = self.item_category_edit.currentText()

		if item_name and item_category_name:
			self.add_button.setDisabled(False)
			self.edit_button.setDisabled(False)
		else:
			self.add_button.setDisabled(True)
			self.edit_button.setDisabled(True)


	def item_category_changed(self):
		item_name = self.item_name_edit.toPlainText()
		item_category_name = self.item_category_edit.currentText()

		if item_name and item_category_name:
			self.add_button.setDisabled(False)
			self.edit_button.setDisabled(False)
		else:
			self.add_button.setDisabled(True)
			self.edit_button.setDisabled(True)

		if item_category_name:
			if self.selected_mode == "add" or self.selected_mode == "edit":
				self.item_property_label.setDisabled(False)
				self.item_property_edit.setDisabled(False)
		else:
			self.item_property_label.setDisabled(True)
			self.item_property_edit.setDisabled(True)

		self.update_property_list()


	def load_image_clicked(self):
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


	def add_button_clicked(self):
		item_id = database_interaction.add_item(
			self.item_name_edit.toPlainText(),
			self.item_category_edit.currentText(),
			self.chosen_image_filename,
			self.item_description_edit.toPlainText(),
			self.item_property_edit.get_checked_checkbox_ids()
		)

		button = self.list_widget.create_button(item_id, self.item_name_edit.toPlainText())
		button.clicked.connect(self.item_clicked)
		self.set_item_info()


	def edit_button_clicked(self):
		database_interaction.edit_item(
			self.selected_item_id,
			self.item_name_edit.toPlainText(),
			self.item_category_edit.currentText(),
			self.chosen_image_filename,
			self.item_description_edit.toPlainText(),
			self.item_property_edit.get_checked_checkbox_ids()
		)

		self.list_widget.rename_button(self.selected_item_id, self.item_name_edit.toPlainText())


	def remove_button_clicked(self):
		database_interaction.remove_item(self.selected_item_id)

		self.set_item_info()
		self.list_widget.delete_button(self.selected_item_id)




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