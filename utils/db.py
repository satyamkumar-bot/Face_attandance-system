import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

@st.cache_resource
def get_db() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")

    if not url:
        try:
            url = st.secrets["SUPABASE_URL"]
        except Exception:
            url = ""

    if not key:
        try:
            key = st.secrets["SUPABASE_KEY"]
        except Exception:
            key = ""

    if not url or not key:
        st.error(f"Supabase credentials missing. Checked: {ENV_PATH}")
        st.stop()

    try:
        return create_client(url, key)
    except Exception as e:
        st.error(f"Supabase connection failed: {type(e).__name__}: {e}")
        st.stop()