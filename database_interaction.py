import sqlite3


database_filename="database.db"


def initialize():
	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		# Napravi tablicu kategorije i umetni nekoliko kategorija
		query = """CREATE TABLE CATEGORIES (ID INTEGER PRIMARY KEY, NAME VARCHAR);"""
		cursor.execute(query)

		query = """INSERT INTO CATEGORIES (NAME) VALUES ("odjeća");"""
		cursor.execute(query)
		query = """INSERT INTO CATEGORIES (NAME) VALUES ("piće");"""
		cursor.execute(query)


		# Napravi tablicu grupa svojstava
		query = """CREATE TABLE PROPERTIES (ID INTEGER PRIMARY KEY, NAME VARCHAR, CATEGORY_ID INT);"""
		cursor.execute(query)

		# Umetni grupe svojstava za odjecu (boja, materijal, spol)
		query = """SELECT category.ID FROM CATEGORIES AS category WHERE category.NAME="odjeća";"""
		cursor.execute(query)
		odjeca_category_id = cursor.fetchone()[0]
		query = f"""INSERT INTO PROPERTIES (NAME, CATEGORY_ID) VALUES ("boja", {odjeca_category_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO PROPERTIES (NAME, CATEGORY_ID) VALUES ("materijal", {odjeca_category_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO PROPERTIES (NAME, CATEGORY_ID) VALUES ("spol", {odjeca_category_id});"""
		cursor.execute(query)

		# Umetni grupe svojstava za pica (vrsta, ambalaza)
		query = """SELECT category.ID FROM CATEGORIES AS category WHERE category.NAME="piće";"""
		cursor.execute(query)
		pice_category_id = cursor.fetchone()[0]
		query = f"""INSERT INTO PROPERTIES (NAME, CATEGORY_ID) VALUES ("vrsta", {pice_category_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO PROPERTIES (NAME, CATEGORY_ID) VALUES ("ambalaža", {pice_category_id});"""
		cursor.execute(query)


		# Napravi tablicu specificnih svojstava
		query = """CREATE TABLE DESCRIPTORS (ID INTEGER PRIMARY KEY, NAME VARCHAR, PROPERTY_ID INT);"""
		cursor.execute(query)

		# Umetni specificna svojstva za boju (crvena, crna, bijela)
		query = """SELECT property.ID FROM PROPERTIES AS property WHERE property.NAME="boja";"""
		cursor.execute(query)
		boja_property_id = cursor.fetchone()[0]
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("crvena", {boja_property_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("crna", {boja_property_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("bijela", {boja_property_id});"""
		cursor.execute(query)

		# Umetni specificna svojstva za materijal (pamuk, poliester)
		query = """SELECT property.ID FROM PROPERTIES AS property WHERE property.NAME="materijal";"""
		cursor.execute(query)
		materijal_property_id = cursor.fetchone()[0]
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("pamuk", {materijal_property_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("poliester", {materijal_property_id});"""
		cursor.execute(query)

		# Umetni specificna svojstva za spol (muski, zenski, unisex)
		query = """SELECT property.ID FROM PROPERTIES AS property WHERE property.NAME="spol";"""
		cursor.execute(query)
		spol_property_id = cursor.fetchone()[0]
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("muški", {spol_property_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("ženski", {spol_property_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("unisex", {spol_property_id});"""
		cursor.execute(query)

		# Umetni specificna svojstva za vrstu pica (gazirano, alkoholno)
		query = """SELECT property.ID FROM PROPERTIES AS property WHERE property.NAME="vrsta";"""
		cursor.execute(query)
		vrsta_pica_property_id = cursor.fetchone()[0]
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("gazirano", {vrsta_pica_property_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("alkoholno", {vrsta_pica_property_id});"""
		cursor.execute(query)

		# Umetni specificna svojstva za ambalazu (boca, tetrapak)
		query = """SELECT property.ID FROM PROPERTIES AS property WHERE property.NAME="ambalaža";"""
		cursor.execute(query)
		ambalaza_property_id = cursor.fetchone()[0]
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("boca", {ambalaza_property_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("tetrapak", {ambalaza_property_id});"""
		cursor.execute(query)

		conn.commit()


def get_categories():
	categories = []

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		query = """SELECT category.name FROM CATEGORIES AS category;"""
		cursor.execute(query)
		categories = [i[0] for i in cursor.fetchall()]

		conn.commit()

	return categories


def category_exists(category_name):
	category_name = category_name.lower()

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		query = f"""SELECT * FROM CATEGORIES AS category WHERE category.NAME="{category_name}";"""
		cursor.execute(query)
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

		query = f"""INSERT INTO CATEGORIES (NAME) VALUES ("{category_name}");"""
		cursor.execute(query)

		conn.commit()


def rename_category(current_category_name, new_category_name):
	current_category_name = current_category_name.lower()
	new_category_name = new_category_name.lower()

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		query = f"""SELECT category.ID FROM CATEGORIES AS category WHERE category.NAME="{current_category_name}";"""
		cursor.execute(query)
		category_id = cursor.fetchone()[0]

		query = f"""UPDATE CATEGORIES AS category SET NAME="{new_category_name}" WHERE category.ID={category_id};"""
		cursor.execute(query)

		conn.commit()


def remove_category(category_name):
	category_name = category_name.lower()

	with sqlite3.connect(database_filename) as conn:
		cursor = conn.cursor()

		query = f"""DELETE FROM CATEGORIES WHERE NAME="{category_name}";"""
		cursor.execute(query)

		conn.commit()