from src.embeddings import search
from security.system_prompts import ENFORCER_SYSTEM_PROMPT
def enforce_legal(sentinel_output,groq_client=None,retry=False):
    query=f"{sentinel_output.get('crime_type','')} {sentinel_output.get('summary','')}"
    results=search(query,k=3)
    if not results or results[0]['score']<0.35:
        if not retry:
            r2=search(f"PECA punishment for {sentinel_output.get('crime_type')}",k=3)
            if r2 and r2[0]['score']>=0.35:
                results=r2
            else:
                return {"text":"Not found","punishment":"Not available in database","score":0.0}
    best=results[0];context="\n".join([r['text'] for r in results])
    final=f"Section: {best['text']}\nScore: {best['score']:.2f}"
    if groq_client:
        try:
            resp=groq_client.chat.completions.create(model="openai/gpt-oss-20b",messages=[{"role":"system","content":ENFORCER_SYSTEM_PROMPT},{"role":"user","content":f"Context: {context}\nDetection: {sentinel_output}"}],temperature=0.2,max_tokens=4000)
            final=resp.choices[0].message.content
        except:
            pass
    return {"punishment":final,"text":final,"score":best['score']}
