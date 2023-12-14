import asyncio
import string
from googletrans import Translator
import config
from functions_api import get_nasa_photo, search
from text import *
from config import token, nasa_token
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import random

bot = Bot(token)
dp = Dispatcher(bot)
FULL_EXPLANATIONS = {}


def create_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton('/start'),
        KeyboardButton('/help'),
        KeyboardButton('/description'),
        KeyboardButton('/random')
    ]
    keyboard.add(*buttons)
    return keyboard


def translate_explanation(text):
    try:
        if text:
            translator = Translator()
            translated = translator.translate(text, dest='ru')
            return translated.text
        else:
            return None
    except Exception as e:
        print(f"Translation error: {e}")
        return None


# Обработчики команд
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    try:
        await message.answer(text=start, reply_markup=create_keyboard())
        await message.delete()
    except Exception as e:
        print(f"Error in start_command: {e}")


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    try:
        await message.answer(text=help_commands, reply_markup=create_keyboard())
        await message.delete()
    except Exception as e:
        print(f"Error in help_command: {e}")


@dp.message_handler(commands=['description'])
async def description_command(message: types.Message):
    try:
        await message.answer(text=description, reply_markup=create_keyboard())
        await message.delete()
    except Exception as e:
        print(f"Error in description_command: {e}")


@dp.message_handler(commands=['random'])
async def random_command(message: types.Message):
    try:
        letters = string.ascii_lowercase
        rand_string = ''.join(random.choice(letters) for i in range(10))
        await message.answer(text=rand_string, reply_markup=create_keyboard())
    except Exception as e:
        print(f"Error in random_command: {e}")


# Обработчик получения фото от NASA
@dp.message_handler(commands=['nasa_photo'])
async def send_nasa_photo(message: types.Message):
    token_nasa = config.nasa_token
    try:
        nasa_photo_url, nasa_explanation = get_nasa_photo(token_nasa)

        if nasa_photo_url and nasa_explanation:
            preview_explanation = nasa_explanation[:400] + '...' if len(nasa_explanation) > 400 else nasa_explanation
            translated_explanation = translate_explanation(nasa_explanation)

            if translated_explanation:
                caption = translated_explanation[:400] + '...' if len(
                    translated_explanation) > 400 else translated_explanation
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton("Читать далее", callback_data="read_more"))

                photo_message = await bot.send_photo(message.chat.id, nasa_photo_url, caption=caption,
                                                     reply_markup=keyboard)

                if photo_message.message_id not in FULL_EXPLANATIONS:
                    FULL_EXPLANATIONS[photo_message.message_id] = translated_explanation
            else:
                await message.reply("Ошибка при переводе описания изображения")
        else:
            await message.reply("Не удалось получить фотографию из космоса или её описание")
    except Exception as e:
        print(f"Error in send_nasa_photo: {e}")


# Обработчик запроса "Читать далее"
@dp.callback_query_handler(lambda callback_query: True)
async def handle_callback_query(callback_query: types.CallbackQuery):
    try:
        if callback_query.data == 'read_more':
            full_explanation = FULL_EXPLANATIONS.get(callback_query.message.message_id)
            if full_explanation:
                await bot.send_message(callback_query.from_user.id, full_explanation)
            else:
                await bot.send_message(callback_query.from_user.id, "Полное описание недоступно.")
    except Exception as e:
        print(f"Error in handle_callback_query: {e}")


# Обработчик поисковых запросов
async def process_search_command(message):
    try:
        query = message.text.split(' ', 1)[1]
        search_results = search(query)
        if search_results:
            for result in search_results[:3]:
                await message.answer(f"Заголовок: {result['title']}\nСсылка: {result['link']}")
        else:
            await message.answer("Ничего не найдено")
    except Exception as e:
        print(f"Error in process_search_command: {e}")


@dp.message_handler(commands=['search'])
async def handle_search_command(message: types.Message):
    await process_search_command(message)


# Запуск бота
async def main():
    try:
        await dp.start_polling()
    except Exception as e:
        print(f"Error in main: {e}")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error in asyncio.run: {e}")
