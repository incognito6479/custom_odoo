from aiogram import types


buttons = {
    'estate': types.KeyboardButton('🏢 Estate'),
    'type': types.KeyboardButton('🏞 Types'),
    'tags': types.KeyboardButton('📌 Tags'),
    'home': types.KeyboardButton('🏠 Home'),
}

start_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
start_kb.add(buttons['estate']).add(buttons['type']).add(buttons['tags'])

inline_kb_back_menu = types.InlineKeyboardMarkup(resize_keyboard=True) \
				.add(types.InlineKeyboardButton('<< Back', callback_data="back_to_menu"))


def get_estate_menu_buttons(queryset):
	estate_menu_buttons = types.InlineKeyboardMarkup(resize_keyboard=True)
	for record in queryset:
		estate_menu_buttons.add(
			types.InlineKeyboardButton(f"{record[9]}", callback_data=f"{record[0]}")
		)
	estate_menu_buttons.add(types.InlineKeyboardButton('<< Back', callback_data="back_to_menu"))
	return estate_menu_buttons


def get_one_estate_with_offer_keyboard(estate_id):
	kb = types.InlineKeyboardMarkup(resize_keyboard=True)
	kb.add(types.InlineKeyboardButton('Show offers', callback_data=f"offer_{estate_id}"))
	kb.add(types.InlineKeyboardButton('<< Back', callback_data="back_to_menu"))
	return kb