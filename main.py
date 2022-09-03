import telebot as t

# bot token
TOKEN = "5509147566:AAHkkNmkFBBl6dAbP1Sij_Y1WxRIcpL49WU"

# shi van - author of this bot
shi_van_id = 979305074
bot = t.TeleBot(TOKEN)
hi_sticker = 'CAACAgIAAxkBAAEFqBZjBT9eq-0nTaWATr0XVRxvOcxREgACThQAAkxXMUhokB7iAfvxHykE'

bot.send_message(shi_van_id, 'Bot started')

# importing admins ids from admins.txt
with open('admins.txt', 'r', encoding="utf-8") as reg:
    admins = set(map(int, reg.readlines()))

# adding ban words (such as "сливы курсов") from ban_words.txt
with open('ban_words.txt', 'r', encoding="utf-8") as reg:
    ban_words = reg.readlines()
    for i in range(len(ban_words)):
        ban_words[i] = ban_words[i][:-1]
    ban_words = set(ban_words)

# adding obscene words from bad_words.txt
# downloaded this list of words from the first site
with open('bad_words.txt', 'r', encoding="utf-8") as reg:
    bad_words = reg.read().split(', ')
    bad_words = set(bad_words)

# importing bad_users ids and their number of warnings from pred.txt
bad_users_id = dict()
with open('pred.txt', 'r', encoding="utf-8") as reg:
    users = reg.readlines()
    for user in users:
        user = user.split()
        bad_users_id[int(user[0])] = int(user[1])


# __________________________________________________
# Bot logic

def warning(message, bad):
    if bad in bad_users_id:
        bad_users_id[bad] += 1
        with open('pred.txt', 'a', encoding="utf-8") as wrn:
            print(bad, " ", bad_users_id[bad], file=wrn)
        if bad_users_id[bad] >= 5:
            bot.ban_chat_member(message.chat.id, bad)
        else:
            bot.send_message(message.chat.id,
                             f'У пользователя {message.from_user.first_name} теперь {bad_users_id[bad]} предупреждений')
    else:
        bad_users_id[bad] = 1
        with open('pred.txt', 'a', encoding="utf-8") as wrn:
            print(bad, " ", bad_users_id[bad], file=wrn)
        bot.send_message(message.chat.id,
                         f'У пользователя {message.from_user.first_name} теперь {bad_users_id[bad]} предупреждений')


@bot.message_handler(commands=['start'])
def start_message(message):
    if message.chat.type == "private":
        bot.send_message(979305074, f'{message.from_user.first_name} (@{message.from_user.username} pressed /start)')
        bot.send_message(message.chat.id, 'Привет, это бот-модер для чатов Умскула!\n'
                                          'Наша цель - избавиться от спама и рассылок\n'
                                          'Чтобы использовать бота:\n'
                                          '1. Добавьте его в чат и выдайте админские права\n'
                                          '2. Напишите @shi_van_ufo, чтобы он выдал вам права\n'
                                          '/help для списка команд')


@bot.message_handler(commands=['help'])
def help_message(message):
    if message.chat.type == "private":
        bot.send_message(message.chat.id, '/ban или /бан в ответ на сообщение банит пользователя \n'
                                          '/warn или /пред в ответ на сообщение выдает предпреждение и удаляет '
                                          'сообщение пользователя '
                                          'и выдает ему предупреждение, после 5 предупреждений пользователь вылетает\n'
                                          '/admin в ответ на сообщение выдает админа пользователю\n'
                                          'Все эти команды работают только если @shi_van_ufo выдал вам права\n\n'
                                          'Так же бот автоматом выдает предупреждения за маты и ссылки (и удаляет '
                                          'сообщения), '
                                          'и банит за слова "слив курсов", "бесплатный предбанник" и т.п.')


@bot.message_handler(commands=['ban', 'бан'])
def ban_message(message):
    if message.from_user.id in admins or message.from_user.is_bot:
        if message.reply_to_message:
            bot.delete_message(message.chat.id, message.reply_to_message.message_id)
            bot.delete_message(message.chat.id, message.message_id)
            bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            bot.send_message(message.chat.id,
                             f'Пользователь был исключен за нарушение правил')


# issuing warnings
@bot.message_handler(commands=['warn', 'пред'])
def warn_message(message):
    if message.from_user.id in admins or message.from_user.is_bot:
        if message.reply_to_message:
            warning(message.reply_to_message, message.reply_to_message.from_user.id)
            bot.delete_message(message.chat.id, message.reply_to_message.message_id)
            bot.delete_message(message.chat.id, message.message_id)


# adding new admins
@bot.message_handler(commands=['admin'])
def admin_message(message):
    if message.from_user.id in admins:
        if message.reply_to_message:
            admins.add(message.reply_to_message.from_user.id)
            with open('admins.txt', 'a', encoding="utf-8") as adm:
                print(message.reply_to_message.from_user.id, file=adm)


@bot.message_handler(content_types='text')
def message_reply(message):
    if message.chat.type == "private":
        bot.send_message(shi_van_id, f'{message.from_user.first_name}: {message.text}')

    message_text = str(message.text.lower())

    # greeting users with a sticker
    if message_text == 'привет, бот':
        bot.send_sticker(message.chat.id, hi_sticker, message.id)

    # checking the message for spam mailing (ban words)
    for word in ban_words:
        if word in message_text and len(word) > 1:
            if message.from_user.id not in admins:
                bot.kick_chat_member(message.chat.id, message.from_user.id)
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id,
                                 f'Пользователь {message.from_user.first_name}'
                                 f'был исключен за подозрительное поведение ('
                                 f'возможно спам рассылка)')
            return 0

    # checking the message for obscene words (bad words)
    for word in bad_words:
        if word in message_text:
            if message.from_user.id not in admins:
                warning(message, message.from_user.id)
                bot.delete_message(message.chat.id, message.message_id)
                return 0

    # removing links from the chat
    if 'https://t.me' in message_text and message.from_user.id not in admins and not message.from_user.is_bot:
        warning(message, message.from_user.id)
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, 'Если ссылка полезная, можете скинуть ее в лс модеру')


bot.infinity_polling()
