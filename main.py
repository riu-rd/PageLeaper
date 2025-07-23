import streamlit as st
import os
import sys
from dotenv import load_dotenv

from src.config.settings import PAGE_TITLE_MAIN
from src.ui import apply_custom_styles, render_header_main, render_authenticator, render_footer

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

st.set_page_config(
    page_title=PAGE_TITLE_MAIN,
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown(apply_custom_styles(), unsafe_allow_html=True)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if st.session_state.authenticated:
    st.switch_page("pages/1_dashboard.py")

render_header_main()

render_authenticator()

render_footer()