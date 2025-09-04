from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *


# Scrollable widget koji sadrzi sekcije checkboxeva,
# sekcije je moguce foldati
class FoldableSectionsCheckboxesScrollList(QScrollArea):
	checkboxes_changed = Signal()

	def __init__(self):
		super().__init__()

		self.setStyleSheet("""
			QToolButton {
				font-size: 10pt;
				text-align: left;
			}

			QCheckBox::indicator {
				margin-left: 20px;
				border: 1px solid #9B9B9B;
				border-radius: 1px;
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


	# Dodaj sekciju checkboxeva
	def add_section(self, section_name, checkbox_infos):
		section_button = QToolButton()
		section_button.setArrowType(Qt.RightArrow)
		section_button.setText(section_name)
		section_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		section_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		section_button.clicked.connect(self._on_section_clicked)
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
			checkbox.checkStateChanged.connect(self.checkbox_changed)
			if self.disabled:
				checkbox.setDisabled(True)
			self.checkboxes[checkbox_id] = checkbox
			checkboxes_widget.layout().addWidget(checkbox)

		self.base_widget.layout().addWidget(checkboxes_widget)


	# Isprazni widget
	def clear(self):
		while self.base_widget.layout().count() > 0:
			widget = self.base_widget.layout().itemAt(0).widget()
			self.base_widget.layout().removeWidget(widget)
			widget.deleteLater()

		self.section_widgets.clear()
		self.checkboxes.clear()


	def _on_section_clicked(self):
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


	def checkbox_changed(self):
		self.checkboxes_changed.emit()


	def setDisabled(self, state):
		# Ako disable, samo disableaj interakciju s checkboxevima (dozvoli scrollanje)
		if state:
			self.disabled = True
			super().setDisabled(False)
			for checkbox in self.checkboxes.values():
				checkbox.setDisabled(True)

		# Inace ako enable, omoguci sve
		else:
			self.disabled = False
			super().setDisabled(False)
			for checkbox in self.checkboxes.values():
				checkbox.setDisabled(False)


	# Ugrabi sve id koji su checked
	def get_checked_checkbox_ids(self):
		checked_checkbox_ids = []

		for id in self.checkboxes:
			checkbox = self.checkboxes[id]
			if checkbox.checkState() == Qt.Checked:
				checked_checkbox_ids.append(id)

		return checked_checkbox_ids