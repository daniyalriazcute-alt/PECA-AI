import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

# FIX: set_page_config MUST BE FIRST st command - before any other st.* call
st.set_page_config(page_title="PECA-Guard - Dual Agent", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

import os
from dotenv import load_dotenv
load_dotenv()
from src.auth import register_user, login_user
from security.firewall import check_injection, get_blocked_message
from src.graph import run_dual_agents

# GROQ client - FIXED proxies error
groq_client = None
api_key = os.getenv("GROQ_API_KEY")
try:
    if not api_key and hasattr(st, 'secrets') and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except:
    pass

if api_key:
    try:
        from groq import Groq
        groq_client = Groq(api_key=api_key)
    except Exception as e:
        print(f"GROQ init failed: {e}")  # DON'T use st.warning here!
        groq_client = None

# ... rest of your dark neon UI code same as before ...
# (Use the full file I saved at /mnt/data/peca-ai-final/app.py)
