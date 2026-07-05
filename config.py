import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Streamlit Cloud fallback
if OPENWEATHER_API_KEY is None:
    try:
        import streamlit as st
        OPENWEATHER_API_KEY = st.secrets["OPENWEATHER_API_KEY"]
    except Exception:
        OPENWEATHER_API_KEY = None