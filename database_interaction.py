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
		odjeca_boja_crvena_id = add_descriptor(odjeca_boja_property_id, "crvena")
		odjeca_boja_crna_id = add_descriptor(odjeca_boja_property_id, "crna")
		odjeca_boja_bijela_id = add_descriptor(odjeca_boja_property_id, "bijela")

		# Umetni specificna svojstva za materijal (pamuk, poliester)
		odjeca_materijal_pamuk_id = add_descriptor(odjeca_materijal_property_id, "pamuk")
		odjeca_materijal_poliester_id = add_descriptor(odjeca_materijal_property_id, "poliester")

		# Umetni specificna svojstva za spol (muski, zenski)
		odjeca_spol_muski_id = add_descriptor(odjeca_spol_property_id, "muški")
		odjeca_spol_zenski_id = add_descriptor(odjeca_spol_property_id, "ženski")

		# Umetni specificna svojstva za vrstu pica (gazirano, alkoholno)
		pice_vrsta_gazirano_id = add_descriptor(pice_vrsta_property_id, "gazirano")
		pice_vrsta_alkoholno_id = add_descriptor(pice_vrsta_property_id, "alkoholno")

		# Umetni specificna svojstva za ambalazu (boca, tetrapak)
		pice_ambalaza_boca_id = add_descriptor(pice_ambalaza_property_id, "boca")
		pice_ambalaza_tetrapak_id = add_descriptor(pice_ambalaza_property_id, "tetrapak")



		connection.execute("""
			CREATE TABLE ITEMS
			(ID INTEGER PRIMARY KEY, NAME VARCHAR, PRICE VARCHAR, AMOUNT INT, CATEGORY_ID INT, IMAGE VARCHAR, DETAILS VARCHAR);
		""")

		connection.execute("""
			CREATE TABLE ITEM_DESCRIPTORS
			(ITEM_ID INT, DESCRIPTOR_ID INT);
		""")


		add_item(
			name="Nike WOW hlače",
			price="29,99",
			amount=10,
			category_name="odjeća",
			image="nike_hlace_crvene.png",
			details="Ove hlače su uistinu WOW.",
			descriptor_ids=[
				odjeca_boja_crna_id,
				odjeca_boja_crvena_id,
				odjeca_materijal_pamuk_id,
				odjeca_spol_muski_id,
			]
		)
		add_item(
			name="Adidas majica sa kapuljačom DELUXE",
			price="24,99",
			amount=9,
			category_name="odjeća",
			image="adidas_majica_kapuljaca.jpg",
			details="Ova bijela unisex majica ima kapuljaču. Baš je DELUXE",
			descriptor_ids=[
				odjeca_boja_bijela_id,
				odjeca_materijal_pamuk_id,
				odjeca_spol_muski_id,
				odjeca_spol_zenski_id,
			]
		)
		add_item(
			name="UMBRO kapa",
			price="9,99",
			amount=999,
			category_name="odjeća",
			image="umbro_kapa.jpg",
			details="Ova kapa se nosi na glavi.",
			descriptor_ids=[
				odjeca_boja_crna_id,
				odjeca_spol_muski_id,
				odjeca_spol_zenski_id,
			]
		)
		add_item(
			name="The North Face Antora",
			price="72,79",
			amount=13,
			category_name="odjeća",
			image="north_face_jakna.png",
			details="Ženska kišna jakna North Face Antora učinit će vas suhima i zaštićenima u svim vremenskim uvjetima. ",
			descriptor_ids=[
				odjeca_boja_bijela_id,
				odjeca_spol_zenski_id,
			]
		)
		add_item(
			name="Champion LADY NEON CUFFED PANTS",
			price="19,84",
			amount=14,
			category_name="odjeća",
			image="champion_hlace.jpg",
			details="Champion NEON ženski lifestyle donji dio trenirke je odličan izbor za opuštene, neformalne prilike nakon napornog dana.",
			descriptor_ids=[
				odjeca_spol_zenski_id,
				odjeca_materijal_poliester_id,
			]
		)

		add_item(
			name="Z bregov Trajno mlijeko 2,8% m.m. 1L",
			price="1,02",
			amount=50,
			category_name="piće",
			image="zbregov_trajno_mlijeko_1l.jpg",
			details="Sterilizirano, homogenizirano mlijeko s 2,8% mliječne masti.",
			descriptor_ids=[
				pice_ambalaza_tetrapak_id,
			]
		)
		add_item(
			name="Jana Prirodna mineralna voda 1,5 l",
			price="0,95",
			amount=12,
			category_name="piće",
			image="jana_voda.jpg",
			details="Negazirana. Izvor: Sveta Jana.",
			descriptor_ids=[
				pice_ambalaza_boca_id,
			]
		)
		add_item(
			name="Coca Cola 2 l",
			price="2,29",
			amount=40,
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
			descriptor_ids=[
				pice_vrsta_gazirano_id,
				pice_ambalaza_boca_id,
			]
		)
		add_item(
			name="Ožujsko Svijetlo pivo 0,5 l",
			price="1,19",
			amount=2,
			category_name="piće",
			image="ozujsko_pivo.jpg",
			details="Najomiljenije hrvatsko pivo. Preko 120 godina hrvatske tradicije i kvalitete. Proizvedeno s ponosom.",
			descriptor_ids=[
				pice_vrsta_alkoholno_id,
				pice_ambalaza_boca_id,
			]
		)
		add_item(
			name="Heineken Svijetlo pivo 0,4 l",
			price="1,25",
			amount=21,
			category_name="piće",
			image="heineken_pivo.jpg",
			details="Pasterizirano. 100% prirodni sastojci.",
			descriptor_ids=[
				pice_vrsta_alkoholno_id,
				pice_ambalaza_boca_id,
			]
		)
		add_item(
			name="Kutjevo Graševina Kvalitetno vino 1 l",
			price="7,15",
			amount=5,
			category_name="piće",
			image="vino.jpg",
			details="Kutjevo i kutjevačka vina simbol su hrvatske vinske kulture još od 1232. godine.",
			descriptor_ids=[
				pice_vrsta_alkoholno_id,
				pice_ambalaza_boca_id,
			]
		)
		add_item(
			name="Cockta original 1,5 l",
			price="1,85",
			amount=15,
			category_name="piće",
			image="cockta.jpg",
			details="Prirodni CO2. Bez kofeina.",
			descriptor_ids=[
				pice_vrsta_gazirano_id,
				pice_ambalaza_boca_id,
			]
		)
		add_item(
			name="Juicy Sok 100% jabuka 1 l",
			price="2,09",
			amount=17,
			category_name="piće",
			image="juicy.jpg",
			details="Najbolje iz voća. Dobro za nas. Dobro za prirodu. Bogat vitaminom C.",
			descriptor_ids=[
				pice_ambalaza_tetrapak_id,
			]
		)
		add_item(
			name="Vindi Multi A+C+E 2 l",
			price="2,49",
			amount=3,
			category_name="piće",
			image="vindi.jpg",
			details="Osvježavajuće negazirano bezalkoholno piće sa sokom od više vrsta voća od koncentriranih sokova, sa šećerom i sladilom, obogaćeno vitaminima.",
			descriptor_ids=[
				pice_ambalaza_tetrapak_id,
			]
		)
		add_item(
			name="Juicy Fruits multivitamin 1,5 l",
			price="1,49",
			amount=20,
			category_name="piće",
			image="juicy_fruits.jpg",
			details="Pasterizirano. Izvor 10 vitamina. Udio voćnog soka: 8%.",
			descriptor_ids=[
				pice_ambalaza_boca_id,
			]
		)

		add_item(
			name="Keyroad Električno šiljilo",
			price="11,89",
			amount=13,
			category_name="ostalo",
			image="siljilo.jpg",
			details="Electric. Potrebne 2xAA baterije.",
			descriptor_ids=[]
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
		# Izbrisi sve grupe svojstava i sva specificna svojstva kategorije koja se brise
		for property in get_properties(category_id):
			for descriptor in get_descriptors(property["ID"]):
				remove_descriptor(descriptor["ID"])
			remove_property(property["ID"])

		# Izbrisi kategoriju
		connection.execute(f"""
			DELETE
			FROM CATEGORIES
			WHERE ID={category_id};
		""")

		# Svim proizvodima obrisane kategorije promjeni kategoriju u kategoriju "Ostalo"
		ostalo_category_id = get_category_id("ostalo")
		connection.execute(f"""
			UPDATE ITEMS
			SET CATEGORY_ID={ostalo_category_id}
			WHERE CATEGORY_ID={category_id};
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
		for descriptor in get_descriptors(property_id):
			remove_descriptor(descriptor["ID"])

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

		connection.execute(f"""
			DELETE
			FROM ITEM_DESCRIPTORS
			WHERE DESCRIPTOR_ID={descriptor_id};
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


def add_item(
	name,
	price,
	amount,
	category_name,
	image = "",
	details = "",
	descriptor_ids = []
):

	item_id = -1
	with connection:
		category_id = get_category_id(category_name)

		result = connection.execute(f"""
			INSERT INTO ITEMS (NAME, PRICE, AMOUNT, CATEGORY_ID, IMAGE, DETAILS)
			VALUES ("{name}", "{price}", {amount}, {category_id}, "{image}", "{details}")
			RETURNING ID;
		""")
		item_id = result[0][0]

		for descriptor_id in descriptor_ids:
			connection.execute(f"""
				INSERT INTO ITEM_DESCRIPTORS (ITEM_ID, DESCRIPTOR_ID)
				VALUES ({item_id}, {descriptor_id})
			""")

	return item_id


def edit_item(
	id,
	name,
	price,
	amount,
	category_name,
	image = "",
	details = "",
	descriptor_ids = []
):
	with connection:
		category_id = get_category_id(category_name)

		connection.execute(f"""
			UPDATE ITEMS
			SET
				NAME="{name}",
				PRICE="{price}",
				AMOUNT={amount},
				CATEGORY_ID={category_id},
				IMAGE="{image}",
				DETAILS="{details}"
			WHERE ID={id};
		""")

		connection.execute(f"""
			DELETE
			FROM ITEM_DESCRIPTORS
			WHERE ITEM_ID={id};
		""")

		for descriptor_id in descriptor_ids:
			connection.execute(f"""
				INSERT INTO ITEM_DESCRIPTORS (ITEM_ID, DESCRIPTOR_ID)
				VALUES ({id}, {descriptor_id})
			""")


def remove_item(item_id):
	with connection:
		connection.execute(f"""
			DELETE
			FROM ITEMS
			WHERE ID={item_id};
		""")

		connection.execute(f"""
			DELETE
			FROM ITEM_DESCRIPTORS
			WHERE ITEM_ID={item_id};
		""")

def get_items_from_category_with_descriptors(category_id, descriptor_ids):
    items = []
    descriptors_string = ",".join(str(id) for id in descriptor_ids)

    with connection:
        if len(descriptor_ids) == 0:
            result, col_names = connection.execute_and_return_col_names(f"""
                SELECT *
                FROM ITEMS
                WHERE CATEGORY_ID={category_id};
            """)

        else:
            result, col_names = connection.execute_and_return_col_names(f"""
                SELECT *
                FROM ITEMS AS item
                WHERE item.CATEGORY_ID={category_id}
                AND item.ID IN (
                    SELECT item2.ITEM_ID
                    FROM ITEM_DESCRIPTORS as item2
                    WHERE item2.DESCRIPTOR_ID IN ({descriptors_string})
                );
            """)

        for row in result:
            item = {}
            for column_name, cell in zip(col_names, row):
                item[column_name] = cell
            items.append(item)

    return items