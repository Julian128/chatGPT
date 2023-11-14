from flask import Flask, render_template, request, jsonify
import json
from gpt import gpt
import html

app = Flask(__name__)

with open("keys.json") as apikeys:
    keys = json.load(apikeys)

bot = gpt(keys["OPENAI_KEY"], "llama")
# bot = gpt(keys["OPENAI_KEY"], "gpt-4-1106-preview")
# bot = gpt(keys["OPENAI_KEY"], "gpt-3.5-turbo")

def calcPrice(inputTokens, outputTokens):
    return round(0.01e-3 * inputTokens + 0.03e-3 * outputTokens, 4)

def messageGenerator(message=""):
    ai_response = bot.getLlamaResponse(message, stream=True)
    # return ai_response
    for resp in ai_response:
        nextToken = resp["choices"][0].get("delta").get("content")

        if nextToken is not None:
            print(nextToken, end="", flush=True)
            yield nextToken

gen = messageGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getNextToken', methods=['POST'])
def getNextToken():
    try:
        nextToken = next(gen)
    except StopIteration:
        pass

    return jsonify(result=html.escape(nextToken))

@app.route('/sendPrompt', methods=['POST'])
def sendPrompt():
    message = request.form['message']
    global gen
    gen = messageGenerator(message)
    return jsonify(result="")

if __name__ == '__main__':
    app.run(debug=True, port=5000)