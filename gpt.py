import openai
import time
from llama_cpp import Llama
from utils import loadCustomInstruction
class gpt:
    temperature = 0.7
    maxTokens = 1024
    frequencyPenalty = 0
    presencePenalty = 0.6
    maxContext = 5
    customInstruction = ""
    conversation = []

    def __init__(self, openaiToken, model):
        openai.api_key = openaiToken
        self.model = model
        if model == "llama":
            self.llama = Llama(model_path="/Users/julian/Code/llama.cpp/models/luna-ai-llama2-uncensored.ggmlv3.q8_0.bin", seed=-1, n_ctx=1024)
        
    def getInstruction(self, userName) -> str:
        return f"A chat between {userName} and an AI assistant. The current model is {self.model}." + self.customInstruction

    def changeModel(self, modelName):
        self.model = modelName

    def preparePrompt(self, prompt, userName):
        messages = [{"role": "system", "content": self.getInstruction(userName)}]
        # messages = loadCustomInstruction()
        for prevPrompt, prevResponse in self.conversation[-self.maxContext:]:
            messages.extend(
                (
                    {"role": "user", "content": prevPrompt},
                    {"role": "assistant", "content": prevResponse},
                )
            )
        messages.append({"role": "user", "content": prompt})
        return messages

    def getResponse(self, prompt, userName="user", stream=True) -> str:

        messages = self.preparePrompt(prompt, userName)
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.maxTokens,
            top_p=1,
            frequency_penalty=self.frequencyPenalty,
            presence_penalty=self.presencePenalty,
            stream=stream
        )

        if stream:
            return completion
        
        response = completion.choices[0].message.content
        self.conversation.append((prompt, response))
        tokensIn = completion.usage.prompt_tokens
        tokensOut = completion.usage.completion_tokens
        return response
        
    def getLlamaResponse(self, prompt, userName="user", stream=True) -> str:
        messages = self.preparePrompt(prompt, userName)
        completion = self.llama.create_chat_completion(messages, stream=stream)

        if stream:
            return completion
        
        response = completion.choices[0].message.content
        self.conversation.append((prompt, response))
        tokensIn = completion.usage.prompt_tokens
        tokensOut = completion.usage.completion_tokens
        return response
    
    def run(self, stream=False):
        while True:
            if (prompt := input("You: ")):
                response = self.getLlamaResponse(prompt, stream) if self.model == "llama" else self.getResponse(msg, stream)
                fullResponse = ""
                while True:
                    resp = next(response, {})
                    if resp:
                        nextToken = resp["choices"][0].get("delta").get("content")
                        if nextToken is not None:
                            # yield nextToken
                            print(nextToken, end="", flush=True)
                            fullResponse += nextToken
                    else:
                        self.conversation.append((prompt, fullResponse))
                        print()
                        break
            time.sleep(1)