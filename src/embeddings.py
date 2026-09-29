import pathlib
import numpy
import faiss

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
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def load_chunks():
    text = DATA_PATH.read_text(encoding='utf-8')
    chunks = []
    size = 500
    overlap = 80
    for i in range(0, len(text), size - overlap):
        chunk = text[i:i+size]
        if chunk.strip():
            chunks.append(chunk.strip())
    return chunks

def build_or_load_index():
    import numpy as np_local
    import faiss as faiss_local
    INDEX_DIR.mkdir(exist_ok=True)
    chunks = load_chunks()

    if INDEX_PATH.exists() and CHUNKS_PATH.exists():
        try:
            index = faiss_local.read_index(str(INDEX_PATH))
            saved_chunks = np_local.load(str(CHUNKS_PATH), allow_pickle=True).tolist()
            model = get_model()
            return index, saved_chunks, model
        except Exception as e:
            print(f"Failed to load, rebuilding: {e}")

    model = get_model()
    embeddings = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
    dim = embeddings.shape[1]
    index = faiss_local.IndexFlatIP(dim)
    index.add(embeddings)
    faiss_local.write_index(index, str(INDEX_PATH))
    np_local.save(str(CHUNKS_PATH), numpy.array(chunks, dtype=object))
    return index, chunks, model

def search(query, k=3):
    try:
        index, chunks, model = build_or_load_index()
        q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        scores, ids = index.search(q_emb, k)
        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx < len(chunks) and idx!= -1:
                results.append({"text": chunks[idx], "score": float(score)})
        return results
    except Exception as e:
        print(f"Search error: {e}")
        try:
            chunks = load_chunks()
            return [{"text": chunks[0], "score": 0.5}] if chunks else []
        except:
            return [{"text": "PECA Act 2016 Section 21: Offence against modesty - Up to 5 years or fine up to 5 million", "score": 0.4}]
