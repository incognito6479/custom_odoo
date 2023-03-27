import logging

from aiogram import Bot, Dispatcher, executor, types
from conf import BOT_TOKEN
from db_query import get_estates_in_menu, id_list_of_estates, get_one_estate, get_list_of_types, \
    get_list_of_tags, get_offers_for_estate
from keyboards import start_kb, inline_kb_back_menu


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    await message.reply(
            "Hi!\nThis is test bot integrated with odoo!\nChoose items from menu.",
            reply_markup=start_kb
        )


@dp.callback_query_handler(lambda c: c.data == 'back_to_menu')
async def start_again(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,
            "Choose items from menu.",
            reply_markup=start_kb
        )


@dp.callback_query_handler(lambda c: c.data in id_list_of_estates)
async def get_one_estate_handler(callback_query: types.CallbackQuery):
    resp = get_one_estate(callback_query.data)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,
            resp['text'],
            reply_markup=resp['keyboard']
        )


@dp.callback_query_handler(lambda c: c.data.startswith("offer"))
async def show_offers_for_estate(callback_query: types.CallbackQuery):
    resp = get_offers_for_estate(callback_query.data.split("_")[1])
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,
            resp['text'],
            reply_markup=inline_kb_back_menu
        )


@dp.message_handler()
async def echo(message: types.Message):
    text = "Sorry I don't understand it"
    if message.text in ['🏢 Estate', '🏞 Types', '📌 Tags']:
        if message.text == "🏢 Estate":
            resp = get_estates_in_menu()
            await message.answer(resp['text'], reply_markup=resp['keyboard'])
        if message.text == "🏞 Types":
            resp = get_list_of_types()
            await message.answer(resp['text'], reply_markup=inline_kb_back_menu)
        if message.text == "📌 Tags":
            resp = get_list_of_tags()
            await message.answer(resp['text'], reply_markup=inline_kb_back_menu)
    elif message.text == "🏠 Home":
        await message.reply(
            "Hi!\nThis is test bot integrated with odoo!\nChoose items from menu.",
            reply_markup=buttons.start_kb
        )
    else:    
        await message.answer(text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)