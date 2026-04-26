from utils import log_info

class PromptBuilder:
    def build(self, query, memory_data="", rag_chunks=None):
        system_prompt = """You are Arcane Agent, a WoW gold-making assistant with access to TSM market data.
- Provide concise, data-driven advice on gold-making strategies.
- Respect market scopes: Region data shows competitive baseline; realm data shows local opportunity.
- Use ALL available data: inventory qtys for posting stacks, csvSales historical prices/volumes for trends, groups for opportunities.
- Even without current prices, suggest based on history/inventory (e.g., post large stacks from inventory, use historical prices for trends).
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

    def build_system(self, query, memory_data, rag_chunks):
        system_prompt = """You are Arcane Agent, a WoW gold-making assistant with access to TSM market data.
- Provide concise, data-driven advice on gold-making strategies.
- Respect market scopes: Region data shows competitive baseline; realm data shows local opportunity.
- Use ALL available data: inventory qtys for posting stacks, csvSales historical prices/volumes for trends, groups for opportunities.
- Even without current prices, suggest based on history/inventory (e.g., post large stacks from inventory, use historical prices for trends).
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

        return f"{system_prompt}\n\n{context}"

    def build_lightweight_system(self, query, memory_data):
        system_prompt = """You are Arcane Agent, a WoW gold-making assistant with access to TSM market data.
- Provide concise, data-driven advice on gold-making strategies.
- Respect market scopes: Region data shows competitive baseline; realm data shows local opportunity.
- Use ALL available data: inventory qtys for posting stacks, csvSales historical prices/volumes for trends, groups for opportunities.
- Even without current prices, suggest based on history/inventory (e.g., post large stacks from inventory, use historical prices for trends).
- Be helpful, accurate, and focused on actionable insights.
- Keep responses under 500 words."""

        context = f"Current Topic: {query}\nMemory: {memory_data}"

        return f"{system_prompt}\n\n{context}"

    def _summarize_data(self, chunks):
        inventory = []
        sales_prices = []
        groups = []
        for chunk in chunks:
            if 'bagQuantity' in chunk or 'bankQuantity' in chunk:
                # Extract top items
                import re
                items = re.findall(r'"(i:[^"]+)": (\d+)', chunk)
                inventory.extend([(item, int(qty)) for item, qty in items])
            if 'csvSales' in chunk:
                # Extract prices
                prices = re.findall(r'"price": (\d+)', chunk)
                sales_prices.extend([int(p) for p in prices])
            if 'collapsed' in chunk:
                # Extract top group items by qty
                collapsed_items = re.findall(r'"(i:[^"]+)": \{"n": "([^"]+)", "q": (\d+)\}', chunk)
                groups.extend([(item, name, int(qty)) for item, name, qty in collapsed_items])
        summary = []
        if inventory:
            top_inv = sorted(inventory, key=lambda x: x[1], reverse=True)[:5]
            summary.append(f"Inventory: {len(inventory)} items, top: {', '.join([f'{item}:{qty}' for item, qty in top_inv])}")
        if sales_prices:
            avg_price = sum(sales_prices) // len(sales_prices) if sales_prices else 0
            summary.append(f"Vendor sales: {len(sales_prices)} entries, avg price: {avg_price}g")
        if groups:
            top_groups = sorted(groups, key=lambda x: x[2], reverse=True)[:5]
            summary.append(f"Groups: {len(groups)} items, top: {', '.join([f'{name}:{qty}' for _, name, qty in top_groups])}")
        return '; '.join(summary)
