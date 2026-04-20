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
            context += "Relevant TSM Data:\n" + "\n".join(rag_chunks[:3])  # Limit to 3 chunks
            # Summarize key data
            summary = self._summarize_data(rag_chunks)
            if summary:
                context += f"\n\nData Summary: {summary}"
        context += f"\nUser Query: {query}"

        prompt = f"System: {system_prompt}\n\n{context}"
        rag_count = len(rag_chunks) if rag_chunks else 0
        log_info(f"Prompt built: {rag_count} RAG chunks + memory + query")
        try:
            log_info(f"Prompt len: {len(prompt)} chars")
            log_info(f"Prompt preview: {prompt[:200]}...")
        except Exception as e:
            log_info(f"Prompt log error: {e}")
        return prompt

    def _summarize_data(self, chunks):
        inventory = []
        sales = []
        for chunk in chunks:
            if 'bagQuantity' in chunk or 'bankQuantity' in chunk:
                # Extract top items
                import re
                items = re.findall(r'"(i:[^"]+)": (\d+)', chunk)
                inventory.extend([(item, int(qty)) for item, qty in items])
            if 'csvSales' in chunk:
                # Count sales
                lines = chunk.split('\n')
                sales_count = len([l for l in lines if l.strip() and not l.startswith('itemString')])
                sales.append(sales_count)
        summary = []
        if inventory:
            top_inv = sorted(inventory, key=lambda x: x[1], reverse=True)[:5]
            summary.append(f"Inventory: {len(inventory)} items, top: {', '.join([f'{item}:{qty}' for item, qty in top_inv])}")
        if sales:
            summary.append(f"Vendor sales: {sum(sales)} entries")
        return '; '.join(summary)
