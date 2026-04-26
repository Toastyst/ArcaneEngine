import chromadb
import ollama
import os
import json
from utils import log_info

class RAGManager:
    def __init__(self, config):
        self.config = config
        self.chroma_path = config.get('chroma_path', 'chroma_db')
        self.client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = self.client.get_or_create_collection(name="tsm_data")

    def embed_text(self, text):
        response = ollama.embeddings(model='nomic-embed-text', prompt=text)
        return response['embedding']

    def upsert_data(self, data):
        documents = []
        metadatas = []
        ids = []
        for section, section_data in data.items():
            for scope_key, details in section_data.items():
                metrics = self._extract_metrics(section, details)
                doc = f"TSM {section} {scope_key}:\nKey metrics: {metrics}\nFull: {json.dumps(details, default=str, indent=2)[:2000]}"
                documents.append(doc)
                metadatas.append({"section": section, "scope": scope_key})
                ids.append(f"{section}_{scope_key}")
        if documents:
            embeddings = [self.embed_text(doc) for doc in documents]
            self.collection.upsert(documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids)
            log_info(f"RAG upsert: {len(documents)} documents added")

    def _extract_metrics(self, section, details):
        if section == 'inventory':
            qtys = [int(v) for v in details.values() if isinstance(v, (int, str)) and str(v).isdigit()] if isinstance(details, dict) else []
            total_qty = sum(qtys)
            top_items = sorted([(k, int(v)) for k, v in details.items() if isinstance(v, (int, str)) and str(v).isdigit()], key=lambda x: x[1], reverse=True)[:3] if isinstance(details, dict) else []
            return f"Total qty: {total_qty}, top: {', '.join([f'{k}:{v}' for k,v in top_items])}"
        elif section == 'accounting':
            total_sales = sum(len(v) for v in details.values() if isinstance(v, list))
            return f"Total sales entries: {total_sales}"
        elif section == 'groups':
            total_items = len(details.get('collapsed', {})) if isinstance(details, dict) else 0
            return f"Items in group: {total_items}"
        else:
            return "Data available"

    def retrieve(self, query, n_results=5):
        query_embedding = self.embed_text(query)
        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
        log_info(f"Query results keys: {list(results.keys())}")
        if 'documents' in results and results['documents']:
            chunks = results['documents'][0] if len(results['documents']) > 0 else []
        else:
            chunks = []
        log_info(f"RAG retrieve for '{query}': {len(chunks)} chunks returned")
        return chunks
