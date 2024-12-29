import sqlite3


database_filename="database.db"



def get_category_id(cursor, category_name):
	category_name = category_name.lower()

	cursor.execute(f"""
		SELECT category.ID FROM CATEGORIES AS category
		WHERE category.NAME="{category_name}";
	""")
	return cursor.fetchone()[0]


def get_property_id(cursor, category_name, property_name):
	category_name = category_name.lower()
	property_name = property_name.lower()

	category_id = get_category_id(cursor, category_name)

	cursor.execute(f"""
		SELECT property.ID FROM PROPERTIES AS property
		WHERE property.CATEGORY_ID={category_id}
		and property.NAME="{property_name}";
	""")
	return cursor.fetchone()[0]



def initialize():
	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		# Napravi tablicu kategorije i umetni nekoliko kategorija
		cursor.execute("""
			CREATE TABLE CATEGORIES
			(ID INTEGER PRIMARY KEY, NAME VARCHAR);
		""")
		conn.commit()

		add_category("odjeća")
		add_category("piće")


		# Napravi tablicu grupa svojstava
		cursor.execute("""
			CREATE TABLE PROPERTIES
			(ID INTEGER PRIMARY KEY, NAME VARCHAR, CATEGORY_ID INT);
		""")
		conn.commit()

		# Umetni grupe svojstava za odjecu (boja, materijal, spol)
		add_property("odjeća", "boja")
		add_property("odjeća", "materijal")
		add_property("odjeća", "spol")

		# Umetni grupe svojstava za pica (vrsta, ambalaza)
		add_property("piće", "vrsta")
		add_property("piće", "ambalaža")


		# Napravi tablicu specificnih svojstava
		cursor.execute("""
			CREATE TABLE DESCRIPTORS
			(ID INTEGER PRIMARY KEY, NAME VARCHAR, PROPERTY_ID INT);
		""")
		conn.commit()

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



		cursor.execute("""
			CREATE TABLE ITEMS
			(ID INTEGER PRIMARY KEY, NAME VARCHAR, CATEGORY_ID INT, IMAGE VARCHAR, DETAILS VARCHAR);
		""")
		conn.commit()

		cursor.execute("""
			CREATE TABLE ITEM_DESCRIPTORS
			(ITEM_ID INT, DESCRIPTOR_ID INT);
		""")
		conn.commit()


		add_item(
			name="Nike WOW hlače",
			category_name="odjeća",
			details="Ove hlače su uistinu WOW.",
			descriptor_names=["crna", "crvena", "pamuk", "muški"]
		)
		add_item(
			name="Adidas majica sa kapuljačom DELUXE",
			category_name="odjeća",
			details="Ova bijela unisex majica ima kapuljaču. Baš je DELUXE",
			descriptor_names=["bijela", "poliester", "muški", "ženski"]
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
			descriptor_names=["tetrapak"]
		)
		add_item(
			name="Coca Cola 2 l",
			category_name="piće",
			details=(
				"Coca-Cola je najpopularnije i najprodavanije bezalkoholno piće u povijesti, "
				"kao i jedan od najprepoznatljivijih brendova na svijetu."
				"Kreirao ga je dr. John S. Pemberton 1886. godine u Atlanti, država Georgia."
				"U početku se točio kao mješavina Coca-Cola sirupa i gazirane vode u apoteci "
				"'Jacob's Pharmacy'. Coca-Cola napitak je patentiran 1887. godine, registriran "
				"kao zaštitni znak 1893., a do 1895. godine nalazi se u prodaji širom SAD-a."
				"Originalni okus. Odličan okus. Osvježavajuće. Odlično ide uz hranu."
				"Podiže raspoloženje."
			),
			descriptor_names=["gazirano", "boca"]
		)



def get_categories():
	categories = []

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		cursor.execute("""
			SELECT *
			FROM CATEGORIES AS category;
		""")
		column_names = [column[0] for column in cursor.description]
		data = cursor.fetchall()

		for row in data:
			category = {}
			for column_name, cell in zip(column_names, row):
				category[column_name] = cell
			categories.append(category)

		conn.commit()

	return categories


def category_exists(category_name):
	category_name = category_name.lower()
	categories = []

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		cursor.execute(f"""
			SELECT *
			FROM CATEGORIES AS category
			WHERE category.NAME="{category_name}";
		""")
		categories = [i[0] for i in cursor.fetchall()]

		conn.commit()

	if len(categories) > 0:
		return True
	else:
		return False


def add_category(category_name):
	category_name = category_name.lower()

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		cursor.execute(f"""
			INSERT INTO CATEGORIES (NAME)
			VALUES ("{category_name}");
		""")

		conn.commit()


def rename_category(current_category_name, new_category_name):
	current_category_name = current_category_name.lower()
	new_category_name = new_category_name.lower()

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		category_id = get_category_id(cursor, current_category_name)

		cursor.execute(f"""
			UPDATE CATEGORIES AS category
			SET NAME="{new_category_name}"
			WHERE category.ID={category_id};
		""")

		conn.commit()


def remove_category(category_name):
	category_name = category_name.lower()

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		for property_name in get_properties(category_name):
			property_id = get_property_id(cursor, category_name, property_name)

			cursor.execute(f"""
				DELETE
				FROM DESCRIPTORS
				WHERE PROPERTY_ID={property_id};
			""")

		category_id = get_category_id(cursor, category_name)
		cursor.execute(f"""
			DELETE
			FROM PROPERTIES
			WHERE CATEGORY_ID={category_id};
		""")

		cursor.execute(f"""
			DELETE
			FROM CATEGORIES
			WHERE NAME="{category_name}";
		""")

		conn.commit()



def get_properties(category_name):
	category_name = category_name.lower()
	properties = []

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		category_id = get_category_id(cursor, category_name)

		cursor.execute(f"""
			SELECT *
			FROM PROPERTIES AS property
			WHERE property.CATEGORY_ID={category_id};
		""")
		column_names = [column[0] for column in cursor.description]
		data = cursor.fetchall()

		for row in data:
			property = {}
			for column_name, cell in zip(column_names, row):
				property[column_name] = cell
			properties.append(property)

		conn.commit()

	return properties


def property_exists(category_name, property_name):
	category_name = category_name.lower()
	property_name = property_name.lower()
	properties = []

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		category_id = get_category_id(cursor, category_name)

		cursor.execute(f"""
			SELECT *
			FROM PROPERTIES AS property
			WHERE property.NAME="{property_name}"
			AND property.CATEGORY_ID={category_id};
		""")
		properties = [i[0] for i in cursor.fetchall()]

		conn.commit()

	if len(properties) > 0:
		return True
	else:
		return False


def add_property(category_name, property_name):
	category_name = category_name.lower()
	property_name = property_name.lower()

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		category_id = get_category_id(cursor, category_name)

		cursor.execute(f"""
			INSERT INTO PROPERTIES (NAME, CATEGORY_ID)
			VALUES ("{property_name}", {category_id});
		""")

		conn.commit()


def rename_property(category_name, current_property_name, new_property_name):
	category_name = category_name.lower()
	current_property_name = current_property_name.lower()
	new_property_name = new_property_name.lower()

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		category_id = get_category_id(cursor, category_name)

		cursor.execute(f"""
			UPDATE PROPERTIES AS property
			SET NAME="{new_property_name}"
			WHERE property.NAME="{current_property_name}"
			AND property.CATEGORY_ID={category_id};
		""")

		conn.commit()


def remove_property(category_name, property_name):
	category_name = category_name.lower()
	property_name = property_name.lower()

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		property_id = get_property_id(cursor, category_name, property_name)
		cursor.execute(f"""
			DELETE
			FROM DESCRIPTORS
			WHERE PROPERTY_ID={property_id};
		""")

		category_id = get_category_id(cursor, category_name)
		cursor.execute(f"""
			DELETE
			FROM PROPERTIES AS property
			WHERE property.NAME="{property_name}"
			AND property.CATEGORY_ID={category_id};
		""")

		conn.commit()



def get_descriptors(category_name, property_name):
	category_name = category_name.lower()
	property_name = property_name.lower()
	descriptors = []

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		property_id = get_property_id(cursor, category_name, property_name)

		cursor.execute(f"""
			SELECT *
			FROM DESCRIPTORS AS descriptor
			WHERE descriptor.PROPERTY_ID={property_id};
		""")
		column_names = [column[0] for column in cursor.description]
		data = cursor.fetchall()

		for row in data:
			descriptor = {}
			for column_name, cell in zip(column_names, row):
				descriptor[column_name] = cell
			descriptors.append(descriptor)

		conn.commit()

	return descriptors


def descriptor_exists(category_name, property_name, descriptor_name):
	category_name = category_name.lower()
	property_name = property_name.lower()
	descriptor_name = descriptor_name.lower()
	descriptors = []

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		property_id = get_property_id(cursor, category_name, property_name)

		cursor.execute(f"""
			SELECT *
			FROM DESCRIPTORS AS descriptor
			WHERE descriptor.NAME="{descriptor_name}"
			AND descriptor.PROPERTY_ID={property_id};
		""")
		descriptors = [i[0] for i in cursor.fetchall()]

		conn.commit()

	if len(descriptors) > 0:
		return True
	else:
		return False


def add_descriptor(category_name, property_name, descriptor_name):
	category_name = category_name.lower()
	property_name = property_name.lower()
	descriptor_name = descriptor_name.lower()

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		property_id = get_property_id(cursor, category_name, property_name)

		cursor.execute(f"""
			INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID)
			VALUES ("{descriptor_name}", {property_id});
		""")

		conn.commit()


def rename_descriptor(category_name, property_name, current_descriptor_name, new_descriptor_name):
	category_name = category_name.lower()
	property_name = property_name.lower()
	current_descriptor_name = current_descriptor_name.lower()
	new_descriptor_name = new_descriptor_name.lower()

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		property_id = get_property_id(cursor, category_name, property_name)

		cursor.execute(f"""
			UPDATE DESCRIPTORS AS descriptor
			SET NAME="{new_descriptor_name}"
			WHERE descriptor.NAME="{current_descriptor_name}"
			AND descriptor.PROPERTY_ID={property_id};
		""")

		conn.commit()


def remove_descriptor(category_name, property_name, descriptor_name):
	category_name = category_name.lower()
	property_name = property_name.lower()
	descriptor_name = descriptor_name.lower()

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		property_id = get_property_id(cursor, category_name, property_name)

		cursor.execute(f"""
			DELETE
			FROM DESCRIPTORS AS descriptor
			WHERE descriptor.NAME="{descriptor_name}"
			AND descriptor.PROPERTY_ID={property_id};
		""")

		conn.commit()



def add_item(
	name,
	category_name,
	image = "",
	details = "",
	descriptor_names = []
):

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		category_id = get_category_id(cursor, category_name)

		cursor.execute(f"""
			INSERT INTO ITEMS (NAME, CATEGORY_ID, IMAGE, DETAILS)
			VALUES ("{name}", {category_id}, "{image}", "{details}");
		""")

		conn.commit()