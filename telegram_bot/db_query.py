import psycopg2
from keyboards import get_estate_menu_buttons, get_one_estate_with_offer_keyboard


estate_status = {"new": "New", "offer_received": "Offer Received", "offer_accepted": "Offer Accepted",
					"sold": "Sold", "canceled": "Canceled"}  


db_connection = psycopg2.connect(
		dbname="rd-demo",
		user="incognito",
		# password="incognito",
		# host="127.0.0.1",
		# port="5432"
	)

db_cursor = db_connection.cursor()

# get all the id list of estates
queryset = "select * from estate_property"
db_cursor.execute(queryset)
queryset = db_cursor.fetchall()
id_list_of_estates = [
	f"{record[0]}" for record in queryset
]


"""
id|create_uid|write_uid|create_date|write_date|bedrooms|living_area|facades|garden_area|
name|postcode|garden_orientation|date_availability|description|garage|garden|expected_price|selling_price
|active|state|property_type_id|salesperson|buyer|total_area

estate - [0, 5, 6, 8, 9, 12, 13, 14, 15, 16, 19, 23]

 id | create_uid | write_uid | name |create_date|write_date| sequance 
type - [24, 25, 26, 27, 28, 29, 30]

id|partner_id|property_id|create_uid|write_uid|status|create_date|write_date|price|validity
offer - [0, 2, 5, 8, 9]
"""


def get_offers_for_estate(estate_id):
	queryset = f"""SELECT * FROM estate_property_offer
							WHERE property_id={estate_id}
						"""
	db_cursor.execute(queryset)
	queryset = db_cursor.fetchall()
	print(queryset)
	text = "List of Offers for this Estate: \n\n"
	if queryset is not None:
		counter = 0
		for record in queryset:
			counter += 1
			text += f"Number: {counter}\n"
			text += (f"Offer ID: {record[0]}\n"
					 f"Offer Status: {record[5]}\n"
					 f"Offer Price: ${record[8]}\n"
					 f"Offer Valid until: {record[9]} days\n\n")
	return {"text": text}


def get_one_estate(estate_id):
	queryset = f"""SELECT * FROM estate_property 
					LEFT JOIN estate_property_type 
					ON estate_property.property_type_id=estate_property_type.id
					WHERE estate_property.id={int(estate_id)}"""
	db_cursor.execute(queryset)
	queryset = db_cursor.fetchone()
	text = ""
	if queryset is not None:
		living_area = 0
		if queryset[8] is not None:
			living_area = queryset[8] 
		text += f"More info about {queryset[9]}\n\n"
		text += (f"Estate name: {queryset[9]}\n"
					f"Estate ID: {queryset[0]}\n"
					f"Bedrooms: {queryset[5]}\n"
					f"Living Area: {queryset[6]} meter square\n"
					f"Garden Area: {queryset[8]} meter square\n"
					f"Total area: {queryset[6]+queryset[8]} meter square\n"
					f"Description: {queryset[13]}\n"
					f"Garage: {queryset[14]}\n"
					f"Price: ${queryset[16]}\n"
					f"Status: {queryset[19]}\n"
					f"Type: {queryset[27]}")
	kb = get_one_estate_with_offer_keyboard(estate_id)
	return {'text': text, "keyboard": kb}


def get_estates_in_menu():
	queryset = "select * from estate_property"
	db_cursor.execute(queryset)
	queryset = db_cursor.fetchall()
	keyboard = get_estate_menu_buttons(queryset)
	text = "List of available real estates"
	return {"text": text, "keyboard": keyboard}


def get_list_of_types():
	queryset = "select * from estate_property_type"
	db_cursor.execute(queryset)
	queryset = db_cursor.fetchall()
	text = "List of Types of real estates: \n\n"
	for record in queryset:
		text += f"Name: {record[3]}\n"
	return {"text": text}


def get_list_of_tags():
	queryset = "select * from estate_property_tag"
	db_cursor.execute(queryset)
	queryset = db_cursor.fetchall()
	text = "List of Tags for real estates: \n\n"
	for record in queryset:
		text += f"Name: {record[3]}\n"
	return {"text": text}