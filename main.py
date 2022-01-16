from telegram import *
from telegram.ext import *
import logging
import psycopg2 as pg2
import re

'''config'''
token = "1867156840:AAG841XbuHlP6KVTasGYXpf9SUGhtJq8zVc"
bot = Bot(token)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

host = 'ec2-3-233-7-12.compute-1.amazonaws.com'
database = 'd5eq8q0mlqoblu'
user_database = 'iyuckjkrlerfwj'
password = 'd6917a96198a1a2e780212478ca10d22c6bae254a694be848a9ef3e66c77bb3a'

keyboard = [["/talktoangel", "/talktomortal", "/getmortal"]]

''''''''


class Account:
    def __init__(
            self,
            username=None,
            name=None,
            roomnumber=None,
            chat_id=None,
            gender=None,
            preference=None,
            key=None):
        self.name = name
        self.username = username
        self.roomNumber = roomnumber
        self.chat_id = chat_id
        self.gender = gender
        self.preference = preference
        self.key = key


class Destination:
    def __init__(
            self,
            destination=None,
            sender=None):
        self.destination = destination
        self.sender = sender


updater = Updater(token, use_context=True)
dispatcher = updater.dispatcher
print(Bot.get_me(bot))

ROOMNUMBER, GENDER, PREFERENCE, KEY = range(4)

newAccountDict = {}


def input_id_into_newAccountDict(username):
    if username not in newAccountDict:
        newAccountDict[username] = Account()


def start(update: Update, _: CallbackContext):
    username = update.effective_message.from_user.username
    input_id_into_newAccountDict(username)
    user = update.message.from_user
    logger.info("User %s started the bot", user.username)
    username = update.effective_chat.username
    name = update.effective_chat.full_name
    chat_id = update.effective_chat.id
    newAccount = newAccountDict[username]
    newAccount.username = username
    newAccount.name = name
    newAccount.chat_id = chat_id
    update.message.reply_text(
        'Please key in your ROOM NUMBER', )
    return ROOMNUMBER


def roomnumber(update: Update, _: CallbackContext):
    username = update.effective_message.from_user.username
    user = update.message.from_user
    trueOrFalse = checkvalidroomnumber(update.message.text.upper(), update)
    if trueOrFalse is False:
        return ROOMNUMBER
    logger.info("Room Number of %s: %s", user.username, update.message.text.upper())
    newAccount = newAccountDict[username]
    newAccount.roomnumber = update.message.text.upper()
    genderList = ['Male', 'Female', 'Others']
    keyboard = []
    for i in genderList:
        keyboard.append([InlineKeyboardButton(i, callback_data=str(i))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please state your gender:', reply_markup=reply_markup)
    return GENDER


def gender(update: Update, _: CallbackContext):
    username = update.effective_chat.username
    newAccount = newAccountDict[username]
    query = update.callback_query
    query.edit_message_text(text=f"Selected option: {query.data}")
    gender = str(query.data)
    newAccount.gender = gender
    update.effective_message.reply_text(
        "Please enter your Angel Mortal Key", )
    return KEY


def key(update: Update, _: CallbackContext):
    username = update.effective_chat.username
    newAccount = newAccountDict[username]
    trueOrFalse = checkvalidkey(update.message.text.lower(), update)
    if trueOrFalse is False:
        return KEY
    newAccount.key = update.message.text.lower()
    update.effective_message.reply_text(
        "Do you have any preferred mortal :D (can't guarantee your allocation though) \nType in a name or simply "
        "respond with a 'No'.", )
    return PREFERENCE


def preference(update: Update, _: CallbackContext):
    username = update.effective_message.from_user.username
    preference = update.message.text.capitalize()
    newAccount = newAccountDict[username]
    newAccount.preference = preference
    conn = pg2.connect(host=host, database=database,
                       user=user_database,
                       password=password)
    cur = conn.cursor()
    insert_account = '''
           INSERT INTO accounts(username, name, roomnumber, chat_id, gender, preference,key)
            VALUES (%s, %s, %s, %s, %s, %s,%s)
            ON CONFLICT (username) DO NOTHING
            '''
    cur.execute(insert_account,
                (newAccount.username, newAccount.name,
                 newAccount.roomnumber, newAccount.chat_id,
                 newAccount.gender, newAccount.preference, newAccount.key))
    conn.commit()
    insert_list = '''
           INSERT INTO list(self,key)
            VALUES ((SELECT id FROM accounts 
                    WHERE accounts.username = %s), %s )
                    ON CONFLICT (self) DO NOTHING
            '''
    cur.execute(insert_list,
                (newAccount.username, newAccount.key))
    conn.commit()
    conn.close()
    update.message.reply_text(
        "Your account has been registered, please wait for further instructions for us to allocate the angel and mortal or visit @eusoffmods_bot if you have not already done so!", )
    return ConversationHandler.END


dictionary = {}


def talktoangel(update: Update, _: CallbackContext):
    isRegisteredAccount = checkregisteredaccount(update.effective_message.chat_id, update)
    if isRegisteredAccount is False:
        return
    conn = pg2.connect(host=host, database=database,
                       user=user_database,
                       password=password)
    cur = conn.cursor()
    getAngelId = '''
    SELECT Chat_id FROM accounts
    WHERE accounts.id =(SELECT Angel FROM list
    WHERE Self = (SELECT id FROM accounts
                  WHERE accounts.username = %s))
    '''
    try:
        cur.execute(getAngelId,
                    (update.effective_chat.username,))
        data = cur.fetchone()[0]
        if update.effective_chat.username not in dictionary:
            dictionary[update.effective_chat.username] = {"Angel": "", "Mortal": "", "sender": ""}
        dictionary[update.effective_chat.username]["Angel"] = data
        dictionary[update.effective_chat.username]["sender"] = 'Mortal'
        update.message.reply_text('You are now sending messages to your Angel')
    except Exception:
        update.message.reply_text(
            'Please wait for your angel and mortal to be allocated before sending message and also visit @eusoffmods_bot if you have not already done so!')


def talktomortal(update: Update, _: CallbackContext):
    conn = pg2.connect(host=host, database=database,
                       user=user_database,
                       password=password)
    cur = conn.cursor()
    getMortalId = '''
    SELECT Chat_id FROM accounts
    WHERE accounts.id = (SELECT Mortal FROM list
    WHERE Self = (SELECT id FROM accounts
                  WHERE accounts.username = %s))
    '''
    try:
        cur.execute(getMortalId,
                    (update.effective_chat.username,))
        data = cur.fetchone()[0]
        if update.effective_chat.username not in dictionary:
            dictionary[update.effective_chat.username] = {"Angel": "", "Mortal": "", "sender": ""}
        dictionary[update.effective_chat.username]["Mortal"] = data
        dictionary[update.effective_chat.username]["sender"] = 'Angel'
        update.message.reply_text('You are now sending messages to your Mortal')
    except Exception:
        update.message.reply_text(
            'Please wait for your angel and mortal to be allocated before sending message and also visit @eusoffmods_bot if you have not already done so!')


def sendmessage(update: Update, context):
    isRegisteredAccount = checkregisteredaccount(update.effective_message.chat_id, update)
    if isRegisteredAccount is False:
        return
    try:
        sender = dictionary[update.effective_chat.username]["sender"]
        text = update.message.text
        if sender == 'Angel':
            dest = dictionary[update.effective_chat.username]["Mortal"]
        elif sender == 'Mortal':
            dest = dictionary[update.effective_chat.username]["Angel"]
        else:
            update.message.reply_text(
                "Specify /talktoangel or /talktomortal",
                reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        context.bot.send_message(chat_id=dest, text=sender + ": " + text)
    except Exception:
        update.message.reply_text(
            "Specify /talktoangel or /talktomortal",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))


def sendsticker(update: Update, context):
    isRegisteredAccount = checkregisteredaccount(update.effective_message.chat_id, update)
    if isRegisteredAccount is False:
        return
    try:
        sender = dictionary[update.effective_chat.username]["sender"]
        message_id = update.message.message_id
        chat_id = update.message.chat_id
        if sender == 'Angel':
            dest = dictionary[update.effective_chat.username]["Mortal"]
        elif sender == 'Mortal':
            dest = dictionary[update.effective_chat.username]["Angel"]
        else:
            update.message.reply_text(
                "Specify /talktoangel or /talktomortal",
                reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        context.bot.send_message(chat_id=dest, text=sender + " sent a sticker!")
        bot.copy_message(dest, chat_id, message_id)
    except Exception:
        update.message.reply_text(
            "Specify /talktoangel or /talktomortal",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))


def sendphoto(update: Update, context):
    isRegisteredAccount = checkregisteredaccount(update.effective_message.chat_id, update)
    if isRegisteredAccount is False:
        return
    try:
        sender = dictionary[update.effective_chat.username]["sender"]
        photo = update.message.photo[0]
        print(photo)
        if sender == 'Angel':
            dest = dictionary[update.effective_chat.username]["Mortal"]
        elif sender == 'Mortal':
            dest = dictionary[update.effective_chat.username]["Angel"]
        else:
            update.message.reply_text(
                "Specify /talktoangel or /talktomortal",
                reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        context.bot.send_message(chat_id=dest, text=sender + " sent a photo!")
        context.bot.send_photo(chat_id=dest, photo=photo)
    except Exception:
        update.message.reply_text(
            "Specify /talktoangel or /talktomortal",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))


def sendvideo(update: Update, context):
    isRegisteredAccount = checkregisteredaccount(update.effective_message.chat_id, update)
    if isRegisteredAccount is False:
        return
    try:
        sender = dictionary[update.effective_chat.username]["sender"]
        video = update.message.video
        if sender == 'Angel':
            dest = dictionary[update.effective_chat.username]["Mortal"]
        elif sender == 'Mortal':
            dest = dictionary[update.effective_chat.username]["Angel"]
        else:
            update.message.reply_text(
                "Specify /talktoangel or /talktomortal",
                reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        context.bot.send_message(chat_id=dest, text=sender + " sent a video!")
        context.bot.send_video(chat_id=dest, video=video)
    except Exception:
        update.message.reply_text(
            "Specify /talktoangel or /talktomortal",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))


def sendvideonote(update: Update, context):
    isRegisteredAccount = checkregisteredaccount(update.effective_message.chat_id, update)
    if isRegisteredAccount is False:
        return
    try:
        sender = dictionary[update.effective_chat.username]["sender"]
        videoNote = update.message.video_note
        if sender == 'Angel':
            dest = dictionary[update.effective_chat.username]["Mortal"]
        elif sender == 'Mortal':
            dest = dictionary[update.effective_chat.username]["Angel"]
        else:
            update.message.reply_text(
                "Specify /talktoangel or /talktomortal",
                reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        context.bot.send_message(chat_id=dest, text=sender + " sent a telebubble!")
        context.bot.send_video_note(chat_id=dest, video_note=videoNote)
    except Exception:
        update.message.reply_text(
            "Specify /talktoangel or /talktomortal",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))


def sendvoice(update: Update, context):
    isRegisteredAccount = checkregisteredaccount(update.effective_message.chat_id, update)
    if isRegisteredAccount is False:
        return
    try:
        sender = dictionary[update.effective_chat.username]["sender"]
        voice = update.message.voice
        if sender == 'Angel':
            dest = dictionary[update.effective_chat.username]["Mortal"]
        elif sender == 'Mortal':
            dest = dictionary[update.effective_chat.username]["Angel"]
        else:
            update.message.reply_text(
                "Specify /talktoangel or /talktomortal",
                reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        context.bot.send_message(chat_id=dest, text=sender + " sent a voice!")
        context.bot.send_voice(chat_id=dest, voice=voice)
    except Exception:
        update.message.reply_text(
            "Specify /talktoangel or /talktomortal",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command. Please "
                                                                    "type /cancel to restart this.")


def cancel(update, context):
    update.message.reply_text(
        'Cancelled', reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
    )
    return ConversationHandler.END


def checkvalidroomnumber(roomnumber, update):
    m = re.match(r"([ABCDE][1234][012][0-9])", roomnumber)
    try:
        start, stop = m.span()
        if stop - start == len(roomnumber):
            return True
        else:
            bot.send_message(chat_id=update.effective_chat.id,
                             text="It appears that you have inputted an invalid room number, please only enter a valid "
                                  "room number "
                                  ".")
            return False
    except Exception:
        bot.send_message(chat_id=update.effective_chat.id,
                         text="It appears that you have inputted an invalid roomnumber, please only enter a valid "
                              "roomnumber "
                              ".")
        return False


def checkvalidkey(key, update):
    validKey = ["dblock"]
    if key in validKey:
        return True
    else:
        bot.send_message(chat_id=update.effective_chat.id,
                         text="It appears that you have inputted an invalid key, please check with your block head "
                              "for the valid key")
        return False


def test(update: Update, _: CallbackContext):
    bot.send_message(chat_id=update.effective_chat.id,
                     text=str(
                         update.effective_chat.id) + " " + update.effective_chat.username + " " + update.effective_chat.full_name)


def getmortal(update: Update, _: CallbackContext):
    conn = pg2.connect(host=host, database=database,
                       user=user_database,
                       password=password)
    cur = conn.cursor()
    getMortalId = '''
        SELECT username, name, roomnumber FROM accounts
        WHERE accounts.id = (SELECT Mortal FROM list
        WHERE Self = (SELECT id FROM accounts
                      WHERE accounts.username = %s))
        '''
    cur.execute(getMortalId,
                (update.effective_chat.username,))
    try:
        data = cur.fetchall()[0]
        update.message.reply_text(
            'Your mortal: ' + data[1] + '(' + data[0] + ')\n' + 'Room Number: ' + data[
                2] + '\nGo on, ask them what their '
                     'likes and dislikes are and '
                     'get to know them!')
    except Exception:
        update.message.reply_text(
            'Please wait for your angel and mortal to be allocated before sending message and also visit @eusoffmods_bot if you have not already done so!')


def notLaunched(update: Update, _: CallbackContext):
    update.message.reply_text(
        'Please wait for your angel and mortal to be allocated before sending message and also visit @eusoffmods_bot if you have not already done so!')


registeredAccountSet = set()


def checkregisteredaccount(chat_id, update):
    if chat_id in registeredAccountSet:
        return True

    else:
        conn = pg2.connect(host=host, database=database,
                           user=user_database,
                           password=password)
        cur = conn.cursor()
        getChatId = '''
            SELECT chat_id FROM accounts
            '''
        cur.execute(getChatId)
        data = cur.fetchall()
        for id in data:
            id = id[0]
            if id not in registeredAccountSet:
                registeredAccountSet.add(id)

    if chat_id in registeredAccountSet:
        return True

    else:
        bot.send_message(chat_id=update.effective_chat.id,
                         text="Please register first with /start")
        return False


MESSAGE = range(1)

def getparticipant(update: Update):
    conn = pg2.connect(host=host, database=database,
                       user=user_database,
                       password=password)
    cur = conn.cursor()
    get_subscriber = '''
            select chat_id from accounts
    '''
    cur.execute(get_subscriber)
    data = cur.fetchall()
    list = []
    for participant in data:
        list.append(participant[0])
    return list


def adminsend(update: Update, context):
    update.message.reply_text(
        'Please enter admin message')
    return MESSAGE


def messagesend(update: Update, context):
    text = update.message.text
    participantList = getparticipant(update)
    for participant in participantList:
        bot.send_message(chat_id=participant, text= "Admin: " + text)
    return ConversationHandler.END


def main():
    createAccount = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ROOMNUMBER: [MessageHandler(Filters.text & ~Filters.command, roomnumber)],
            GENDER: [CallbackQueryHandler(gender)],
            KEY: [MessageHandler(Filters.text, key)],
            PREFERENCE: [MessageHandler(Filters.text, preference)]
        },
        fallbacks=[CommandHandler('cancel', cancel)], )
    dispatcher.add_handler(createAccount)

    adminMessage = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("^(Admin Message)$"), adminsend)],
        states={
            MESSAGE: [MessageHandler(Filters.text & ~Filters.command, messagesend)],
        },
        fallbacks=[CommandHandler('cancel', cancel)], )
    dispatcher.add_handler(adminMessage)

    cancelHandler = CommandHandler("cancel", cancel)
    dispatcher.add_handler(cancelHandler)

    notLaunchedHandler = MessageHandler(Filters.text, notLaunched)
    dispatcher.add_handler(notLaunchedHandler)

    angelHandler = CommandHandler("talktoangel", talktoangel)
    dispatcher.add_handler(angelHandler)

    mortalHandler = CommandHandler("talktomortal", talktomortal)
    dispatcher.add_handler(mortalHandler)

    getMortalHandler = CommandHandler('getmortal', getmortal)
    dispatcher.add_handler(getMortalHandler)

    sendMessage = MessageHandler(Filters.text, sendmessage)
    dispatcher.add_handler(sendMessage)

    sendSticker = MessageHandler(Filters.sticker, sendsticker)
    dispatcher.add_handler(sendSticker)

    sendPhoto = MessageHandler(Filters.photo, sendphoto)
    dispatcher.add_handler(sendPhoto)

    sendVideo = MessageHandler(Filters.video, sendvideo)
    dispatcher.add_handler(sendVideo)

    sendVideoNote = MessageHandler(Filters.video_note, sendvideonote)
    dispatcher.add_handler(sendVideoNote)

    sendVoice = MessageHandler(Filters.voice, sendvoice)
    dispatcher.add_handler(sendVoice)

    # unknownHandler = CommandHandler(Filters.command, unknown)
    # dispatcher.add_handler(unknownHandler)

    testHandler = CommandHandler('test', test)
    dispatcher.add_handler(testHandler)
    updater.start_polling()


if __name__ == '__main__':
    main()
