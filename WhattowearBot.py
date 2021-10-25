from pyowm import OWM
import telebot
from telebot import types

from my_tokens import owm_token, telebot_token
from text_blocks import hello, temp_minus_25, temp_minus_15, temp_minus_5, temp_zero, temp_10, temp_17, temp_24, \
    temp_35, temp_60, keyboard_text

owm = OWM(owm_token)
mgr = owm.weather_manager()

bot = telebot.TeleBot(telebot_token)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, hello)


@bot.message_handler(content_types=['text'])
def send_info(message):
    global city
    city = message.text
    observation = mgr.weather_at_place(message.text)
    w = observation.weather
    status = w.detailed_status
    temp = int(w.temperature('celsius')['temp'])
    feels_like = int(w.temperature('celsius')['feels_like'])
    answer = 'В городе ' + message.text + ' сейчас ' + str(temp) + ' градусов ' + \
             ', ощущается как ' + str(feels_like) + '\n\n'
    if feels_like <= -25:
        answer += temp_minus_25
    elif feels_like <= -15:
        answer += temp_minus_15
    elif feels_like <= -5:
        answer += temp_minus_5
    elif feels_like <= 0:
        answer += temp_zero
    elif feels_like <= 10:
        answer += temp_10
    elif feels_like <= 17:
        answer += temp_17
    elif feels_like <= 24:
        answer += temp_24
    elif feels_like <= 35:
        answer += temp_35
    elif feels_like <= 60:
        answer += temp_60
    if 'rain' in status:
        answer += '\n\n' + 'Там дождь, бери зонтик'
    bot.send_message(message.chat.id, answer)

    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='да, учесть прогноз', callback_data='yes')
    key_no = types.InlineKeyboardButton(text='нет, мне ненадолго', callback_data='no')
    keyboard.add(key_no, key_yes)
    bot.send_message(message.chat.id, text=keyboard_text, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'yes':
        three_h_forecast = mgr.forecast_at_place(city, '3h').forecast
        index = 0
        limit = 5
        somelist = []
        for weather in three_h_forecast:
            somelist.append(weather)
            index += 1
            if index == limit:
                break
        a = str(somelist)
        if 'rain' in a:
            bot.send_message(call.message.chat.id, 'В ближайшие часы ожидается дождь, не забудь зонтик')
        else:
            bot.send_message(call.message.chat.id, 'В ближайшие часы дождь не ожидается')
    if call.data == 'no':
        bot.send_message(call.message.chat.id, 'Надеюсь, я помог тебе. Если что - обращайся :)')


bot.infinity_polling()
