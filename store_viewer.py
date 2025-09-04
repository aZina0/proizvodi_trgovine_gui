from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
import database_interaction
from helper_classes import *



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


class Window(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setMinimumSize(850, 500)
		self.setWindowTitle("Preglednik proizvoda")
		self.setWindowIcon(QIcon("resources/settings.png"))

		self.base_widget = QWidget(self)
		self.base_widget.setLayout(QGridLayout())
		self.base_widget.layout().setContentsMargins(0, 0, 0, 0)
		self.base_widget.layout().setRowStretch(0, 1)
		self.base_widget.layout().setColumnStretch(0, 1)
		self.setCentralWidget(self.base_widget)

		self.show()



class ItemViewer(QWidget):
	def __init__(self, parent):
		super().__init__(parent)

		layout = QGridLayout()
		layout.setColumnStretch(0, 1)
		layout.setColumnStretch(1, 5)
		layout.setRowStretch(1, 1)
		self.setLayout(layout)

		self.setStyleSheet(
			"""
			QPushButton {
				font-size: 13pt;
				height: 30;
			}
			"""
		)


		# kategorije
		self.category_widget = QWidget()
		self.category_widget.setLayout(QVBoxLayout())
		self.category_widget.layout().setContentsMargins(0, 0, 0, 0)
		self.category_title = QLabel("<b>Kategorija</b>")
		self.category_edit = QComboBox()
		self.category_edit.currentTextChanged.connect(self._on_category_changed)

		self.category_widget.layout().addWidget(self.category_title)
		self.category_widget.layout().addWidget(self.category_edit)
		layout.addWidget(self.category_widget, 0, 0)


		# svojstva
		self.property_group = QWidget()
		self.property_group.setLayout(QVBoxLayout())
		self.property_group.layout().setContentsMargins(0, 0, 0, 0)
		self.property_title = QLabel("<b>Svojstva</b>")
		self.property_edit = FoldableSectionsCheckboxesScrollList()
		self.property_edit.checkboxes_changed.connect(self.refresh_items)
		self.property_group.layout().addWidget(self.property_title)
		self.property_group.layout().addWidget(self.property_edit)
		layout.addWidget(self.property_group, 1, 0)


		# items
		self.items = QWidget()
		self.items.setLayout(QGridLayout())
		self.items.layout().setColumnStretch(0, 1)
		self.items.layout().setColumnStretch(1, 1)
		self.items.layout().setColumnStretch(2, 1)
		self.items.layout().setColumnStretch(3, 1)
		self.items.layout().setContentsMargins(0, 0, 0, 0)
		self.scroll_area = QScrollArea()
		self.scroll_area.setWidgetResizable(True)
		self.scroll_area.setWidget(self.items)
		self.scroll_area.setFrameStyle(0)
		layout.addWidget(self.scroll_area, 0, 1, 2, 1)


		for category in database_interaction.get_categories():
			category_name = category["NAME"]
			self.category_edit.addItem(category_name.capitalize())

		self.selected_category = -1
		self.category_edit.setCurrentIndex(self.selected_category)



	def _on_category_changed(self):
		category_name = self.category_edit.currentText()

		if category_name:
			self.property_group.setDisabled(False)
			self.selected_category = database_interaction.get_category_id(category_name)
		else:
			self.property_group.setDisabled(True)
			self.selected_category = -1

		self.update_property_list()
		self.refresh_items()



	def update_property_list(self):
		self.property_edit.clear()

		if self.selected_category:
			# Dodaj iznova svojstva i grupe svojstava iz baze podataka
			for property in database_interaction.get_properties(self.selected_category):
				descriptors = []

				for descriptor in database_interaction.get_descriptors(property["ID"]):
					descriptor_id = descriptor["ID"]
					descriptor_name = descriptor["NAME"]
					descriptors.append(
						{"ID": descriptor_id, "NAME": descriptor_name.capitalize()}
					)

				self.property_edit.add_section(property["NAME"], descriptors)


	def refresh_items(self):
		# izbrisi stare proizvode
		while self.items.layout().count() > 0:
			item = self.items.layout().itemAt(0).widget()
			self.items.layout().removeWidget(item)
			item.deleteLater()

		if self.selected_category > -1:
			column = 0
			row = 0
			for item in database_interaction.get_items_from_category_with_descriptors(self.selected_category, self.property_edit.get_checked_checkbox_ids()):
				if column >= 4:
					column = 0
					row += 1

				item_frame = QFrame()
				item_frame.setFixedSize(150, 230)
				item_frame.setLineWidth(1)
				item_frame.setMidLineWidth(1)
				item_frame.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
				item_frame.setLayout(QGridLayout())
				item_frame.layout().setContentsMargins(3, 3, 3, 3)

				image = QLabel()
				image.setFixedSize(140, 140)
				image.setScaledContents(True)
				if item['IMAGE']:
					pixmap = QPixmap(f"resources/item_images/{item['IMAGE']}")
					self.chosen_image_filename = item['IMAGE']
				else:
					pixmap = QPixmap(f"resources/item_images/no_image.png")
					self.chosen_image_filename = ""
				image.setPixmap(pixmap)
				item_frame.layout().addWidget(image, 0, 0, 1, 2)

				item_name = QLabel(item["NAME"])
				item_name.setWordWrap(True)
				item_frame.layout().addWidget(item_name, 1, 0, 1, 2)

				item_price = QLabel(item["PRICE"] + "€")
				item_price.setAlignment(Qt.AlignCenter)
				item_price.setStyleSheet("font-size: 17px")
				item_frame.layout().addWidget(item_price, 2, 0)

				button = QPushButton("Kupi")
				button.setStyleSheet("""
					font-size: 15px;
					padding: 0px 10px;
					height: 25;
					background-color: #008900;
					color: #FFFFFF;
				""")
				item_frame.layout().addWidget(button, 2, 1)


				self.items.layout().addWidget(item_frame, row, column, alignment=Qt.AlignCenter | Qt.AlignTop)

				column += 1



window = Window()
item_viewer = ItemViewer(window)

window.base_widget.layout().addWidget(item_viewer, 0, 0)




app.exec()