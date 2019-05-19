import urllib.request
from bs4 import BeautifulSoup
import sqlite3
import telebot


with open('token.txt') as f:
    token = f.readline()
    bot = telebot.TeleBot(token)


class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"


def generate_list(page):
    opener = AppURLopener()
    response = opener.open('https://www.anekdot.ru/release/anekdot/year/2019/{0}'.format(page))
    html = response.read()
    html = html.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    paragraphs = soup.find_all('div', {'class': "topicbox"})
    anek_list = []
    for item in paragraphs:
        if (item.get('id') != None):
            anek_list.append((int(item.get('id')), item.find('div', {'class': "text"}).text))
    return anek_list


class ListOfJokes:

    def __init__(self):
        self.list = generate_list(1)
        self.index = 0
        self.page = 1
        self.prev_id = -1

    def new_page(self):
        self.index = 0
        self.page += 1
        self.list = generate_list(self.page)

    def increment(self):
        self.prev_id = self.generate_id_joke()
        self.index += 1
        if len(self.list) == self.index:
            self.new_page()

    def get_joke(self):
        return self.list[self.index][1]

    def generate_id_joke(self):
        return self.list[self.index][0]

    def get_joke_from_index(self, id_joke):
        if id_joke == -1:
            return "no previous joke"
        return generate_list(id_joke / 1000)[id_joke % 1000]


A = ListOfJokes()


@bot.message_handler(content_types=['video', 'audio', 'sticker'])
def get_text_messages(message):
    bot.send_message(message.from_user.id, "Я умею только читать(", reply_markup=keyboard1)


@bot.message_handler(commands=['help'])
def get_text_messages(message):
    bot.send_message(message.from_user.id, "/help - получить справку по боту \n"
                                               "/joke - увидеть новую шутку \n"
                                               "/mark - узнать среднюю оценку пользователей \n\n"
                                               "Напиши estimate и оценку от 0 до 10, чтобы оценит анекдот. Например, estimate 8 \n \n"
                                               "Напиши привет, just for fun\n\n"
                                               "/delete - для полной перезагрузки бота для твоего аккаунта\n", reply_markup=keyboard1)

@bot.message_handler(commands=['joke'])
def get_text_messages(message):
    take_new_joke(message)


@bot.message_handler(commands=['start'])
def get_text_messages(message):
    bot.send_message(message.chat.id, 'Привет, ты написал мне /start. Я выдаю лучшие(нет) шутки за 2019 год по версии сайта anekdot.ru. Для информации напиши /help', reply_markup=keyboard1)


@bot.message_handler(commands=['mark'])
def get_text_messages(message):
    bot.send_message(message.chat.id, get_avg_mark(A.prev_id), reply_markup=keyboard1)


@bot.message_handler(commands=['delete'])
def get_text_messages(message):
    delete_history(message.from_user.id)
    bot.send_message(message.chat.id, 'history deleted', reply_markup=keyboard1)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == "привет":
        bot.send_message(message.from_user.id, "Привет, напиши /joke и увидишь несмешную шутку с просторов рунета", reply_markup=keyboard1)
    elif message.text.lower().find('estimate') != -1:
        message.text = message.text.lower()
        bot.send_message(message.chat.id, update_mark(message.chat.id, A.prev_id, message.text.replace('estimate ', '')), reply_markup=keyboard1)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.", reply_markup=keyboard1)


keyboard1 = telebot.types.ReplyKeyboardMarkup(True)
keyboard1.row('/joke', '/mark', '/help')


def take_new_joke(message):
    bot.send_message(message.from_user.id, "Сейчас будет шуточка...")
    while was_read(message.from_user.id, A.generate_id_joke()):
        A.increment()
    bot.send_message(message.from_user.id, A.get_joke(), reply_markup=keyboard1)
    add_sequence(message.from_user.id, A.generate_id_joke())
    A.increment()


def create_tables():
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_jokes (
            id_chat INTEGER,
            id_anek INTEGER,
            mark INTEGER CHECK (mark >= -1 AND mark <= 10)
        )''')
    conn.commit()


def add_sequence(id_chat, id_anek):
    query = '''
            INSERT INTO user_jokes (id_chat, id_anek, mark) VALUES 
                ("{}", "{}", "{}");'''
    query = query.format(id_chat, id_anek, -1)
    cur = conn.cursor()
    cur.execute(query)


def update_mark(id_chat, id_anek, mark):
    try:
        mark = int(mark)
    except ValueError:
        return 'Неправильный формат ввода'
    if mark > 10 or mark < 0:
        return 'Неправильный формат ввода'

    if id_anek < 0:
        return "Нет анекдота до этого"
    query = '''
            UPDATE user_jokes SET mark = {} WHERE id_chat = {} AND id_anek = {} ;'''
    query = query.format(mark, id_chat, id_anek)
    cur = conn.cursor()
    cur.execute(query)
    return 'Ваша оценка обновлена'


def select_all_sequences():
    query = '''SELECT *
               FROM user_jokes'''
    cur = conn.cursor()
    cur.execute(query)

    for row in cur:
        print(row)


def delete_all_history():
    query = '''DELETE FROM user_jokes'''
    cur = conn.cursor()
    cur.execute(query)


def delete_history(id_chat):
    query = '''DELETE
               FROM user_jokes
               WHERE id_chat = {}'''
    query = query.format(id_chat)
    cur = conn.cursor()
    cur.execute(query)


def was_read(id_chat, id_anek):
    query = '''SELECT id_chat
               FROM user_jokes
               WHERE id_chat = {} AND id_anek = {}'''
    query = query.format(id_chat, id_anek)
    cur = conn.cursor()
    cur.execute(query)
    for row in cur:
        return row[0] != None


def get_avg_mark(id_anek):
    if id_anek < 0:
        return "Нет анекдота до этого"
    query = '''SELECT AVG(mark)
               FROM user_jokes
               WHERE id_anek = {} AND mark > -1'''
    query = query.format(id_anek)
    cur = conn.cursor()
    cur.execute(query)
    for row in cur:
        if row[0] == None:
             return 'Оценок нет. Будь первым!'
        return row[0]


with sqlite3.connect('example.db', check_same_thread=False) as conn:
    create_tables()
    bot.polling(none_stop=True, interval=1)
    #select_all_sequences() #вывести бд под конец
    # delete_all_history() #удаление всех строк

