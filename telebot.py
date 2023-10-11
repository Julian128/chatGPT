import requests
import time
import os
import pickle
import numpy as np

from gpt import gpt

class TeleBot:
    def __init__(self, telegramApiKey, openaiApiKey):
        self.apiUrl: str = f"https://api.telegram.org/bot{telegramApiKey}/"
        self.message: dict = {
                "text": "",
                "name": "",
                "chatId": 0,
                "date": 0
                }
        self.printOut: bool = True
        self.baseCost: float = 0.0025
        self.userUsage: dict[int, float] = {}
        self.blockedUsers: list[int] = []

        self.gpt: gpt = gpt(openaiApiKey)

        if (os.path.exists("userUsage.pickle")):
            self.userUsage = pickle.load(open("userUsage.pickle", "rb"))

    def update(self) -> requests.Response:
        params: dict[str, int] = {"timeout": 0, "offset": 30}
        resp = requests.get(f"{self.apiUrl}getUpdates", params)
        if resp.status_code != 200:
            raise Exception(f"Error: {resp.status_code}")
        return resp.json()['result']

    def sendMessage(self, chatId, text) -> requests.Response:
        params: dict = {"chat_id": chatId, "text": text}
        return requests.post(f"{self.apiUrl}sendMessage", params)

    # return a dict with the message info if there is a new message
    def readMessage(self) -> dict:
        # print("Waiting for message...", end="\r")
        if resp := self.update():
            resp = resp[-1]["message"]
            msg = {
                "text": resp["text"],
                "name": resp["from"]["first_name"],
                "chatId": resp["from"]["id"],
                "date": resp["date"]
                }
            
            if msg["chatId"] in self.blockedUsers:
                return None

            if self.message and (msg['date'] > self.message['date'] and msg['date'] > time.time() - 15):
                self.message = msg
                self.addUser()
                return msg

    def addUser(self):
        id = int(self.message["chatId"])
        if id not in self.userUsage:
            self.userUsage[id] = 0
    
    def addUsage(self, tokensIn, tokensOut):
        id = int(self.message["chatId"])
        if self.gpt.currentModel == "gpt-4":
            self.userUsage[id] += tokensIn / 1000 * 0.03 + tokensOut / 1000 * 0.06 + self.baseCost
        elif self.gpt.currentModel == "gpt-3.5-turbo":
            self.userUsage[id] += tokensIn / 1000 * 0.003 + tokensOut / 1000 * 0.004 + self.baseCost
        else:
            raise Exception("Unknown model")

        pickle.dump(self.userUsage, open("userUsage.pickle", "wb"))

        if self.userUsage[id] > np.random.uniform(0.1, 2):
            self.sendMessage(self.message["chatId"], f"You have spent {(self.userUsage[int(self.message['chatId'])]):.2f}€, please pay via paypal: @JMoik or BTC lightning: lnbc1pjjg4jfpp553r4jufltgjfqv49zgkllkpe3aa4p0j6c3242fgkgkvvvtmxhscsdqqcqzzgxqyz5vqrzjqwnvuc0u4txn35cafc7w94gxvq5p3cu9dd95f7hlrh0fvs46wpvhdwj6wqkzdrtgnyqqqqryqqqqthqqpyrzjqw8c7yfutqqy3kz8662fxutjvef7q2ujsxtt45csu0k688lkzu3ldwj6wqkzdrtgnyqqqqryqqqqthqqpysp55d7hu9tuhpsjd07jya6mr3glunl355ft96vcg8d2jhcdtf0jwskq9qypqsqfartftk4fzxrzx58yqh48j68x3qc8wh5n4uyme9s23l0w37ffj2h26zmdz9tk3qxynt5y8na70ce0nny7ek0hm5l2fg76ajxyxj3h7gqjwpw2f")

        if self.userUsage[id] > 2:
            self.blockedUsers.append(id)


    # def commands(self) -> bool:
    #     try:
    #         # split the msg at whitespace and lowercase it
    #         msg = self.message["text"].split()
    #         if msg[0].strip().lower() == "/help":
    #             return True
    #         if msg[0].strip().lower() == "/changemodel":
    #             self.CURRENT_MODEL = msg[1].strip().lower()
    #             self.sendMessage(msg['chatId'], f"Model changed to {msg[1]}")
    #             return True
    #         if msg[0].strip().lower() == "/cost":
    #             if int(self.message['chatId']) not in self.userUsage:
    #                 self.addUser()
    #                 self.sendMessage(self.message['chatId'], f"You have spent €0")
    #             self.sendMessage(self.message['chatId'], f"You have spent €{round(self.userUsage[int(self.message['chatId'])], 3)}")
    #             return True
    #     except Exception as e:
    #         print(e)
    #         return False

    def run(self):
        while True:
            if (msg := self.readMessage()):
                # if self.commands():
                #     continue
                response, tokensIn, tokensOut = self.gpt.getResponse(msg["name"], msg["text"])
                self.addUsage(tokensIn, tokensOut)
                self.sendMessage(msg["chatId"], response)
                if (self.printOut):
                    print(msg["name"], ":", msg["text"])
                    print(response)
            time.sleep(1)
