import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="PageWise - Dashboard",
    page_icon="📖",
    layout="wide",
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

# Check authentication status
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Access denied. Please log in on the main page.")
    st.switch_page("main.py")

# Create header with Exit button
col1, col2 = st.columns([10, 1])
with col1:
    st.title("Dashboard")
with col2:
    if st.button("Exit", key="exit_button"):
        # Clear authentication status
        st.session_state.authenticated = False
        # Navigate back to main page
        st.switch_page("main.py")

# Main dashboard content
st.write("Hello, Dashboard!")