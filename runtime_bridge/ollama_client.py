import ollama

class OllamaClient:
    def __init__(self, model='llama3.2:3b'):
        self.model = model

    def call(self, prompt):
        response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']