import json

from telebot import TeleBot

def main():
    with open("keys.json") as apikeys:
       keys = json.load(apikeys)

    telebot = TeleBot(keys["TELEGRAM_KEY"], keys["OPENAI_KEY"])
    telebot.run()

if __name__ == "__main__":
    main()