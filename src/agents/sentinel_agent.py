import json,re
from security.system_prompts import SENTINEL_SYSTEM_PROMPT
def analyze_with_sentinel(user_input,groq_client=None):
    crime_map={"blackmail":"Blackmail Sec 21","photo":"Modesty Sec 21","bully":"Bullying Sec 20","stalk":"Stalking Sec 24","defamation":"Dignity Sec 20"}
    lower=user_input.lower()
    dtype="General Harassment"
    for k,v in crime_map.items():
        if k in lower:
            dtype=v;break
    is_crime=any(k in lower for k in crime_map) or len(lower.split())>5
    if groq_client:
        try:
            resp=groq_client.chat.completions.create(model="openai/gpt-oss-20b",messages=[{"role":"system","content":SENTINEL_SYSTEM_PROMPT},{"role":"user","content":user_input}],temperature=0.2,max_tokens=800)
            text=resp.choices[0].message.content
            m=re.search(r'\{.*\}',text,re.DOTALL)
            if m:
                return json.loads(m.group())
        except:
            pass
    return {"detected":bool(is_crime),"crime_type":dtype,"confidence":0.94 if is_crime else 0.62,"summary":f"Incident indicates {dtype}","peca_keywords":[k for k in crime_map if k in lower]}
