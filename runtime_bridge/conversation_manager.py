class ConversationManager:
    def __init__(self, max_history=12):
        self.history = []
        self.max_history = max_history
        self.active = False
        self.original_query = ''

    def start_session(self, user_content, query):
        self.history = [{'role': 'user', 'content': user_content}]
        self.active = True
        self.original_query = query

    def add_user(self, content):
        self.history.append({'role': 'user', 'content': content})
        self._trim()

    def add_assistant(self, content):
        self.history.append({'role': 'assistant', 'content': content})
        self._trim()

    def get_messages(self, system_content):
        return [{'role': 'system', 'content': system_content}] + self.history[-10:]

    def clear(self):
        self.history = []
        self.active = False
        self.original_query = ''

    def _trim(self):
        while len(self.history) > self.max_history:
            self.history.pop(0)