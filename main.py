import telebot
import json
import sqlite3
import io
from random import randint
from datetime import *
from ploziks import *
from anekdots import *
from imgs import *
from demotivator import *


with open('res/token.json', 'r', encoding='utf8') as file:
    json_file = json.load(file)
    token = json_file['token']

with open('res/settings.json', 'r', encoding='utf8') as file:
    json_file = json.load(file)
    adjectives = np.array(json_file['adjectives'])
    nouns = np.array(json_file['nouns'])
    welcomes = np.array(json_file['welcomes'])
    commands = np.array(json_file['commands'])


try:
    sql_vip = f'SELECT user_id FROM users WHERE vip_status=1'
    con = sqlite3.connect('res/database.db')
    cur = con.cursor()
    vip_users = cur.execute(sql_vip).fetchall()[0]
    con.commit()
    con.close()
except:
    vip_users = []


command_message = '\n\nДоступные команды:\n'
last_min_rand = {}
last_max_rand = {}
super_users = []
imgs_count = {}
imgs_requests = {}
last_plozik = {}
dem_photos = {}
big_texts = {}
small_texts = {}

bot = telebot.TeleBot(token, parse_mode=False)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global last_plozik
    if call.data == "+1":
        bot.answer_callback_query(call.id, "Answer is Yes")
    elif call.data == "-1":
        bot.answer_callback_query(call.id, "Answer is No")


def sql_insert(*args):
    con = sqlite3.connect('res/database.db')
    cur = con.cursor()
    cur.execute(*args)
    con.commit()
    con.close()


def sql_select(*args):
    con = sqlite3.connect('res/database.db')
    cur = con.cursor()
    a = cur.execute(*args).fetchall()
    con.commit()
    con.close()
    return a


def sql_update(*args):
    con = sqlite3.connect('res/database.db')
    cur = con.cursor()
    cur.execute(*args)
    con.commit()
    con.close()


@bot.message_handler(commands=['start', 'help', 's', 'h'])
def start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username
    command = '/h'
    time_normal = str(datetime.today().time())[:8]
    date_normal = datetime.today().date()
    sql = f'INSERT INTO request_logs(user_id, chat_id, username, command, time_normal, date_normal) VALUES(?,?,?,?,?,?)'
    sql_insert(sql, [user_id, chat_id, username, command, time_normal, date_normal])
    user_id = message.from_user.id
    con = sqlite3.connect('res/database.db')
    cur = con.cursor()
    try:
        sql = f'SELECT start_message FROM users WHERE user_id={user_id}'
        start_message = cur.execute(sql).fetchall()[0][0]
    except:
        username = message.from_user.username
        chat_id = message.chat.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        county_code = message.from_user.language_code
        start_message = f'{np.random.choice(welcomes)} {np.random.choice(adjectives)} {np.random.choice(nouns)}!'
        sql = f'INSERT INTO users(user_id, username, chat_id, first_name, last_name, county_code, start_message) VALUES(?,?,?,?,?,?,?)'
        cur.execute(sql, [user_id, username, chat_id, first_name, last_name, county_code, start_message])
        con.commit()
    con.close()
    bot.send_message(message.chat.id, start_message + command_message + '\n'.join(commands))


@bot.message_handler(commands=['rewelcome', 'rw'])
def re_rand_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username
    command = '/rw'
    time_normal = str(datetime.today().time())[:8]
    date_normal = datetime.today().date()
    sql = f'INSERT INTO request_logs(user_id, chat_id, username, command, time_normal, date_normal) VALUES(?,?,?,?,?,?)'
    sql_insert(sql, [user_id, chat_id, username, command, time_normal, date_normal])
    con = sqlite3.connect('res/database.db')
    cur = con.cursor()
    sql = f'SELECT start_message FROM users WHERE user_id={user_id}'
    start_message_old = cur.execute(sql).fetchall()[0][0]
    start_message = f'{np.random.choice(welcomes)} {np.random.choice(adjectives)} {np.random.choice(nouns)}!'
    while start_message == start_message_old:
        start_message = f'{np.random.choice(welcomes)} {np.random.choice(adjectives)} {np.random.choice(nouns)}!'
    sql = f'UPDATE users SET start_message="{start_message}" WHERE user_id="{user_id}"'
    cur.execute(sql)
    con.commit()
    con.close()
    bot.send_message(message.chat.id, f'Ваше новое приветствие:\n{start_message}')


@bot.message_handler(commands=['random', 'rnd'])
def info_rand(message):
    bot.send_message(message.chat.id, f'Введите минимальный предел:')
    bot.register_next_step_handler(message, min_rand)


def min_rand(message):
    global last_min_rand
    try:
        rand_min = int(float(message.text))
        last_min_rand[int(message.from_user.id)] = rand_min
        user_id = message.from_user.id
        chat_id = message.chat.id
        username = message.from_user.username
        command = '/rnd'
        time_normal = str(datetime.today().time())[:8]
        date_normal = datetime.today().date()
        sql = f'INSERT INTO request_logs(user_id, chat_id, username, command, time_normal, date_normal) VALUES(?,?,?,?,?,?)'
        sql_insert(sql, [user_id, chat_id, username, command, time_normal, date_normal])
        bot.send_message(message.chat.id, f'Введите максимальный предел:')
        bot.register_next_step_handler(message, max_rand)
    except:
        bot.send_message(message.chat.id, f'Введено неверное значение!\nПопробуйте снова:')
        bot.register_next_step_handler(message, min_rand)


def max_rand(message):
    global last_max_rand
    try:
        rand_max = int(float(message.text))
        last_max_rand[int(message.from_user.id)] = rand_max
        final_rand(message)
    except:
        bot.send_message(message.chat.id, f'Введено неверное значение!\nПопробуйте снова:')
        bot.register_next_step_handler(message, max_rand)


def final_rand(message):
    global last_max_rand
    global last_min_rand
    rand_min = last_min_rand[int(message.from_user.id)]
    rand_max = last_max_rand[int(message.from_user.id)]
    rand_int = randint(rand_min, rand_max)
    bot.send_message(message.chat.id, f'Ваше рандомное число: {rand_int}')


@bot.message_handler(commands=['plz'])
def get_ploz(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username
    command = '/plz'
    time_normal = str(datetime.today().time())[:8]
    date_normal = datetime.today().date()
    sql = f'INSERT INTO request_logs(user_id, chat_id, username, command, time_normal, date_normal) VALUES(?,?,?,?,?,?)'
    sql_insert(sql, [user_id, chat_id, username, command, time_normal, date_normal])
    bot.send_message(message.chat.id, rand_ploz())


@bot.message_handler(commands=['ank'])
def get_anekdot(message):
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id
        username = message.from_user.username
        command = '/ank'
        time_normal = str(datetime.today().time())[:8]
        date_normal = datetime.today().date()
        sql = f'INSERT INTO request_logs(user_id, chat_id, username, command, time_normal, date_normal) VALUES(?,?,?,?,?,?)'
        sql_insert(sql, [user_id, chat_id, username, command, time_normal, date_normal])
        bot.send_message(message.chat.id, anekdot_request())
    except:
        bot.send_message(message.chat.id, 'Произошла неизвестная ошибка!')


@bot.message_handler(commands=['img'])
def info_imgs(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username
    command = '/img'
    time_normal = str(datetime.today().time())[:8]
    date_normal = datetime.today().date()
    sql = f'INSERT INTO request_logs(user_id, chat_id, username, command, time_normal, date_normal) VALUES(?,?,?,?,?,?)'
    sql_insert(sql, [user_id, chat_id, username, command, time_normal, date_normal])
    bot.send_message(message.chat.id, 'По какому запросу картинки вы хотите получить?')
    bot.register_next_step_handler(message, request_imgs)


def request_imgs(message):
    global imgs_requests
    try:
        request = str(message.text)
        imgs_requests[message.chat.id] = request
        bot.send_message(message.chat.id, 'Хорошо. Сколько картинок ты хочешь получить?')
        bot.register_next_step_handler(message, request_count)
    except:
        bot.send_message(message.chat.id, 'Произошла ошибка! Попробуйте снова:')
        bot.register_next_step_handler(message, request_imgs)


def request_count(message):
    global imgs_requests
    images = []
    try:
        res = str(message.text)
        res = res.replace(',', '.')
        count_request = int(float(res))
        if count_request > 25:
            bot.send_message(message.chat.id, 'МНОГО! Ограничимся 25 картинками.')
            count_request = 25
        requests_imgs_requests = img_request(imgs_requests[message.chat.id], count_request)
        for src in requests_imgs_requests:
            response = requests.get(src, stream=True)
            images.append(response.raw.read())
        for img_count in range(len(requests_imgs_requests)):
            bot.send_photo(message.chat.id, images[img_count])
    except:
        bot.send_message(message.chat.id, 'Произошла ошибка! Возможно вы ввели некоррекное значение. Попробуйте снова:')
        bot.register_next_step_handler(message, request_count)


@bot.message_handler(commands=['dem'])
def dem_info(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username
    command = '/dem'
    time_normal = str(datetime.today().time())[:8]
    date_normal = datetime.today().date()
    sql = f'INSERT INTO request_logs(user_id, chat_id, username, command, time_normal, date_normal) VALUES(?,?,?,?,?,?)'
    sql_insert(sql, [user_id, chat_id, username, command, time_normal, date_normal])
    bot.send_message(message.chat.id, 'Отправьте картинку для демотивирования:')
    bot.register_next_step_handler(message, dem_photo)


def dem_photo(message):
    global dem_photos
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        downloaded_file = Image.open(io.BytesIO(downloaded_file))
        dem_photos[message.from_user.id] = downloaded_file
        bot.send_message(message.chat.id, 'Отлично! Какой большой текст вы хотите увидеть?')
        bot.register_next_step_handler(message, dem_big_text)
    else:
        bot.send_message(message.chat.id, 'Кажется, вы отправили не фотографию. Попробуйте снова:')
        bot.register_next_step_handler_by_chat_id(message.chat.id, dem_photo)


def dem_big_text(message):
    global big_texts
    if message.content_type == 'text':
        big_texts[message.from_user.id] = message.text
        bot.send_message(message.chat.id, 'Превосходно! Какой малый текст вы хотите увидеть?')
        bot.register_next_step_handler_by_chat_id(message.chat.id, dem_small_text)
    else:
        bot.send_message(message.chat.id, 'Похоже, что вы не ввели текст или ввели не текст. Попробуйте снова:')
        bot.register_next_step_handler_by_chat_id(message.chat.id, dem_big_text)


def dem_small_text(message):
    global small_texts
    if message.content_type == 'text':
        small_texts[message.from_user.id] = message.text
        bot.send_message(message.chat.id, 'Замечательно! Мы начали обработку вашего запроса...')
        get_dem(message)
    else:
        bot.send_message(message.chat.id, 'Похоже, что вы не ввели текст или ввели не текст. Попробуйте снова:')
        bot.register_next_step_handler_by_chat_id(message.chat.id, dem_small_text)


def get_dem(message):
    global dem_photos
    global big_texts
    global small_texts
    dem_photo = dem_photos[message.chat.id]
    big_text = big_texts[message.chat.id]
    small_text = small_texts[message.chat.id]
    dem = create_dem(dem_photo, big_text, small_text)
    if dem is not None:
        bot.send_photo(message.chat.id, dem)
    else:
        bot.send_message(message.chat.id, 'А, нет, не замечательно. Произошла ошибка! Возможно, один из ваших вводов был некорректным.')


bot.infinity_polling()
