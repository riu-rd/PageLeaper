import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="PageWise - Authentication",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide the sidebar navigation
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Check if user is already authenticated and redirect
if st.session_state.authenticated:
    st.switch_page("pages/1_dashboard.py")

# Display title and tagline
st.title("PageWise")
st.caption("Ask more, scroll less.")

# Create authentication form
with st.container():
    password = st.text_input("Password", type="password", key="password_input")
    
    if st.button("Enter", use_container_width=True):
        # Get password from environment variable
        correct_password = os.getenv("PASSWORD")
        
        if password == correct_password:
            # Set authentication state
            st.session_state.authenticated = True
            # Trigger immediate re-run to redirect
            st.rerun()
        else:
            # Display error message
            st.error("Invalid password.")

# Footer
st.markdown("---")
st.markdown("Created by Darius Vincent Ardales", help="PageWise - Ask more, scroll less.")