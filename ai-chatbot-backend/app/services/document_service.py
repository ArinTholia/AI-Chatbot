from pathlib import Path
import re
try:
    import fitz # PyMuPDF
except ImportError:
    fitz = None

KNOWLEDGE_BASE_DIR = Path("knowledge_base")

def get_document_stats():
    filenames = []
    if KNOWLEDGE_BASE_DIR.exists():
        for file_path in KNOWLEDGE_BASE_DIR.glob("*.txt"):
            filenames.append(file_path.name)
        for file_path in KNOWLEDGE_BASE_DIR.glob("*.pdf"):
            filenames.append(file_path.name)
    return {
        "document_count": len(filenames),
        "filenames": filenames
    }

def load_documents():
    documents = []
    if not KNOWLEDGE_BASE_DIR.exists():
        return documents
        
    # Load TXT files
    for file_path in KNOWLEDGE_BASE_DIR.glob("*.txt"):
        try:
            text = file_path.read_text(encoding="utf-8")
            documents.append({"source": file_path.name, "text": text})
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}")
            
    # Load PDF files
    if fitz:
        for file_path in KNOWLEDGE_BASE_DIR.glob("*.pdf"):
            try:
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text() + "\n"
                documents.append({"source": file_path.name, "text": text})
            except Exception as e:
                print(f"Error reading {file_path.name}: {e}")
    else:
        print("PyMuPDF (fitz) is not installed. PDF files will be ignored.")
        
    return documents

def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        end_idx = min(i + chunk_size, len(words))
        # Try to find a sentence boundary near the end index
        if end_idx < len(words):
            # Look back up to 100 words to find a punctuation mark
            search_start = max(i, end_idx - 100)
            for j in range(end_idx - 1, search_start - 1, -1):
                if words[j].endswith('.') or words[j].endswith('!') or words[j].endswith('?'):
                    end_idx = j + 1
                    break
        
        chunk = " ".join(words[i:end_idx])
        chunks.append(chunk)
        if end_idx == len(words):
            break
        i = end_idx - chunk_overlap
        if i <= 0:
            i = end_idx # Prevent infinite loop if overlap is too large
    return chunks

def load_and_chunk_documents():
    documents = load_documents()
    chunks = []
    for document in documents:
        document_chunks = chunk_text(document["text"])
        for chunk in document_chunks:
            chunks.append({"source": document["source"], "text": chunk})
    return chunks

if __name__ == "__main__":
    stats = get_document_stats()
    print("Document Stats:", stats)
    chunks = load_and_chunk_documents()
    print(f"Created {len(chunks)} chunks.")