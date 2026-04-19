import ollama
import json

class OllamaClient:
    def __init__(self, model='llama3.2:3b'):
        self.model = model

    def call(self, prompt, tools=None):
        messages = [{'role': 'user', 'content': prompt}]
        while True:
            response = ollama.chat(model=self.model, messages=messages, tools=tools)
            if 'tool_calls' in response['message']:
                for tool_call in response['message']['tool_calls']:
                    tool_name = tool_call['function']['name']
                    args = tool_call['function']['arguments']
                    if tool_name == 'calculator':
                        result = self._calculate(args.get('expression', ''))
                        messages.append({'role': 'tool', 'content': str(result)})
                    else:
                        messages.append({'role': 'tool', 'content': 'Unknown tool'})
                # Continue conversation
            else:
                return response['message']['content']

    def _calculate(self, expression):
        try:
            # Simple eval for basic math
            return eval(expression, {"__builtins__": None}, {})
        except:
            return "Error in calculation"
