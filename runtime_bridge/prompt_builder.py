from utils import log_info

class PromptBuilder:
    def build(self, query, memory_data="", rag_chunks=None):
        system_prompt = """You are Arcane Agent, a WoW gold-making assistant with access to TSM market data.
- Provide concise, data-driven advice on gold-making strategies.
- Respect market scopes: Region data shows competitive baseline; realm data shows local opportunity.
- Use provided data for prices, volumes, trends.
- Be helpful, accurate, and focused on actionable insights.
- Keep responses under 500 words."""

        context = f"Memory: {memory_data}\n"
        if rag_chunks:
            context += "Relevant Data:\n" + "\n".join(rag_chunks[:3])  # Limit to 3 chunks
        context += f"\nUser Query: {query}"

        prompt = f"System: {system_prompt}\n\n{context}"
        rag_count = len(rag_chunks) if rag_chunks else 0
        log_info(f"Prompt built: {rag_count} RAG chunks + memory + query")
        return prompt
