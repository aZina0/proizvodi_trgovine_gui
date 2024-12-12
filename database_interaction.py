import sqlite3

def initialize():
	with sqlite3.connect("database.db") as conn:
		cursor = conn.cursor()

		# Napravi tablicu kategorije i umetni nekoliko kategorija
		query = """CREATE TABLE CATEGORIES (NAME VARCHAR);"""
		cursor.execute(query)

		query = """INSERT INTO CATEGORIES (NAME) VALUES ("odjeća");"""
		cursor.execute(query)
		query = """INSERT INTO CATEGORIES (NAME) VALUES ("piće");"""
		cursor.execute(query)


		# Napravi tablicu grupa svojstava
		query = """CREATE TABLE PROPERTIES (NAME VARCHAR, CATEGORY_ID INT);"""
		cursor.execute(query)

		# Umetni grupe svojstava za odjecu (boja, materijal, spol)
		query = """SELECT category.ROWID FROM CATEGORIES AS category WHERE category.NAME == "odjeća";"""
		cursor.execute(query)
		odjeca_category_id = cursor.fetchone()[0]
		query = f"""INSERT INTO PROPERTIES (NAME, CATEGORY_ID) VALUES ("boja", {odjeca_category_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO PROPERTIES (NAME, CATEGORY_ID) VALUES ("materijal", {odjeca_category_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO PROPERTIES (NAME, CATEGORY_ID) VALUES ("spol", {odjeca_category_id});"""
		cursor.execute(query)

		# Umetni grupe svojstava za pica (vrsta, ambalaza)
		query = """SELECT category.ROWID FROM CATEGORIES AS category WHERE category.NAME == "piće";"""
		cursor.execute(query)
		pice_category_id = cursor.fetchone()[0]
		query = f"""INSERT INTO PROPERTIES (NAME, CATEGORY_ID) VALUES ("vrsta", {pice_category_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO PROPERTIES (NAME, CATEGORY_ID) VALUES ("ambalaža", {pice_category_id});"""
		cursor.execute(query)


		# Napravi tablicu specificnih svojstava
		query = """CREATE TABLE DESCRIPTORS (NAME VARCHAR, PROPERTY_ID INT);"""
		cursor.execute(query)

		# Umetni specificna svojstva za boju (crvena, crna, bijela)
		query = """SELECT property.ROWID FROM PROPERTIES AS property WHERE property.NAME == "boja";"""
		cursor.execute(query)
		boja_property_id = cursor.fetchone()[0]
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("crvena", {boja_property_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("crna", {boja_property_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("bijela", {boja_property_id});"""
		cursor.execute(query)

		# Umetni specificna svojstva za materijal (pamuk, poliester)
		query = """SELECT property.ROWID FROM PROPERTIES AS property WHERE property.NAME == "materijal";"""
		cursor.execute(query)
		materijal_property_id = cursor.fetchone()[0]
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("pamuk", {materijal_property_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("poliester", {materijal_property_id});"""
		cursor.execute(query)

		# Umetni specificna svojstva za spol (muski, zenski, unisex)
		query = """SELECT property.ROWID FROM PROPERTIES AS property WHERE property.NAME == "spol";"""
		cursor.execute(query)
		spol_property_id = cursor.fetchone()[0]
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("muški", {spol_property_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("ženski", {spol_property_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("unisex", {spol_property_id});"""
		cursor.execute(query)

		# Umetni specificna svojstva za vrstu pica (gazirano, alkoholno)
		query = """SELECT property.ROWID FROM PROPERTIES AS property WHERE property.NAME == "vrsta";"""
		cursor.execute(query)
		vrsta_pica_property_id = cursor.fetchone()[0]
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("gazirano", {vrsta_pica_property_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("alkoholno", {vrsta_pica_property_id});"""
		cursor.execute(query)

		# Umetni specificna svojstva za ambalazu (boca, tetrapak)
		query = """SELECT property.ROWID FROM PROPERTIES AS property WHERE property.NAME == "ambalaža";"""
		cursor.execute(query)
		ambalaza_property_id = cursor.fetchone()[0]
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("boca", {ambalaza_property_id});"""
		cursor.execute(query)
		query = f"""INSERT INTO DESCRIPTORS (NAME, PROPERTY_ID) VALUES ("tetrapak", {ambalaza_property_id});"""
		cursor.execute(query)

		conn.commit()


def get_categories():
	categories = []

	with sqlite3.connect("database.db") as conn:
		cursor = conn.cursor()

		query = """SELECT category.name FROM CATEGORIES AS category;"""
		cursor.execute(query)
		categories = [i[0] for i in cursor.fetchall()]

		conn.commit()

	return categories