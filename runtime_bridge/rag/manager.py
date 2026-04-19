import chromadb
import ollama
import os
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
        # data is dict from provider, e.g., {"item:123": {"region": {...}, "realm": {...}}}
        documents = []
        metadatas = []
        ids = []
        for item_id, scopes in data.items():
            for scope, market in scopes.items():
                doc = f"Item {item_id} {scope} data: {', '.join(f'{k}={v}' for k,v in market.items())}"
                documents.append(doc)
                metadatas.append({"item_id": item_id, "scope": scope})
                ids.append(f"{item_id}_{scope}")
        if documents:
            embeddings = [self.embed_text(doc) for doc in documents]
            self.collection.upsert(documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids)
            log_info(f"RAG upsert: {len(documents)} documents added")

    def retrieve(self, query, n_results=5):
        query_embedding = self.embed_text(query)
        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
        chunks = results['documents'] if results['documents'] else []
        log_info(f"RAG retrieve for '{query}': {len(chunks)} chunks returned")
        return chunks
