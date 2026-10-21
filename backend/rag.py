import os
import uuid
from typing import List, Dict, Any

class CompanyKnowledge:
    def __init__(self, persist_directory: str = None):
        if persist_directory is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            persist_directory = os.path.join(base_dir, "db", "vector_db")
        os.makedirs(persist_directory, exist_ok=True)
        self.persist_directory = persist_directory

        self.client = None
        self.collection = None
        self.init_db()

    def init_db(self):
        try:
            import chromadb
            from chromadb.utils import embedding_functions

            self.client = chromadb.PersistentClient(path=self.persist_directory)
            api_key = os.getenv("OPENAI_API_KEY")

            # If a valid OpenAI API key is provided, use OpenAI embeddings
            if api_key and api_key.startswith("sk-") and len(api_key) > 20:
                try:
                    ef = embedding_functions.OpenAIEmbeddingFunction(
                        api_key=api_key,
                        model_name="text-embedding-3-small"
                    )
                    self.collection = self.client.get_or_create_collection(
                        name="company_knowledge",
                        embedding_function=ef
                    )
                    print("[RAG] ChromaDB initialized with OpenAI embeddings.")
                except Exception as ex:
                    print(f"[RAG] OpenAI Embedding failed, falling back to default: {ex}")
                    self.collection = self.client.get_or_create_collection(name="company_knowledge")
            else:
                # Use ChromaDB built-in default embedding function (offline friendly)
                self.collection = self.client.get_or_create_collection(name="company_knowledge")
                print("[RAG] ChromaDB initialized with local default embeddings.")

            # Seed initial company policies if empty
            if self.collection and self.collection.count() == 0:
                self.seed_defaults()
        except Exception as e:
            print(f"[RAG] ChromaDB initialization notice: {e}")
            self.collection = None

    def seed_defaults(self):
        default_docs = [
            {
                "title": "Corporate AI Usage Guidelines",
                "text": "COMSATS IT Policy: Employees are permitted to use approved AI middleware only. All prompts must be sanitized of client CNICs, passwords, and private connection strings prior to processing.",
                "metadata": {"category": "Security", "department": "IT"}
            },
            {
                "title": "Employee Reimbursement SOP",
                "text": "Finance Dept SOP 2026: Official travel and equipment expenses require pre-approval from department heads. Claims must be submitted via the finance portal within 15 calendar days.",
                "metadata": {"category": "Finance", "department": "HR"}
            },
            {
                "title": "Information Classification Standard",
                "text": "Data Security Policy: Company assets are classified into Public, Internal, Confidential, and Restricted. Source code repositories and customer databases are strictly Restricted.",
                "metadata": {"category": "Compliance", "department": "Infosec"}
            }
        ]
        for doc in default_docs:
            self.add_document(text=doc["text"], title=doc["title"], metadata=doc["metadata"])

    def add_document(self, text: str, title: str = "", metadata: dict = None) -> str:
        if not self.collection:
            return ""
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        meta = metadata or {}
        if title:
            meta["title"] = title
        meta["timestamp"] = str(os.path.getmtime(self.persist_directory))

        try:
            self.collection.add(
                documents=[text],
                metadatas=[meta],
                ids=[doc_id]
            )
            return doc_id
        except Exception as e:
            print(f"[RAG] Error adding document: {e}")
            return ""

    def list_documents(self) -> List[Dict[str, Any]]:
        if not self.collection:
            return []
        try:
            data = self.collection.get()
            docs = []
            for i in range(len(data.get("ids", []))):
                docs.append({
                    "id": data["ids"][i],
                    "text": data["documents"][i] if "documents" in data and i < len(data["documents"]) else "",
                    "metadata": data["metadatas"][i] if "metadatas" in data and i < len(data["metadatas"]) else {}
                })
            return docs
        except Exception as e:
            print(f"[RAG] Error listing documents: {e}")
            return []

    def delete_document(self, doc_id: str) -> bool:
        if not self.collection:
            return False
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            print(f"[RAG] Error deleting document: {e}")
            return False

    def query(self, query_text: str, n_results: int = 2) -> List[str]:
        if not self.collection or self.collection.count() == 0:
            return []
        try:
            count = min(n_results, self.collection.count())
            results = self.collection.query(
                query_texts=[query_text],
                n_results=count
            )
            if results and 'documents' in results and len(results['documents']) > 0:
                return results['documents'][0]
            return []
        except Exception as e:
            print(f"[RAG] Error querying knowledge base: {e}")
            return []

# Global RAG instance
knowledge_base = CompanyKnowledge()
