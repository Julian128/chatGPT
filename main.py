import json
from gpt import gpt

def main():
    with open("keys.json") as apikeys:
       keys = json.load(apikeys)

    model = gpt(keys["OPENAI_KEY"], "llama")#"gpt-3.5-turbo")#"gpt-4-1106-preview")
    model.run()

if __name__ == "__main__":
    main()