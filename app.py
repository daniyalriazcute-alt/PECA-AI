import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()
from src.auth import register_user, login_user
from security.firewall import check_injection, get_blocked_message
from src.graph import run_dual_agents

groq_client = None
api_key = os.getenv("GROQ_API_KEY")
try:
    if not api_key and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except:
    pass

if api_key:
    try:
        from groq import Groq
        groq_client = Groq(api_key=api_key)
    except:
        groq_client = None

st.set_page_config(page_title="PECA-Guard - Dual AI Justice System", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

# ========== MOCK DARK NEON UI - EXACT LIKE ORIGINAL MOCK ==========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
.stApp {
    background: #0A0E17!important;
    background-image:
        radial-gradient(at 20% 30%, rgba(0, 217, 255, 0.15) 0px, transparent 50%),
        radial-gradient(at 80% 20%, rgba(0, 255, 136, 0.12) 0px, transparent 50%),
        radial-gradient(at 40% 80%, rgba(0, 217, 255, 0.08) 0px, transparent 50%)!important;
}
* { font-family: 'Inter', sans-serif; }
h1,h2,h3 { color: #FFFFFF!important; }
p, label, span { color: #E5E7EB!important; }
.glass {
    background: rgba(17, 24, 39, 0.7)!important;
    backdrop-filter: blur(16px);
    border: 1px solid rgba(0, 217, 255, 0.2);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    transition: all 0.3s ease;
}
.glass:hover {
    border-color: rgba(0, 217, 255, 0.4);
    box-shadow: 0 8px 32px rgba(0, 217, 255, 0.15);
    transform: translateY(-2px);
}
.neon-title {
    background: linear-gradient(135deg, #00D9FF 0%, #00FF88 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
    font-size: 36px;
}
.chat-bubble-user {
    background: linear-gradient(135deg, rgba(0,217,255,0.15), rgba(0,255,136,0.15));
    border: 1px solid rgba(0,217,255,0.3);
    border-radius: 16px 16px 0 16px;
    padding: 14px;
    margin: 10px 0 10px auto;
    max-width: 80%;
    color: #E5E7EB;
}
.chat-bubble-agent1 {
    background: rgba(0, 217, 255, 0.08);
    border-left: 3px solid #00D9FF;
    border-radius: 0 16px 16px 16px;
    padding: 16px;
    margin: 10px 0;
    color: #E5E7EB;
}
.chat-bubble-agent2 {
    background: rgba(0, 255, 136, 0.08);
    border-left: 3px solid #00FF88;
    border-radius: 0 16px 16px 16px;
    padding: 16px;
    margin: 10px 0;
    color: #E5E7EB;
}
.firewall-card { background: white!important; border-left: 5px solid #EF4444; border-radius: 12px; padding: 20px; color: #111827!important; }
.firewall-card * { color: #111827!important; }
.status-dot { width:10px; height:10px; border-radius:50%; display:inline-block; box-shadow: 0 0 8px currentColor; }
.stTextInput > div > div > input,.stTextArea > div > div > textarea {
    background: rgba(17, 24, 39, 0.8)!important;
    border: 1px solid rgba(0, 217, 255, 0.2)!important;
    color: white!important;
    border-radius: 10px!important;
}
.stButton > button {
    background: linear-gradient(135deg, #00D9FF 0%, #00FF88 100%)!important;
    color: #0A0E17!important;
    font-weight: 700!important;
    border: none!important;
    border-radius: 10px!important;
}
.stTabs [data-baseweb="tab-list"] { background: rgba(17,24,39,0.5); border-radius: 10px; }
.stTabs [aria-selected="true"] { color: #00D9FF!important; }
section[data-testid="stSidebar"] { background: #0F141F!important; border-right: 1px solid rgba(0,217,255,0.1); }
</style>
""", unsafe_allow_html=True)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated=False
    st.session_state.user=None
    st.session_state.chat_history=[]

def is_greeting(t):
    t=t.strip().lower()
    return t in ["hi","hello","hey","salam","aoa","assalamualaikum"] or t.startswith(("hi ","hello ","hey "))

def instant_greeting():
    return "Hello! I'm your PECA-Guard Assistant powered by dual AI agents - **Cyber Sentinel** and **Legal Enforcer** using openai/gpt-oss-20b. How can I assist you today?"

# AUTH PAGE - MOCK DARK
if not st.session_state.authenticated:
    col1,col2=st.columns([1.2,0.8], gap="large")
    with col1:
        st.markdown("""
        <div style="padding:40px 20px">
          <div style="display:flex; align-items:center; gap:12px; margin-bottom:24px">
            <div style="width:48px; height:48px; background:linear-gradient(135deg,#00D9FF,#00FF88); border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:24px; box-shadow: 0 0 20px rgba(0,217,255,0.3)">🛡️</div>
            <div>
              <div class="neon-title">PECA-Guard</div>
              <p style="margin:0; color:#9CA3AF!important; font-size:13px">Pakistan Prevention of Electronic Crimes Act 2016</p>
            </div>
          </div>
          <h1 style="font-size:42px; font-weight:800; line-height:1.1; margin:20px 0; color:white!important">Dual AI Justice System</h1>
          <p style="color:#9CA3AF!important; font-size:16px">Enterprise-grade cybersecurity platform with two specialized AI agents.</p>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:32px">
            <div class="glass"><div style="font-size:20px">🔍</div><div style="font-weight:600; color:white; margin-top:8px">Sentinel Detection</div><div style="font-size:12px; color:#9CA3AF!important">AI detects bullying, stalking, sextortion</div></div>
            <div class="glass"><div style="font-size:20px">⚖️</div><div style="font-weight:600; color:white; margin-top:8px">Enforcer Legal</div><div style="font-size:12px; color:#9CA3AF!important">Exact PECA section, imprisonment & fine</div></div>
            <div class="glass"><div style="font-size:20px">⚡</div><div style="font-weight:600; color:white; margin-top:8px">GROQ Powered</div><div style="font-size:12px; color:#9CA3AF!important">openai/gpt-oss-20b free API, ultra-fast</div></div>
            <div class="glass"><div style="font-size:20px">🛡️</div><div style="font-weight:600; color:white; margin-top:8px">AI Firewall</div><div style="font-size:12px; color:#9CA3AF!important">Prompt injection blocked professionally</div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass" style="padding:32px; margin-top:40px">', unsafe_allow_html=True)
        tab1,tab2=st.tabs(["Login","Register"])
        with tab1:
            email=st.text_input("Email",key="login_email")
            pwd=st.text_input("Password",type="password",key="login_pwd")
            if st.button("Sign In →",use_container_width=True):
                ok,user=login_user(email,pwd)
                if ok:
                    st.session_state.authenticated=True
                    st.session_state.user=user
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        with tab2:
            name=st.text_input("Full Name",key="reg_name")
            email2=st.text_input("Email",key="reg_email")
            pwd2=st.text_input("Password",type="password",key="reg_pwd")
            if st.button("Create Account",use_container_width=True):
                ok,msg=register_user(name,email2,pwd2)
                st.success(msg) if ok else st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# CHAT PAGE - DARK MOCK UI
with st.sidebar:
    st.markdown(f"""
    <div class="glass" style="padding:16px">
      <div style="display:flex; gap:10px; align-items:center">
        <div style="width:36px; height:36px; border-radius:50%; background:linear-gradient(135deg,#00D9FF,#00FF88); display:flex; align-items:center; justify-content:center; color:#0A0E17; font-weight:800">{st.session_state.user['name'][0].upper()}</div>
        <div><div style="font-weight:600; color:white">{st.session_state.user['name']}</div><div style="font-size:11px; color:#9CA3AF">{st.session_state.user['email']}</div></div>
      </div>
      <div style="margin-top:16px; display:flex; gap:8px; align-items:center; font-size:12px; color:#9CA3AF">
        <span class="status-dot" style="background:#00FF88; color:#00FF88"></span> GROQ: openai/gpt-oss-20b
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 💬 Short-Term Memory")
    for i, chat in enumerate(st.session_state.chat_history[-5:][::-1]):
        st.caption(f"{i+1}. {chat['user'][:40]}...")
    if st.button("Logout",use_container_width=True):
        st.session_state.authenticated=False
        st.rerun()

st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; padding:12px 16px; background: rgba(17,24,39,0.5); border: 1px solid rgba(0,217,255,0.1); border-radius:10px; margin-bottom:20px">
  <div style="display:flex; gap:20px">
    <div><span class="status-dot" style="background:#00D9FF; color:#00D9FF"></span><span style="color:white; font-weight:600"> Sentinel</span></div>
    <div><span class="status-dot" style="background:#00FF88; color:#00FF88"></span><span style="color:white; font-weight:600"> Enforcer</span></div>
  </div>
  <div style="font-size:11px; color:#6B7280">FAISS | LangGraph | openai/gpt-oss-20b</div>
</div>
""", unsafe_allow_html=True)

for item in st.session_state.chat_history:
    st.markdown(f'<div class="chat-bubble-user">{item["user"]}</div>', unsafe_allow_html=True)
    if item.get("agent1"):
        a1=item["agent1"]
        st.markdown(f'<div class="chat-bubble-agent1"><b style="color:#00D9FF">Cyber Sentinel - {a1["crime_type"]} ({a1["confidence"]*100:.0f}%)</b><br>{a1["summary"]}</div>', unsafe_allow_html=True)
    if item.get("agent2"):
        a2=item["agent2"]
        st.markdown(f'<div class="chat-bubble-agent2"><b style="color:#00FF88">Legal Enforcer</b><br>{a2["punishment"]}<br><small>FAISS Score: {a2["score"]:.2f} | openai/gpt-oss-20b</small></div>', unsafe_allow_html=True)
    if item.get("blocked"):
        b=item["blocked"]
        st.markdown(f'<div class="firewall-card"><b style="color:#DC2626">{b["title"]}</b><p>{b["message"]}</p></div>', unsafe_allow_html=True)

user_input=st.chat_input("Describe your cyber incident... e.g., Someone blackmailing me with private photos")
if user_input:
    if is_greeting(user_input):
        st.session_state.chat_history.append({"user":user_input,"agent2":{"punishment":instant_greeting(),"score":1.0}})
        st.rerun()
    is_inj,_,_=check_injection(user_input)
    if is_inj:
        st.session_state.chat_history.append({"user":user_input,"blocked":get_blocked_message()})
        st.rerun()
    with st.status("🤖 Dual Agents Working - LangGraph: Goal → Decide → Act → Observe → Complete", expanded=True) as status:
        st.write("🛡️ Sentinel analyzing...")
        result=run_dual_agents(user_input,groq_client)
        st.write(f"⚖️ Enforcer fetching... Score: {result['agent2_output']['score']:.2f}")
        status.update(label="✅ Analysis Complete", state="complete")
    st.session_state.chat_history.append({"user":user_input,"agent1":result["agent1_output"],"agent2":result["agent2_output"]})
    st.rerun()
