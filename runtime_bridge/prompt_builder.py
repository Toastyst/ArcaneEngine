class PromptBuilder:
    def build(self, query, memory_data=""):
        return f"User query: {query}\nMemory: {memory_data}\nArcane Agent – You are a knowledgeable WoW assistant. Answer concisely, accurately, and helpfully about quests, classes, mechanics, and lore."