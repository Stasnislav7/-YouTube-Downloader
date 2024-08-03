import os
import time
import telebot
from pytube import YouTube
from telebot import types
import Token

bot = telebot.TeleBot(Token.Token)
user_list = {}
content_map = {'audio': 'mp3', 'video': 'mp4'}


class User:
    def __init__(self, chat_id, content_type):
        self.chat_id = chat_id
        self.content_type = content_type

    def yt(self, url, message, bot, file_extension):
        download_youtube_content_type(url, message, bot, file_extension)

    @staticmethod
    def get_or_create(chat_id):
        if user_list.get(chat_id):
            return user_list.get(chat_id)
        user = User(chat_id, 'video')
        user_list[chat_id] = user
        return user


@bot.message_handler(commands=['start'])
def welcome(message):
    mess = f'Привіт {message.from_user.first_name}, Відправляй посилання: '
    bot.send_message(message.chat.id, mess)


@bot.message_handler(commands=['audio'])
def audio(message):
    user = User.get_or_create(message.chat.id)
    user.content_type = 'audio'
    bot.send_message(message.chat.id, 'Режим аудіо увімкнено')


@bot.message_handler(commands=['video'])
def video(message):
    user = User.get_or_create(message.chat.id)
    user.content_type = 'video'
    bot.send_message(message.chat.id, 'Режим відео увімкнено')


@bot.message_handler(func=lambda m: True)
def text_message(message):
    chat_id = message.chat.id
    url = message.text
    if message.text.startswith('https://youtu.be/'):
        user = User.get_or_create(chat_id)
        bot.send_message(chat_id, 'Починаю завантаження, це може зайняти декілька хвилин :)')
        user.yt(url, message, bot, content_map.get(user.content_type))


def download_youtube_content_type(url, message, bot, file_extension):
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=(file_extension == 'mp3')).first()
    if not os.path.exists('media'):
        os.makedirs('media')
    file_path = f'media/{message.chat.id}.{file_extension}'
    stream.download(filename=file_path)

    with open(file_path, 'rb') as file:
        if file_extension == 'mp3':
            bot.send_audio(message.chat.id, file, caption="Ось ваша музика")
        else:
            bot.send_video(message.chat.id, file, caption="Ось ваше відео")

    os.remove(file_path)


@bot.message_handler(commands=['test'])
def find_file_ids(message):
    for file in os.listdir('media/'):
        if file.split('.')[-1] == 'ogg':
            with open('media/' + file, 'rb') as f:
                res = bot.send_video(message.chat.id, f)
                print(file, res)


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(3)
