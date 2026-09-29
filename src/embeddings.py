import pathlib
from sentence_transformers import SentenceTransformer
import faiss, numpy as np
DATA_PATH=pathlib.Path(__file__).parent.parent/"data"/"peca_act_2016.txt"
INDEX_DIR=pathlib.Path(__file__).parent.parent/"database"
INDEX_PATH=INDEX_DIR/"peca_faiss.index"
CHUNKS_PATH=INDEX_DIR/"peca_chunks.npy"
_model=None
def get_model():
    global _model
    if _model is None:
        _model=SentenceTransformer('all-MiniLM-L6-v2')
    return _model
def load_chunks():
    text=DATA_PATH.read_text()
    return [text[i:i+500].strip() for i in range(0,len(text),420) if text[i:i+500].strip()]
def build_or_load_index():
    INDEX_DIR.mkdir(exist_ok=True)
    model=get_model();chunks=load_chunks()
    if INDEX_PATH.exists():
        index=faiss.read_index(str(INDEX_PATH))
        saved=np.load(str(CHUNKS_PATH),allow_pickle=True).tolist()
        return index,saved,model
    emb=model.encode(chunks,convert_to_numpy=True,normalize_embeddings=True)
    index=faiss.IndexFlatIP(emb.shape[1]);index.add(emb)
    faiss.write_index(index,str(INDEX_PATH))
    import numpy as np
    np.save(str(CHUNKS_PATH),np.array(chunks,dtype=object))
    return index,chunks,model
def search(query,k=3):
    index,chunks,model=build_or_load_index()
    q_emb=model.encode([query],convert_to_numpy=True,normalize_embeddings=True)
    scores,ids=index.search(q_emb,k)
    return [{"text":chunks[i],"score":float(s)} for s,i in zip(scores[0],ids[0]) if i!=-1]
