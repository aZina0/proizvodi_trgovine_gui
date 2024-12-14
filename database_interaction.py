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
		WHERE property.CATEGORY_ID="{category_id}"
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

		cursor.execute("""
			INSERT INTO CATEGORIES (NAME)
			VALUES ("odjeća");
		""")
		cursor.execute("""
			INSERT INTO CATEGORIES (NAME)
			VALUES ("piće");
		""")


		# Napravi tablicu grupa svojstava
		cursor.execute("""
			CREATE TABLE PROPERTIES
			(ID INTEGER PRIMARY KEY, NAME VARCHAR, CATEGORY_ID INT);
		""")

		# Umetni grupe svojstava za odjecu (boja, materijal, spol)
		odjeca_category_id = get_category_id(cursor, "odjeća")
		cursor.execute(f"""
			INSERT INTO PROPERTIES (NAME, CATEGORY_ID)
			VALUES ("boja", {odjeca_category_id});
		""")
		cursor.execute(f"""
			INSERT INTO PROPERTIES (NAME, CATEGORY_ID)
			VALUES ("materijal", {odjeca_category_id});
		""")
		cursor.execute(f"""
			INSERT INTO PROPERTIES (NAME, CATEGORY_ID)
			VALUES ("spol", {odjeca_category_id});
		""")

		# Umetni grupe svojstava za pica (vrsta, ambalaza)
		pice_category_id = get_category_id(cursor, "piće")
		cursor.execute(f"""
			INSERT INTO PROPERTIES (NAME, CATEGORY_ID)
			VALUES ("vrsta", {pice_category_id});
		""")
		cursor.execute(f"""
			INSERT INTO PROPERTIES (NAME, CATEGORY_ID)
			VALUES ("ambalaža", {pice_category_id});
		""")


		# Napravi tablicu specificnih svojstava
		cursor.execute("""
			CREATE TABLE DESCRIPTORS
			(ID INTEGER PRIMARY KEY, NAME VARCHAR, PROPERTY_ID INT);
		""")

		# Umetni specificna svojstva za boju (crvena, crna, bijela)
		boja_property_id = get_property_id(cursor, "odjeća", "boja")
		cursor.execute(f"""
			INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID)
			VALUES ("crvena", {boja_property_id});
		""")
		cursor.execute(f"""
			INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID)
			VALUES ("crna", {boja_property_id});
		""")
		cursor.execute(f"""
			INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID)
			VALUES ("bijela", {boja_property_id});
		""")

		# Umetni specificna svojstva za materijal (pamuk, poliester)
		materijal_property_id = get_property_id(cursor, "odjeća", "materijal")
		cursor.execute(f"""
			INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID)
			VALUES ("pamuk", {materijal_property_id});
		""")
		cursor.execute(f"""
			INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID)
			VALUES ("poliester", {materijal_property_id});
		""")

		# Umetni specificna svojstva za spol (muski, zenski, unisex)
		spol_property_id = get_property_id(cursor, "odjeća", "spol")
		cursor.execute(f"""
			INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID)
			VALUES ("muški", {spol_property_id});
		""")
		cursor.execute(f"""
			INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID)
			VALUES ("ženski", {spol_property_id});
		""")
		cursor.execute(f"""
			INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID)
			VALUES ("unisex", {spol_property_id});
		""")

		# Umetni specificna svojstva za vrstu pica (gazirano, alkoholno)
		vrsta_pica_property_id = get_property_id(cursor, "piće", "vrsta")
		cursor.execute(f"""
			INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID)
			VALUES ("gazirano", {vrsta_pica_property_id});
		""")
		cursor.execute(f"""
			INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID)
			VALUES ("alkoholno", {vrsta_pica_property_id});
		""")

		# Umetni specificna svojstva za ambalazu (boca, tetrapak)
		ambalaza_property_id = get_property_id(cursor, "piće", "ambalaža")
		cursor.execute(f"""
			INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID)
			VALUES ("boca", {ambalaza_property_id});
		""")
		cursor.execute(f"""
			INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID)
			VALUES ("tetrapak", {ambalaza_property_id});
		""")

		conn.commit()


def get_categories():
	categories = []

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		cursor.execute("""
			SELECT category.name
			FROM CATEGORIES AS category;
		""")
		categories = [i[0] for i in cursor.fetchall()]

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
			SELECT property.NAME
			FROM PROPERTIES AS property
			WHERE property.CATEGORY_ID={category_id};
		""")
		properties = [i[0] for i in cursor.fetchall()]

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
			SELECT descriptor.NAME
			FROM DESCRIPTORS AS descriptor
			WHERE descriptor.PROPERTY_ID={property_id};
		""")
		descriptors = [i[0] for i in cursor.fetchall()]

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