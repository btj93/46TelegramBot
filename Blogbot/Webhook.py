import telebot
# from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from Blogbot.IO import readData, addData, deleteData, blogfilename
from Blogbot import telegram
import time

botToken = telegram.nogiblogbotToken
btjchat_id = '396277982'
webhookURL = 'https://jeffrey76.pythonanywhere.com/' + botToken

bot = telebot.TeleBot(token=botToken, threaded=False)

editsublist_text = "請選擇心儀成員 選擇後即可接收到blog更新及showroom提示"
help_text_group = "簡介:\n此bot提供乃木坂46, 櫻坂46, 日向坂成員blog更新及showroom提示\n使用者可依照個人喜好選擇接收(訂閱)哪些成員的資訊 (預設為無)\n私訊及群組對話皆可使用 (群組對話只有管理員可以修改訂閱列表)\n\n指令一覽:\n/help@NogiBlog_bot - 顯示此頁面\n/editsublist@NogiBlog_bot - 編輯訂閱列表\n\n如有任何問題請聯絡:https://t.me/btj93"
help_text_private = "簡介:\n此bot提供乃木坂46, 櫻坂46, 日向坂成員blog更新及showroom提示\n使用者可依照個人喜好選擇接收(訂閱)哪些成員的資訊 (預設為無)\n私訊及群組對話皆可使用 (群組對話只有管理員可以修改訂閱列表)\n\n指令一覽:\n/help - 顯示此頁面\n/editsublist - 編輯訂閱列表\n\n如有任何問題請聯絡:https://t.me/btj93"
no_permission_text = "親 你沒有此權限哦"

logfilename = "access.log"

def checkPermission(chat_id, user_id):
    if chat_id == user_id or user_id in list(map(lambda o: o.user.id, bot.get_chat_administrators(chat_id))) or str(user_id) == btjchat_id:
        return True


def getLog():
    file = Path(logfilename)
    file.touch(exist_ok=True)
    return file.read_text()


def appendLog(record):
    with open(logfilename, 'a') as fp:
        print(record, file=fp)


# app = Flask(__name__)

def process(data):
    update = telebot.types.Update.de_json(data)
    bot.process_new_updates([update])

# @app.route(f'/{botToken}', methods=['POST'])
# def webhook():
#     update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
#     bot.process_new_updates([update])
#     return 'ok', 200


# @bot.message_handler(commands=['start', 'help'])
# def handle_start_help(message):
#     telegram.send_text(message.chat.id, help_text_group)
#     # telegram.send_text(telegram.logchat_id, message)


@bot.message_handler(func=lambda message: message.text is not None and ((message.chat.type == "private" and ("/start" in message.text or "/help" in message.text)) or ("/start@NogiBlog_bot" in message.text or "/help@NogiBlog_bot" in message.text)))
def handle_start_help(message):
    if message.chat.type == "private":
        telegram.send_text(message.chat.id, help_text_private)
    else:
        telegram.send_text(message.chat.id, help_text_group)



def gen_markup_first_layer(a=False, b=False, c=False):
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(*(InlineKeyboardButton(a, callback_data=f'1 {a}') for a in ['乃木坂46', '櫻坂46', '日向坂46']))
    return markup


def gen_markup_second_layer(chat_id, group):
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(*(InlineKeyboardButton(f"{'✓ ' if str(chat_id) in val else ''}{key}",
                                      callback_data=f"{'✓' if str(chat_id) in val else ''}{key} {group}") for key, val
                 in
                 readData(blogfilename)[group].items()))
    markup.add(InlineKeyboardButton("+all", callback_data=f"+all {group}"))
    markup.add(InlineKeyboardButton("-all", callback_data=f"-all {group}"))
    markup.add(InlineKeyboardButton("back", callback_data=f"back"))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        if checkPermission(call.message.chat.id, call.from_user.id):
            telegram.send_text(telegram.logchat_id, f"Group name: {call.message.chat.title}\nUser: {call.from_user.first_name} {call.from_user.last_name} @{call.from_user.username}\nCallback: {call.data}")
            if "1" in call.data:
                # bot.answer_callback_query(call.id, "Answer is Yes")
                bot.edit_message_text(text=editsublist_text, message_id=call.message.message_id,
                                      chat_id=call.message.chat.id,
                                      reply_markup=gen_markup_second_layer(call.message.chat.id,
                                                                           call.data.split(" ")[1]))
            elif "back" in call.data:
                bot.edit_message_text(text=editsublist_text, message_id=call.message.message_id,
                                      chat_id=call.message.chat.id,
                                      reply_markup=gen_markup_first_layer())
            elif "+all" in call.data:
                group = call.data.split(' ')[1]
                if addData(group, '*', call.message.chat.id):
                    bot.edit_message_text(text=editsublist_text, message_id=call.message.message_id,
                                          chat_id=call.message.chat.id,
                                          reply_markup=gen_markup_second_layer(call.message.chat.id, group))
            elif "-all" in call.data:
                group = call.data.split(' ')[1]
                if deleteData(group, '*', call.message.chat.id):
                    bot.edit_message_text(text=editsublist_text, message_id=call.message.message_id,
                                          chat_id=call.message.chat.id,
                                          reply_markup=gen_markup_second_layer(call.message.chat.id, group))
            else:
                group = call.data.split(' ')[1]
                if '✓' in call.data:
                    member = call.data.split(' ')[0].replace('✓', '')
                    if deleteData(group, member, call.message.chat.id):
                        bot.edit_message_text(text=editsublist_text, message_id=call.message.message_id,
                                      chat_id=call.message.chat.id,
                                      reply_markup=gen_markup_second_layer(call.message.chat.id, group))
                else:
                    member = call.data.split(' ')[0]
                    if addData(group, member, call.message.chat.id):
                        bot.edit_message_text(text=editsublist_text, message_id=call.message.message_id,
                                      chat_id=call.message.chat.id,
                                      reply_markup=gen_markup_second_layer(call.message.chat.id, group))
    except Exception as e:
        print(e)


@bot.message_handler(commands=['editsublist'])
def handle_editsublist(message):
    if checkPermission(message.chat.id, message.from_user.id):
        telegram.send_text(message.chat.id, editsublist_text, markup=gen_markup_first_layer())
    else:
        telegram.send_text(message.chat.id, no_permission_text)


@bot.message_handler(commands=['getchatid'])
def handle_getchatid(message):
    chatid = message.chat.id
    if str(message.from_user.id) == btjchat_id:
        telegram.send_text(btjchat_id, chatid)
