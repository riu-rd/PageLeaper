import streamlit as st
from google import genai
from src.config import GEMINI_API_KEY


@st.cache_resource
def init_gemini_client():
    """Initialize Google Gemini client"""
    return genai.Client(api_key=GEMINI_API_KEY)