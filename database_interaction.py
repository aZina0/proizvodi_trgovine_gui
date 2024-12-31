import sqlite3



class ConnectionManager():
	def __init__(self):
		self.database_filename = "database.db"
		self.active = False
		self.connection = None
		self.level = 0


	def __enter__(self):
		if not self.active:
			self.connection = sqlite3.connect(self.database_filename)
			self.active = True

		self.level += 1


	def __exit__(self, exception_type, exception_value, traceback):
		if self.level > 0:
			self.level -= 1

		if self.level == 0:
			self.connection.close()
			self.active = False


	def execute(self, query):
		if not self.active:
			raise Exception("No active connection.")

		cursor = self.connection.cursor()
		cursor.execute(query)
		result = cursor.fetchall()
		cursor.close()
		self.connection.commit()

		return result


	def execute_and_return_col_names(self, query):
		if not self.active:
			raise Exception("No active connection.")

		cursor = self.connection.cursor()
		cursor.execute(query)
		result = cursor.fetchall()
		col_names = [column[0] for column in cursor.description]
		cursor.close()
		self.connection.commit()

		return result, col_names


connection = ConnectionManager()




def get_category_id(category_name):
	category_name = category_name.lower()

	with connection:
		result = connection.execute(f"""
			SELECT category.ID FROM CATEGORIES AS category
			WHERE category.NAME="{category_name}";
		""")

	return result[0][0]


def get_property_id(category_name, property_name):
	category_name = category_name.lower()
	property_name = property_name.lower()

	category_id = get_category_id(category_name)

	with connection:
		result = connection.execute(f"""
			SELECT property.ID FROM PROPERTIES AS property
			WHERE property.CATEGORY_ID={category_id}
			and property.NAME="{property_name}";
		""")

	return result[0][0]


def get_descriptor_id(category_name, property_name, descriptor_name):
	category_name = category_name.lower()
	property_name = property_name.lower()
	descriptor_name = descriptor_name.lower()

	property_id = get_property_id(category_name, property_name)

	with connection:
		result = connection.execute(f"""
			SELECT descriptor.ID FROM DESCRIPTORS AS descriptor
			WHERE descriptor.PROPERTY_ID={property_id}
			and descriptor.NAME="{descriptor_name}";
		""")

	return result[0][0]



def initialize():
	with connection:
		# Napravi tablicu kategorije i umetni nekoliko kategorija
		connection.execute("""
			CREATE TABLE CATEGORIES
			(ID INTEGER PRIMARY KEY, NAME VARCHAR);
		""")

		add_category("odjeća")
		add_category("piće")

		# Napravi tablicu grupa svojstava
		connection.execute("""
			CREATE TABLE PROPERTIES
			(ID INTEGER PRIMARY KEY, NAME VARCHAR, CATEGORY_ID INT);
		""")

		# Umetni grupe svojstava za odjecu (boja, materijal, spol)
		add_property("odjeća", "boja")
		add_property("odjeća", "materijal")
		add_property("odjeća", "spol")

		# Umetni grupe svojstava za pica (vrsta, ambalaza)
		add_property("piće", "vrsta")
		add_property("piće", "ambalaža")


		# Napravi tablicu specificnih svojstava
		connection.execute("""
			CREATE TABLE DESCRIPTORS
			(ID INTEGER PRIMARY KEY, NAME VARCHAR, PROPERTY_ID INT);
		""")

		# Umetni specificna svojstva za boju (crvena, crna, bijela)
		add_descriptor("odjeća", "boja", "crvena")
		add_descriptor("odjeća", "boja", "crna")
		add_descriptor("odjeća", "boja", "bijela")

		# Umetni specificna svojstva za materijal (pamuk, poliester)
		add_descriptor("odjeća", "materijal", "pamuk")
		add_descriptor("odjeća", "materijal", "poliester")

		# Umetni specificna svojstva za spol (muski, zenski)
		add_descriptor("odjeća", "spol", "muški")
		add_descriptor("odjeća", "spol", "ženski")

		# Umetni specificna svojstva za vrstu pica (gazirano, alkoholno)
		add_descriptor("piće", "vrsta", "gazirano")
		add_descriptor("piće", "vrsta", "alkoholno")

		# Umetni specificna svojstva za ambalazu (boca, tetrapak)
		add_descriptor("piće", "ambalaža", "boca")
		add_descriptor("piće", "ambalaža", "tetrapak")



		connection.execute("""
			CREATE TABLE ITEMS
			(ID INTEGER PRIMARY KEY, NAME VARCHAR, CATEGORY_ID INT, IMAGE VARCHAR, DETAILS VARCHAR);
		""")

		connection.execute("""
			CREATE TABLE ITEM_DESCRIPTORS
			(ITEM_ID INT, DESCRIPTOR_ID INT);
		""")


		add_item(
			name="Nike WOW hlače",
			category_name="odjeća",
			details="Ove hlače su uistinu WOW.",
			properties_descriptors=[
				("boja", "crna"),
				("boja", "crvena"),
				("materijal", "pamuk"),
				("spol", "muški"),
			]
		)
		add_item(
			name="Adidas majica sa kapuljačom DELUXE",
			category_name="odjeća",
			details="Ova bijela unisex majica ima kapuljaču. Baš je DELUXE",
			properties_descriptors=[
				("boja", "bijela"),
				("materijal", "poliester"),
				("spol", "muški"),
				("spol", "ženski"),
			]
		)
		add_item(
			name="UMBRO kapa",
			category_name="odjeća",
			details="Ova kapa se nosi na glavi.",
		)

		add_item(
			name="Z bregov Trajno mlijeko 2,8% m.m. 1L",
			category_name="piće",
			details="Sterilizirano, homogenizirano mlijeko s 2,8% mliječne masti.",
			properties_descriptors=[
				("ambalaža", "tetrapak"),
			]
		)
		add_item(
			name="Coca Cola 2 l",
			category_name="piće",
			image="coca_cola.jpg",
			details=(
				"Coca-Cola je najpopularnije i najprodavanije bezalkoholno piće u povijesti, "
				"kao i jedan od najprepoznatljivijih brendova na svijetu. "
				"Kreirao ga je dr. John S. Pemberton 1886. godine u Atlanti, država Georgia. "
				"U početku se točio kao mješavina Coca-Cola sirupa i gazirane vode u apoteci "
				"'Jacob's Pharmacy'. Coca-Cola napitak je patentiran 1887. godine, registriran "
				"kao zaštitni znak 1893., a do 1895. godine nalazi se u prodaji širom SAD-a. "
				"Originalni okus. Odličan okus. Osvježavajuće. Odlično ide uz hranu. "
				"Podiže raspoloženje. "
			),
			properties_descriptors=[
				("vrsta", "gazirano"),
				("ambalaža", "boca"),
			]
		)



def get_categories():
	categories = []

	with connection:
		result, col_names = connection.execute_and_return_col_names("""
			SELECT *
			FROM CATEGORIES AS category;
		""")

		for row in result:
			category = {}
			for column_name, cell in zip(col_names, row):
				category[column_name] = cell
			categories.append(category)

	return categories


def category_exists(category_name):
	category_name = category_name.lower()

	with connection:
		result = connection.execute(f"""
			SELECT *
			FROM CATEGORIES AS category
			WHERE category.NAME="{category_name}";
		""")

	if len(result) > 0:
		return True
	else:
		return False


def add_category(category_name):
	category_name = category_name.lower()

	with connection:
		connection.execute(f"""
			INSERT INTO CATEGORIES (NAME)
			VALUES ("{category_name}");
		""")


def rename_category(current_category_name, new_category_name):
	current_category_name = current_category_name.lower()
	new_category_name = new_category_name.lower()

	with connection:
		category_id = get_category_id(current_category_name)

		connection.execute(f"""
			UPDATE CATEGORIES AS category
			SET NAME="{new_category_name}"
			WHERE category.ID={category_id};
		""")


def remove_category(category_name):
	category_name = category_name.lower()

	with connection:
		for property in get_properties(category_name):
			property_id = get_property_id(category_name, property["NAME"])

			connection.execute(f"""
				DELETE
				FROM DESCRIPTORS
				WHERE PROPERTY_ID={property_id};
			""")

		category_id = get_category_id(category_name)
		connection.execute(f"""
			DELETE
			FROM PROPERTIES
			WHERE CATEGORY_ID={category_id};
		""")

		connection.execute(f"""
			DELETE
			FROM CATEGORIES
			WHERE NAME="{category_name}";
		""")



def get_properties(category_name):
	category_name = category_name.lower()
	properties = []

	with connection:
		category_id = get_category_id(category_name)

		result, col_names = connection.execute_and_return_col_names(f"""
			SELECT *
			FROM PROPERTIES AS property
			WHERE property.CATEGORY_ID={category_id};
		""")

		for row in result:
			property = {}
			for column_name, cell in zip(col_names, row):
				property[column_name] = cell
			properties.append(property)

	return properties


def property_exists(category_name, property_name):
	category_name = category_name.lower()
	property_name = property_name.lower()

	with connection:
		category_id = get_category_id(category_name)

		result = connection.execute(f"""
			SELECT *
			FROM PROPERTIES AS property
			WHERE property.NAME="{property_name}"
			AND property.CATEGORY_ID={category_id};
		""")

	if len(result) > 0:
		return True
	else:
		return False


def add_property(category_name, property_name):
	category_name = category_name.lower()
	property_name = property_name.lower()

	with connection:
		category_id = get_category_id(category_name)

		connection.execute(f"""
			INSERT INTO PROPERTIES (NAME, CATEGORY_ID)
			VALUES ("{property_name}", {category_id});
		""")


def rename_property(category_name, current_property_name, new_property_name):
	category_name = category_name.lower()
	current_property_name = current_property_name.lower()
	new_property_name = new_property_name.lower()

	with connection:
		category_id = get_category_id(category_name)

		connection.execute(f"""
			UPDATE PROPERTIES AS property
			SET NAME="{new_property_name}"
			WHERE property.NAME="{current_property_name}"
			AND property.CATEGORY_ID={category_id};
		""")


def remove_property(category_name, property_name):
	category_name = category_name.lower()
	property_name = property_name.lower()

	with connection:
		property_id = get_property_id(category_name, property_name)
		connection.execute(f"""
			DELETE
			FROM DESCRIPTORS
			WHERE PROPERTY_ID={property_id};
		""")

		category_id = get_category_id(category_name)
		connection.execute(f"""
			DELETE
			FROM PROPERTIES AS property
			WHERE property.NAME="{property_name}"
			AND property.CATEGORY_ID={category_id};
		""")



def get_descriptors(category_name, property_name):
	category_name = category_name.lower()
	property_name = property_name.lower()
	descriptors = []

	with connection:
		property_id = get_property_id(category_name, property_name)

		result, col_names = connection.execute_and_return_col_names(f"""
			SELECT *
			FROM DESCRIPTORS AS descriptor
			WHERE descriptor.PROPERTY_ID={property_id};
		""")

		for row in result:
			descriptor = {}
			for column_name, cell in zip(col_names, row):
				descriptor[column_name] = cell
			descriptors.append(descriptor)

	return descriptors


def descriptor_exists(category_name, property_name, descriptor_name):
	category_name = category_name.lower()
	property_name = property_name.lower()
	descriptor_name = descriptor_name.lower()

	with connection:
		property_id = get_property_id(category_name, property_name)

		result = connection.execute(f"""
			SELECT *
			FROM DESCRIPTORS AS descriptor
			WHERE descriptor.NAME="{descriptor_name}"
			AND descriptor.PROPERTY_ID={property_id};
		""")

	if len(result) > 0:
		return True
	else:
		return False


def add_descriptor(category_name, property_name, descriptor_name):
	category_name = category_name.lower()
	property_name = property_name.lower()
	descriptor_name = descriptor_name.lower()

	with connection:
		property_id = get_property_id(category_name, property_name)

		connection.execute(f"""
			INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID)
			VALUES ("{descriptor_name}", {property_id});
		""")


def rename_descriptor(category_name, property_name, current_descriptor_name, new_descriptor_name):
	category_name = category_name.lower()
	property_name = property_name.lower()
	current_descriptor_name = current_descriptor_name.lower()
	new_descriptor_name = new_descriptor_name.lower()

	with connection:
		property_id = get_property_id(category_name, property_name)

		connection.execute(f"""
			UPDATE DESCRIPTORS AS descriptor
			SET NAME="{new_descriptor_name}"
			WHERE descriptor.NAME="{current_descriptor_name}"
			AND descriptor.PROPERTY_ID={property_id};
		""")


def remove_descriptor(category_name, property_name, descriptor_name):
	category_name = category_name.lower()
	property_name = property_name.lower()
	descriptor_name = descriptor_name.lower()

	with connection:
		property_id = get_property_id(category_name, property_name)

		connection.execute(f"""
			DELETE
			FROM DESCRIPTORS AS descriptor
			WHERE descriptor.NAME="{descriptor_name}"
			AND descriptor.PROPERTY_ID={property_id};
		""")



def get_items():
	items = []

	with connection:
		result, col_names = connection.execute_and_return_col_names(f"""
			SELECT *
			FROM ITEMS;
		""")

		for row in result:
			item = {}
			for column_name, cell in zip(col_names, row):
				item[column_name] = cell
			items.append(item)

	return items


def get_item(item_id):
	item = {}

	with connection:
		result, col_names = connection.execute_and_return_col_names(f"""
			SELECT *
			FROM ITEMS AS item
			WHERE item.ID={item_id};
		""")

		for column_name, cell in zip(col_names, result[0]):
			item[column_name] = cell

	return item


def add_item(
	name,
	category_name,
	image = "",
	details = "",
	properties_descriptors = []
):

	item_id = -1
	with connection:
		category_id = get_category_id(category_name)

		result = connection.execute(f"""
			INSERT INTO ITEMS (NAME, CATEGORY_ID, IMAGE, DETAILS)
			VALUES ("{name}", {category_id}, "{image}", "{details}")
			RETURNING ID;
		""")
		item_id = result[0][0]

		for property_descriptor in properties_descriptors:
			property_name = property_descriptor[0]
			descriptor_name = property_descriptor[1]
			descriptor_id = get_descriptor_id(
				category_name,
				property_name,
				descriptor_name
			)

			connection.execute(f"""
				INSERT INTO ITEM_DESCRIPTORS (ITEM_ID, DESCRIPTOR_ID)
				VALUES ({item_id}, {descriptor_id})
			""")

	return item_id