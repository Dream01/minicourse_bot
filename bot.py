import config
import asyncio
import requests
from aiogram.utils.markdown import text
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, \
    KeyboardButton, KeyboardButtonPollType

bot = Bot(config.TOKEN)
dispatcher = Dispatcher(bot)

keyboard = InlineKeyboardMarkup(row_width=1)
menu_button_1 = InlineKeyboardButton(text='Погода ⏳', callback_data='menu_button_1',
                                     url='https://ua.sinoptik.ua/%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0-%D0%BB%D1%8C%D0%B2%D1%96%D0%B2')
menu_button_2 = InlineKeyboardButton(text='Ukraine 🇺🇦', callback_data='menu_button_2')
menu_button_3 = InlineKeyboardButton(text='Help 🆘', callback_data='menu_button_3',
                                     switch_inline_query_current_chat='/help')
keyboard.add(menu_button_1, menu_button_2, menu_button_3)

greet_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
button_hi = KeyboardButton('Hello 👻')
greet_keyboard.add(button_hi)

greet_keyboard_1 = ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = KeyboardButton('/start')
button_2 = KeyboardButton('/user_ids')
button_3 = KeyboardButton('/chat_ids')
greet_keyboard_1.add(button_1, button_2, button_3)

greet_keyboard_2 = ReplyKeyboardMarkup(resize_keyboard=True)
button_4 = KeyboardButton('/start')
button_5 = KeyboardButton('/Ukraine')
button_6 = KeyboardButton('/user_ids')
button_7 = KeyboardButton('/chat_ids')
greet_keyboard_2.row(button_1, button_2)
greet_keyboard_2.add(button_3)
greet_keyboard_2.insert(button_4)
greet_keyboard_2.row(button_5, button_6, button_7)
greet_keyboard_2.insert(KeyboardButton('/test'))

greet_keyboard_3 = ReplyKeyboardMarkup(resize_keyboard=True)
get_contact = KeyboardButton('Can I get your contact? 📱', request_contact=True)
get_location = KeyboardButton('Can I get your location? 🧭', request_location=True)
poll = KeyboardButtonPollType('Test')
request_poll = KeyboardButton('Poll', request_poll=poll)
greet_keyboard_3.add(get_contact, get_location, request_poll)


def get_country_by_name(country_name):
    url = f"https://restcountries-v1.p.rapidapi.com/name/{country_name}"

    headers = {
        'x-rapidapi-key': "bb99c4539dmshd6580b39ce65be7p1ac729jsn9040fd61491f",
        'x-rapidapi-host': "restcountries-v1.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers)
    return response


def get_weather(country, city):
    url = "https://community-open-weather-map.p.rapidapi.com/weather"

    querystring = {"q": f"{city},{country}"}

    headers = {
        'x-rapidapi-key': "bb99c4539dmshd6580b39ce65be7p1ac729jsn9040fd61491f",
        'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response


def get_country_data(response, message):
    if response.status_code == 200:
        json_result = response.json()[0]
        try:
            capital = json_result[message]
        except KeyError:
            return 'Such key not found'
        return capital
    else:
        return 'Not found'


@dispatcher.message_handler(commands=['start'])
async def process_start_command(msg: Message):
    await msg.answer('Hi there.', reply_markup=greet_keyboard)


@dispatcher.message_handler(commands=['menu'])
async def button_menu(msg: Message):
    await msg.answer('That what I can do!', reply_markup=greet_keyboard_1)


@dispatcher.message_handler(commands=['menu1'])
async def button_menu_1(msg: Message):
    await msg.answer('That what I can do!', reply_markup=greet_keyboard_2)


@dispatcher.message_handler(commands=['user_data'])
async def get_user_data(msg: Message):
    await msg.answer('Get the user data. ', reply_markup=greet_keyboard_3)


@dispatcher.callback_query_handler(text_contains='menu_button_')
async def menu(call: CallbackQuery):
    if call.data and call.data.startswith("menu_button_"):
        code = call.data[-1:]
        if code.isdigit():
            code = int(code)
        if code == 1:
            await call.message.edit_text('Google', reply_markup=keyboard)
        if code == 2:
            country = get_country_by_name('Ukraine')
            country_dict = country.json()[0]
            lst = []
            for i in country_dict:
                lst.append(f'{i} - {country_dict[i]}')
            await call.message.edit_text(lst, reply_markup=keyboard)
        if code == 3:
            await call.message.answer('Help', reply_markup=keyboard)
        else:
            await bot.answer_callback_query(call.id)


user_id_lst = []
chat_id_lst = []


@dispatcher.message_handler(commands='Ukraine')
async def get_weather_by_country_and_city(msg: Message):
    message = msg.text.split(' ')
    country = message[0].strip('/')
    action = 'capital'
    result = get_country_by_name(country)
    res = get_country_data(result, action)
    user_id_lst.append(msg.from_user.id)
    chat_id_lst.append(msg.chat.id)
    await msg.answer(res)


@dispatcher.message_handler(commands='user_ids')
async def get_user_id(msg: Message):
    await msg.answer(str(user_id_lst))


@dispatcher.message_handler(commands='chat_ids')
async def get_chat_id(msg: Message):
    await msg.answer(str(chat_id_lst))


help_message = text(
    "This is help for current bot.",
    "What can I do here: \n",
    "/start - привітання",
    "/menu - основне меню",
    "/menu1 - меню 1",
    "/Ukraine - дані про столицю",
    "/user_ids - ід користувачів",
    "/chat_ids - ід чатів",
    sep='\n'
)


@dispatcher.message_handler(commands=['help', 'hp'])
async def helper(msg: Message):
    await msg.answer(help_message)


@dispatcher.message_handler(commands=['send_my_message'])
async def send_my_message_to_chat(msg: Message):
    await bot.send_message(chat_id='Your chat id', text=msg.text)


asyncio.run(dispatcher.start_polling())
