import telebot
import requests
from googleapiclient.discovery import build

bot = telebot.TeleBot('6932183540:AAENG1FAl3eiT-38zGBYqvX3DkDMc9TOYCE')

# Словарь для хранения изначальных вопросов пользователей
user_questions = {}



# Ответ на команду /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"Привет, {message.from_user.first_name}! Чем могу помочь?\n "
                          f"Для вопроса о погоде, напишите - погода.\n"
                          f"Для вопроса о курсе валют, напишите - курс.\n"
                          f"Для вопроса о книгах, напишите - книга.\n"
                          f"Для помощи используйте команду /help.\n"
                          f"Для завершения используйте команду /stop")

@bot.message_handler(commands=['stop'])
def send_goodbye(message):
    bot.reply_to(message, f"До свидания, {message.from_user.first_name}! Надеюсь был тебе полезен, для возобновление диалога напиши /start ")


# Ответ на команду /help
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Этот бот может предоставить информацию о погоде,курсе валюты или книгах.\n"
                          "Для получения информации о погоде, напишите - погода, укажите город, например: 'Москва'\n"
                          "Для получения информации о курсе валют, напишите - курс,укажите код базовой и целевой валюты,. например: 'USD , EUR'\n"
                          "Для получения информации о книгах, напишите - книга,укажите название книги. например: 'Облоиов'\n"
                          "Доступные команды:\n"
                          "/start - начать беседу\n"
                          "/stop - закончить беседу\n"
                          "/help - получить помощь")


# Функция для получения информации о книгах с использованием Google Books API
def get_book_info(book_title):
    api_key = "AIzaSyB6Shlf_lUKXQ-lQB4rAOx7WsZ42alneaY"
    service = build('books', 'v1', developerKey=api_key)
    request = service.volumes().list(q=book_title)
    response = request.execute()

    books_info = []
    if 'items' in response:
        for book in response['items']:
            volume_info = book['volumeInfo']
            title = volume_info.get('title')
            authors = volume_info.get('authors', ['Unknown Author'])
            description = volume_info.get('description', 'No description available')
            average_rating = volume_info.get('averageRating', 'Not rated')

            book_data = {
                'Title': title,
                'Authors': authors,
                'Description': description,
                'Average Rating': average_rating
            }
            books_info.append(book_data)

    return books_info


# Функция для форматирования информации о книгах с ограничением количества книг в ответе
def format_book_info(book_info, limit=1):
    formatted_info = ""
    books_to_display = book_info[:limit]

    for book in books_to_display:
        formatted_info += f"Название: {book['Title']}\n"
        formatted_info += f"Авторы: {', '.join(book['Authors'])}\n"
        formatted_info += f"Описание: {book['Description']}\n"

    return formatted_info



def process_how_can_i_help(message):
     bot.send_message(message.chat.id, "Чем я еще могу помочь?\n"
                                      "Для получения информации о погоде, напишите - погода, укажите город, например: 'Москва'\n"
                                      "Для получения информации о курсе валют, напишите - курс,укажите код базовой и целевой валюты,. например: 'USD , EUR'\n"
                                      "Для получения информации о книгах, напишите - книга,укажите название книги. например: 'Обломов'\n")

def get_weather(city):
    api_key = "286b058678be6bfefb682d0c90908c6d"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={api_key}&units=metric"
    response = requests.get(complete_url)
    data = response.json()
    return data

# Функция для обработки запроса о погоде
def process_weather_request(city):
    weather_data = get_weather(city)
    if weather_data.get("cod") != "404":
        if "weather" in weather_data:
            weather_desc = weather_data["weather"][0]["description"]
            temperature = weather_data["main"]["temp"]
            return f"Погода в {city.capitalize()}: {weather_desc}. Температура: {temperature}°C"
        else:
            return "Данные о погоде недоступны. Пожалуйста, попробуйте другой город."

    else:
        return "Город не найден. Пожалуйста, уточните запрос."



# Функция для получения данных о курсе валют с использованием API
def process_currency_request(base_currency, target_currency):
    api_key = "9198c3f84a929120648f5f78"
    base_url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    response = requests.get(base_url)
    if response.status_code == 200:
        data = response.json()
        if target_currency in data['rates']:
            rate = data['rates'][target_currency]
            return f"1 {base_currency} = {rate} {target_currency}"
        else:
            return "Информация о запрошенной валюте недоступна."
    else:
        return "Проблема при получении данных о курсе валюты."



# Функция для обработки ответа на запрос информации о книге
def process_book_response(message):
    book_title = message.text
    book_info = get_book_info(book_title)
    if book_info:
        bot.reply_to(message, format_book_info(book_info))
        process_how_can_i_help(message)
    else:
        bot.reply_to(message, "К сожалению, информация о книге не найдена.")
        process_how_can_i_help(message)


'''
# Ответ на команды /start и /help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Чем могу помочь? Задайте вопрос о погоде или курсе валюты.")
'''

# Обработка сообщений пользователя
@bot.message_handler(func=lambda message: True)
# Ответ на обычные сообщения пользователя
@bot.message_handler(func=lambda message: True)
def process_user_input(message):
    user_input = message.text.lower()
    query_type = determine_query_type(user_input)
    if query_type == "погода":
        user_questions[message.chat.id] = "погода"
        bot.reply_to(message, "Для какого города вы хотите узнать погоду?")
        bot.register_next_step_handler(message, process_weather_response)
    elif query_type == "валюта":
        user_questions[message.chat.id] = "валюта"
        bot.reply_to(message, "Введите код базовой валюты:")
        bot.register_next_step_handler(message, process_currency_base)
    elif query_type == "книга":
        user_questions[message.chat.id] = "название книги"
        bot.reply_to(message, "Введите название книги:")
        bot.register_next_step_handler(message, process_book_response)
    else:
        bot.reply_to(message, "Простите, не могу понять ваш запрос.")
        process_how_can_i_help(message)


# Функция для определения типа запроса
def determine_query_type(user_input):
    if "погода" in user_input:
        return "погода"
    elif "курс" in user_input:
        return "валюта"
    elif "книга" in user_input:
        return "книга"
    else:
        return "неопределенный"




# Обработчик ответа на вопрос о погоде
def process_weather_response(message):
    city = message.text
    response = process_weather_request(city)
    bot.reply_to(message, response)
    process_how_can_i_help(message)


# Обработчик ответа на запрос кода базовой валюты
def process_currency_base(message):
    base_currency = message.text.upper()
    bot.reply_to(message, "Введите код целевой валюты:")
    bot.register_next_step_handler(message, process_currency_target, base_currency)

# Обработчик ответа на запрос кода целевой валюты
def process_currency_target(message, base_currency):
    target_currency = message.text.upper()
    response = process_currency_request(base_currency, target_currency)
    bot.reply_to(message, response)
    process_how_can_i_help(message)

'''
@bot.message_handler(commands=['end'])
def send_goodbye(message):
    bot.reply_to(message, f"До свидания, {message.from_user.first_name}! Надеюсь, я смог помочь вам.")
'''

# Запуск бота
bot.polling()
