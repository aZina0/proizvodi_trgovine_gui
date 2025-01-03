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



def initialize():
	with connection:
		# Napravi tablicu kategorije i umetni nekoliko kategorija
		connection.execute("""
			CREATE TABLE CATEGORIES
			(ID INTEGER PRIMARY KEY, NAME VARCHAR);
		""")

		odjeca_category_id = add_category("odjeća")
		pice_category_id = add_category("piće")
		add_category("ostalo")

		# Napravi tablicu grupa svojstava
		connection.execute("""
			CREATE TABLE PROPERTIES
			(ID INTEGER PRIMARY KEY, NAME VARCHAR, CATEGORY_ID INT);
		""")

		# Umetni grupe svojstava za odjecu (boja, materijal, spol)
		odjeca_boja_property_id = add_property(odjeca_category_id, "boja")
		odjeca_materijal_property_id = add_property(odjeca_category_id, "materijal")
		odjeca_spol_property_id = add_property(odjeca_category_id, "spol")

		# Umetni grupe svojstava za pica (vrsta, ambalaza)
		pice_vrsta_property_id = add_property(pice_category_id, "vrsta")
		pice_ambalaza_property_id = add_property(pice_category_id, "ambalaža")


		# Napravi tablicu specificnih svojstava
		connection.execute("""
			CREATE TABLE DESCRIPTORS
			(ID INTEGER PRIMARY KEY, NAME VARCHAR, PROPERTY_ID INT);
		""")

		# Umetni specificna svojstva za boju (crvena, crna, bijela)
		add_descriptor(odjeca_boja_property_id, "crvena")
		add_descriptor(odjeca_boja_property_id, "crna")
		add_descriptor(odjeca_boja_property_id, "bijela")

		# Umetni specificna svojstva za materijal (pamuk, poliester)
		add_descriptor(odjeca_materijal_property_id, "pamuk")
		add_descriptor(odjeca_materijal_property_id, "poliester")

		# Umetni specificna svojstva za spol (muski, zenski)
		add_descriptor(odjeca_spol_property_id, "muški")
		add_descriptor(odjeca_spol_property_id, "ženski")

		# Umetni specificna svojstva za vrstu pica (gazirano, alkoholno)
		add_descriptor(pice_vrsta_property_id, "gazirano")
		add_descriptor(pice_vrsta_property_id, "alkoholno")

		# Umetni specificna svojstva za ambalazu (boca, tetrapak)
		add_descriptor(pice_ambalaza_property_id, "boca")
		add_descriptor(pice_ambalaza_property_id, "tetrapak")



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



def get_category_id(category_name):
	category_name = category_name.lower()

	with connection:
		result = connection.execute(f"""
			SELECT category.ID FROM CATEGORIES AS category
			WHERE category.NAME="{category_name}";
		""")

	return result[0][0]


def get_category_name(category_id):
	with connection:
		result = connection.execute(f"""
			SELECT category.NAME FROM CATEGORIES AS category
			WHERE category.ID={category_id};
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
	category_id = -1

	with connection:
		result = connection.execute(f"""
			INSERT INTO CATEGORIES (NAME)
			VALUES ("{category_name}")
			RETURNING ID;
		""")

		category_id = result[0][0]

	return category_id


def rename_category(category_id, new_category_name):
	new_category_name = new_category_name.lower()

	with connection:
		connection.execute(f"""
			UPDATE CATEGORIES AS category
			SET NAME="{new_category_name}"
			WHERE category.ID={category_id};
		""")


def remove_category(category_id):
	with connection:
		for property in get_properties(category_id):
			property_id = property["ID"]

			connection.execute(f"""
				DELETE
				FROM DESCRIPTORS
				WHERE PROPERTY_ID={property_id};
			""")

		connection.execute(f"""
			DELETE
			FROM PROPERTIES
			WHERE CATEGORY_ID={category_id};
		""")

		connection.execute(f"""
			DELETE
			FROM CATEGORIES
			WHERE ID={category_id};
		""")



def get_properties(category_id):
	properties = []

	with connection:
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


def property_exists(category_id, property_name):
	property_name = property_name.lower()

	with connection:
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


def add_property(category_id, property_name):
	property_name = property_name.lower()
	property_id = -1

	with connection:
		result = connection.execute(f"""
			INSERT INTO PROPERTIES (NAME, CATEGORY_ID)
			VALUES ("{property_name}", {category_id})
			RETURNING ID;
		""")

		property_id = result[0][0]

	return property_id


def rename_property(property_id, new_property_name):
	new_property_name = new_property_name.lower()

	with connection:
		connection.execute(f"""
			UPDATE PROPERTIES
			SET NAME="{new_property_name}"
			WHERE ID={property_id};
		""")


def remove_property(property_id):
	with connection:
		connection.execute(f"""
			DELETE
			FROM DESCRIPTORS
			WHERE PROPERTY_ID={property_id};
		""")

		connection.execute(f"""
			DELETE
			FROM PROPERTIES
			WHERE ID={property_id};
		""")



def get_descriptors(property_id):
	descriptors = []

	with connection:
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


def descriptor_exists(property_id, descriptor_name):
	descriptor_name = descriptor_name.lower()

	with connection:
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


def add_descriptor(property_id, descriptor_name):
	descriptor_name = descriptor_name.lower()
	descriptor_id = -1

	with connection:
		result = connection.execute(f"""
			INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID)
			VALUES ("{descriptor_name}", {property_id})
			RETURNING ID;
		""")

		descriptor_id = result[0][0]

	return descriptor_id


def rename_descriptor(descriptor_id, new_descriptor_name):
	new_descriptor_name = new_descriptor_name.lower()

	with connection:
		connection.execute(f"""
			UPDATE DESCRIPTORS AS descriptor
			SET NAME="{new_descriptor_name}"
			WHERE descriptor.ID={descriptor_id};
		""")


def remove_descriptor(descriptor_id):
	with connection:
		connection.execute(f"""
			DELETE
			FROM DESCRIPTORS
			WHERE ID={descriptor_id};
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


def get_item_descriptors(item_id):
	descriptor_ids = []

	with connection:
		result = connection.execute(f"""
			SELECT DESCRIPTOR_ID
			FROM ITEM_DESCRIPTORS
			WHERE ITEM_ID={item_id};
		""")

		for descriptor in result:
			descriptor_ids.append(descriptor[0])

	return descriptor_ids