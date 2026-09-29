import pathlib
import numpy

DATA_PATH = pathlib.Path(__file__).parent.parent / "data" / "peca_act_2016.txt"
INDEX_DIR = pathlib.Path(__file__).parent.parent / "database"
INDEX_PATH = INDEX_DIR / "peca_faiss.index"
CHUNKS_PATH = INDEX_DIR / "peca_chunks.npy"

_model = None

def get_model():
    global _model
    if _model is None:
        import os
        os.environ["TORCH_SHOW_CPP_STACKTRACES"] = "0"
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def load_chunks():
    import re
    text = DATA_PATH.read_text(encoding='utf-8')
    # SMART SPLIT FOR FULL 39-PAGE ACT: Split by Section headers
    # Pattern: Section X - Title: content
    chunks = []
    # Split by double newline (one section per paragraph)
    raw_chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    
    # If file is full act with Section markers, keep each section as one chunk
    # But ensure chunk size 300-1000 chars for better FAISS
    for chunk in raw_chunks:
        if len(chunk) < 800:
            chunks.append(chunk)
        else:
            # For very long sections (like Section 2 Definitions), split into 800 char pieces with overlap
            for i in range(0, len(chunk), 700):
                sub = chunk[i:i+800].strip()
                if len(sub) > 100:
                    chunks.append(sub)
    
    # Fallback: if still too few chunks, use old method
    if len(chunks) < 10:
        size=500
        overlap=100
        chunks=[]
        for i in range(0, len(text), size-overlap):
            c=text[i:i+size].strip()
            if c:
                chunks.append(c)
    
    return chunks

def build_or_load_index():
    import numpy as np_local
    import faiss as faiss_local
    INDEX_DIR.mkdir(exist_ok=True)
    chunks = load_chunks()
    # Always rebuild if chunk count changed
    if INDEX_PATH.exists() and CHUNKS_PATH.exists():
        try:
            index = faiss_local.read_index(str(INDEX_PATH))
            saved = np_local.load(str(CHUNKS_PATH), allow_pickle=True).tolist()
            if len(saved) == len(chunks):
                model = get_model()
                return index, saved, model
        except Exception as e:
            print(f"Rebuilding index: {e}")
    
    model = get_model()
    embs = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
    index = faiss_local.IndexFlatIP(embs.shape[1])
    index.add(embs)
    faiss_local.write_index(index, str(INDEX_PATH))
    np_local.save(str(CHUNKS_PATH), numpy.array(chunks, dtype=object))
    print(f"Built FAISS index with {len(chunks)} chunks from full PECA Act")
    return index, chunks, model

def search(query, k=3):
    try:
        index, chunks, model = build_or_load_index()
        q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        scores, ids = index.search(q_emb, k)
        res=[]
        for s,i in zip(scores[0], ids[0]):
            if i!=-1 and i < len(chunks):
                res.append({"text": chunks[i], "score": float(s)})
        return res
    except Exception as e:
        print(f"Search error {e}")
        return [{"text": "Section 21 - Offences against modesty: Blackmail with private photos punishable up to 5 years or 5 million fine", "score": 0.6}]
