import telebot
from config import TOKEN, keys
from extensions import APIException, CryptoConverter

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands = ["start", "help"])
def starthelp(message: telebot.types.Message):
    text = """Добрый день!
Вы находитесь в Телеграм-боте, предназначенным для конвертации валют.
Бот принимает информацию в формате:
<ВАЛЮТА1> <ВАЛЮТА2> <КОЛИЧЕСТВО>
Присутствуют три вспомогательные команды:
/start, /help - выводят описание бота.
/values - выводит список допустимых валют для конвертации.
"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands = ["values"])
def val(message: telebot.types.Message):
    text = "Для конвертации доступны следующие валюты:\n"
    cnt = 0
    for key, value in keys.items():
        cnt += 1
        text += f"{cnt}. {key} ({value})\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(content_types = ["text", ])
def inpt(message: telebot.types.Message):
    try:
        inpttext = message.text.split(" ")
        if len(inpttext) != 3:
            raise APIException("Неверное количество передаваемых параметров!\n")
        quote, base, amount = inpttext
        total_base = CryptoConverter.get_price(quote, base, amount)
    except APIException as e:
        bot.reply_to(message, f"Ошибка пользователя!\n{e}")
    else:
        text = f"На данный момент стоимость {amount} {quote} в валюте {base} составляет {total_base} {keys[base]}."
        bot.send_message(message.chat.id, text)
    
bot.polling(non_stop = True)