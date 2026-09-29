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

st.set_page_config(page_title="PECA-Guard", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
.glass { background: rgba(17,24,39,0.7); backdrop-filter: blur(16px); border: 1px solid rgba(0,217,255,0.2); border-radius:16px; }
.chat-bubble-user { background: linear-gradient(135deg,#00D9FF22,#00FF8822); border:1px solid #00D9FF44; border-radius:16px 16px 0 16px; padding:14px; margin:10px 0 10px auto; max-width:80%; }
.chat-bubble-agent1 { background: rgba(0,217,255,0.08); border-left:3px solid #00D9FF; border-radius:0 16px 16px 16px; padding:16px; margin:10px 0; }
.chat-bubble-agent2 { background: rgba(0,255,136,0.08); border-left:3px solid #00FF88; border-radius:0 16px 16px 16px; padding:16px; margin:10px 0; }
.firewall-card { background:white; border-left:5px solid #EF4444; border-radius:12px; padding:20px; color:#111827; }
.status-dot { width:10px; height:10px; border-radius:50%; display:inline-block; }
</style>
""", unsafe_allow_html=True)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated=False
    st.session_state.user=None
    st.session_state.chat_history=[]

def is_greeting(t):
    t=t.strip().lower()
    return t in ["hi","hello","hey","salam","aoa"] or t.startswith(("hi ","hello "))

def instant_greeting():
    return "Hello! I'm PECA-Guard Assistant powered by **openai/gpt-oss-20b** on GROQ. I have dual agents: Sentinel for detection and Enforcer for legal punishment. How can I help?"

if not st.session_state.authenticated:
    col1,col2=st.columns([1.2,0.8])
    with col1:
        st.markdown("<h1>🛡️ PECA-Guard</h1><h2>Dual AI Justice System</h2><p>PECA Act 2016 | openai/gpt-oss-20b | No threats blocked, no latency</p>")
    with col2:
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
                    st.error("Invalid")
        with tab2:
            name=st.text_input("Full Name",key="reg_name")
            email2=st.text_input("Email",key="reg_email")
            pwd2=st.text_input("Password",type="password",key="reg_pwd")
            if st.button("Create Account",use_container_width=True):
                ok,msg=register_user(name,email2,pwd2)
                st.success(msg) if ok else st.error(msg)
    st.stop()

with st.sidebar:
    st.markdown(f'<b>{st.session_state.user["name"]}</b><br><span class="status-dot" style="background:#00FF88"></span> openai/gpt-oss-20b',unsafe_allow_html=True)
    if st.button("Logout"):
        st.session_state.authenticated=False
        st.rerun()

for item in st.session_state.chat_history:
    st.markdown(f'<div class="chat-bubble-user">{item["user"]}</div>',unsafe_allow_html=True)
    if item.get("agent1"):
        a1=item["agent1"]
        st.markdown(f'<div class="chat-bubble-agent1"><b>{a1["crime_type"]} ({a1["confidence"]*100:.0f}%)</b><br>{a1["summary"]}</div>',unsafe_allow_html=True)
    if item.get("agent2"):
        a2=item["agent2"]
        st.markdown(f'<div class="chat-bubble-agent2"><b>Legal Enforcer</b><br>{a2["punishment"]}</div>',unsafe_allow_html=True)
    if item.get("blocked"):
        b=item["blocked"]
        st.markdown(f'<div class="firewall-card"><b style="color:#DC2626">{b["title"]}</b><p>{b["message"]}</p></div>',unsafe_allow_html=True)

user_input=st.chat_input("Describe incident...")
if user_input:
    if is_greeting(user_input):
        st.session_state.chat_history.append({"user":user_input,"agent2":{"punishment":instant_greeting(),"score":1.0}})
        st.rerun()
    is_inj,_,_=check_injection(user_input)
    if is_inj:
        st.session_state.chat_history.append({"user":user_input,"blocked":get_blocked_message()})
        st.rerun()
    result=run_dual_agents(user_input,groq_client)
    st.session_state.chat_history.append({"user":user_input,"agent1":result["agent1_output"],"agent2":result["agent2_output"]})
    st.rerun()
