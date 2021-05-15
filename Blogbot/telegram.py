import telebot
import json
from time import sleep

testchat_id = "Insert Chat id here"
logchat_id = btjchat_id
nogiblogbotToken = 'Insert Telegram Bot Token Here'
testbotToken = 'Insert Telegram Bot Token Here'

botToken = nogiblogbotToken

bot = telebot.TeleBot(botToken)


def send_text(chatid, text, markup=None, disable_web_page_preview=False):
    try:
        bot.send_message(chatid, text,
                         disable_web_page_preview=disable_web_page_preview, reply_markup=markup)
    except telebot.apihelper.ApiException as e:
        print(e)
        error = json.loads(e.result.text)
        if error['error_code'] == 429:
            delay = error['parameters']['retry_after']
            print(delay)
            sleep(delay + 5)
            send_text(logchat_id, f"{text} {e}", disable_web_page_preview=True)
            send_text(chatid, text, markup=markup, disable_web_page_preview=disable_web_page_preview)
        elif error['error_code'] == 400 and 'group send failed' in error['description']:
            sleep(5)
            send_text(logchat_id, f"{text} {e}", disable_web_page_preview=True)
            send_text(chatid, text, markup=markup, disable_web_page_preview=disable_web_page_preview)


def send_media_group(chatid, medias):
    try:
        bot.send_media_group(chatid, medias)
    except telebot.apihelper.ApiException as e:
        print(e)
        error = json.loads(e.result.text)
        if error['error_code'] == 429:
            delay = error['parameters']['retry_after']
            print(delay)
            sleep(delay + 5)
            send_text(logchat_id, f'media {e}')
            send_media_group(chatid, medias)
        elif error['error_code'] == 400 and 'group send failed' in error['description']:
            sleep(5)
            send_text(logchat_id, f'media {e}')
            send_media_group(chatid, medias)
