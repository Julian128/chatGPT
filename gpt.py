import openai

class gpt:
    temperature = 0.7
    maxTokens = 1024
    frequencyPenalty = 0
    presencePenalty = 0.6
    maxContext = 8
    currentModel = "gpt-3.5-turbo"  # gpt-4, gpt-3.5-turbo
    customInstruction = ""
    conversation = []

    def __init__(self, openaiToken):
        openai.api_key = openaiToken
        
    def getInstruction(self, userName) -> str:
        return f"A chat between {userName} and an AI assistant. The current model is {self.currentModel}. It is okay to call the user by their name." + self.customInstruction

    def changeModel(self, modelName):
        self.currentModel = modelName 

    def getResponse(self, userName, prompt) -> str:
        messages = [{"role": "system", "content": self.getInstruction(userName)}]
        for prevPrompt, prevResponse in self.conversation[-self.maxContext:]:
            messages.extend(
                (
                    {"role": "user", "content": prevPrompt},
                    {"role": "assistant", "content": prevResponse},
                )
            )
        messages.append({"role": "user", "content": prompt})
        # functions = [
        #         {
        #             "name": "changeModel",
        #             "description": "Change the model to use (gpt-4, gpt-3.5-turbo)", 
        #             "parameters": {
        #                 "type": "object",
        #                 "properties": {
        #                     "modelName": {
        #                         "type": "string",
        #                         "description": "The gpt model to use",
        #                     }
        #                 },
        #                 "required": ["modelName"],
        #             },
        #         }
        #     ]
        
        completion = openai.ChatCompletion.create(
            model=self.currentModel,
            messages=messages,
            # functions=functions,
            temperature=self.temperature,
            max_tokens=self.maxTokens,
            top_p=1,
            frequency_penalty=self.frequencyPenalty,
            presence_penalty=self.presencePenalty,
        )

        response = completion.choices[0].message.content
        self.conversation.append((prompt, response))
        tokensIn = completion.usage.prompt_tokens
        tokensOut = completion.usage.completion_tokens
        # print(completion)
        # if response["function_call"]:
        #     if response["function_call"]["name"] == "changeModel":
        #         self.changeModel(response["function_call"]["parameters"]["modelName"])
        #         self.sendMessage(self.message["chatId"], f"Model changed to {self.CURRENT_MODEL}")

        return response, tokensIn, tokensOut


    # gpt4          - 8192 tokens   - €0.03/€0.06 per 1000 tokens in and out  - €0.05 per prompt
    # gpt4-32k      - 32768 tokens  - €0.20 per 1000 tokens in and out  - €0.10 per prompt
    # gpt-3.5-turbo - 8192 tokens   - €0.003/€0.004 per 1000 tokens in and out  - €0.005 per prompt
