from pathlib import Path
import chromadb
from app.services.document_service import load_and_chunk_documents
from app.services.embedding_service import create_embedding

CHROMA_PATH = Path("chroma_db")
COLLECTION_NAME = "srmist_documents"

def _get_client_and_collection():
    try:
        client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        collection = client.get_or_create_collection(name=COLLECTION_NAME)
        return client, collection
    except Exception as e:
        print(f"Error connecting to ChromaDB: {e}")
        raise

client, collection = _get_client_and_collection()

def get_stats():
    try:
        count = collection.count()
        results = collection.get(include=["metadatas"])
        sources = set()
        if results and results.get("metadatas"):
            for meta in results["metadatas"]:
                if meta and "source" in meta:
                    sources.add(meta["source"])
        return {
            "collection_name": COLLECTION_NAME,
            "total_chunks": count,
            "total_documents": len(sources),
            "sources": list(sources)
        }
    except Exception as e:
        print(f"Error getting vector store stats: {e}")
        return {"collection_name": COLLECTION_NAME, "total_chunks": 0, "total_documents": 0, "sources": []}

def reset_collection():
    try:
        client.delete_collection(name=COLLECTION_NAME)
        global collection
        collection = client.create_collection(name=COLLECTION_NAME)
        print(f"Collection {COLLECTION_NAME} reset successfully.")
    except Exception as e:
        print(f"Error resetting collection: {e}")

def build_vector_store():
    chunks = load_and_chunk_documents()
    if not chunks:
        return 0
    ids = []
    documents = []
    embeddings = []
    metadatas = []
    for index, chunk in enumerate(chunks):
        ids.append(f"chunk_{index}")
        documents.append(chunk["text"])
        embeddings.append(create_embedding(chunk["text"]))
        metadatas.append({"source": chunk["source"]})
    try:
        collection.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
        return len(chunks)
    except Exception as e:
        print(f"Error building vector store: {e}")
        return 0

def search(query: str, top_k: int = 3):
    try:
        query_embedding = create_embedding(query)
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
        retrieved = []
        if not results or not results.get("documents") or not results["documents"][0]:
            return retrieved
            
        for i in range(len(results["documents"][0])):
            retrieved.append({
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "score": results["distances"][0][i]
            })
        return retrieved
    except Exception as e:
        print(f"Error searching vector store: {e}")
        return []

if __name__ == "__main__":
    stats = get_stats()
    print("Vector Store Stats:", stats)