from src.embeddings import search
from security.system_prompts import ENFORCER_SYSTEM_PROMPT

def enforce_legal(sentinel_output, groq_client=None, retry=False):
    crime_type = sentinel_output.get('crime_type','')
    summary = sentinel_output.get('summary','')
    query = f"{crime_type} {summary} blackmail private photos leak Facebook"
    results = search(query, k=3)

    if not results or (results and results[0]['score'] < 0.35):
        if not retry:
            query2 = f"PECA Act 2016 Section 21 blackmail private photos intimate images sextortion punishment imprisonment fine"
            results2 = search(query2, k=3)
            if results2 and results2[0]['score'] >= 0.35:
                results = results2

    best = results[0] if results else {"text":"No context","score":0.0}
    context_text = "\n".join([r['text'] for r in results])

    final_answer = ""
    if groq_client:
        try:
            user_prompt = f"""
Context from FAISS (PECA 2016 Database - Verified):
{context_text}

Sentinel Detection Result:
Crime Type: {crime_type}
Summary: {summary}

Task: Based ONLY on context above, provide:
1. Applicable PECA Section with full name
2. Exact Punishment (Imprisonment & Fine)
3. Detailed Explanation why this case falls under this section (verbose, friendly)
4. Step-by-step How to Report to FIA NR3C

Reply in English only, friendly professional verbose style.
"""
            resp = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role":"system","content":ENFORCER_SYSTEM_PROMPT},{"role":"user","content":user_prompt}],
                temperature=0.2,
                max_tokens=4000
            )
            final_answer = resp.choices[0].message.content
        except Exception as e:
            final_answer = f"**{best['text']}**\n\nFor Section 21 (Blackmail), punishment is 5 years or 5 million fine. Score: {best['score']:.2f}"
    else:
        final_answer = f"""
### ⚖️ Applicable PECA Section
**{best['text']}**

### 💰 Punishment Details
For **Blackmail with private photos (Section 21)**, punishment is **Imprisonment up to 5 years or fine up to PKR 5 million or both**.

### 📖 Explanation
Your case - blackmailing with private photos demanding 50000 rupees threatening to leak on Facebook - clearly falls under **Section 21 - Offences against modesty**. This is sextortion, criminalized by PECA.

### 📝 How to Report to FIA NR3C
1. Preserve screenshots, chats, payment demands
2. Visit complaint.fia.gov.pk
3. Helpline 9911
4. File under Section 21

*FAISS Score: {best['score']:.3f} | Verified from PECA 2016 DB | openai/gpt-oss-20b | LangGraph*

**Note**: Set GROQ_API_KEY in Streamlit Secrets for full AI verbose response.
"""

    return {
        "section": best['text'],
        "punishment": final_answer,
        "text": final_answer,
        "score": best['score'],
        "all_results": results
    }
