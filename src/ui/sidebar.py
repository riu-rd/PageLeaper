import streamlit as st
import time
from src.auth.session import reset_session
from src.config import MODEL_OPTIONS, CONFIG_WARNING, NEW_SESSION_WARNING


def render_configuration_sidebar():
    """Render the configuration sidebar"""
    st.markdown("### ⚙️ Configurations")
    
    # Debug: Show current active configuration
    # st.caption(f"**Active Config:**")
    # st.caption(f"Model: {st.session_state.model_config['model']}")
    # st.caption(f"Temp: {st.session_state.model_config['temperature']}")
    # st.caption(f"Top-K: {st.session_state.model_config['top_k']}")
    # st.caption(f"Top-P: {st.session_state.model_config['top_p']}")
    
    st.divider()
    
    # Model selection
    current_model = st.session_state.model_config['model']
    model_index = 0 if current_model == 'gemini-2.5-flash' else 1
    model_option = st.selectbox(
        "Model",
        list(MODEL_OPTIONS.keys()),
        index=model_index,
        key="model_select"
    )
    new_model = MODEL_OPTIONS[model_option]
    
    # Temperature
    new_temp = st.slider(
        "Temperature",
        min_value=0.1,
        max_value=1.5,
        value=st.session_state.model_config['temperature'],
        step=0.05,
        key="temp_slider"
    )
    
    # Top-K
    new_top_k = st.slider(
        "Top-K",
        min_value=1,
        max_value=500,
        value=st.session_state.model_config['top_k'],
        key="topk_slider"
    )
    
    # Top-P
    new_top_p = st.slider(
        "Top-P",
        min_value=0.00,
        max_value=1.00,
        value=st.session_state.model_config['top_p'],
        step=0.01,
        key="topp_slider"
    )
    
    # Check if configuration changed
    config_changed = (
        new_model != st.session_state.model_config['model'] or
        new_temp != st.session_state.model_config['temperature'] or
        new_top_k != st.session_state.model_config['top_k'] or
        new_top_p != st.session_state.model_config['top_p']
    )
    
    if config_changed:
        if not st.session_state.confirm_apply:
            if st.button("Apply Changes", type="primary", key="apply_config"):
                st.session_state.confirm_apply = True
                st.rerun()
        else:
            st.warning(CONFIG_WARNING)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirm", key="confirm_apply_btn", type="primary"):

                    st.session_state.model_config['model'] = new_model
                    st.session_state.model_config['temperature'] = new_temp
                    st.session_state.model_config['top_k'] = new_top_k
                    st.session_state.model_config['top_p'] = new_top_p
                    
                    reset_session(clear_all=False)
                    
                    st.success("Configuration updated!")
                    time.sleep(0.5)
                    st.rerun()
            with col2:
                if st.button("Cancel", key="cancel_apply_btn"):
                    st.session_state.confirm_apply = False
                    st.rerun()
    
    st.divider()
    
    # New Session button
    if not st.session_state.confirm_new_session:
        if st.button("New Session", type="secondary", key="new_session"):
            st.session_state.confirm_new_session = True
            st.rerun()
    else:
        st.warning(NEW_SESSION_WARNING)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm", key="confirm_new_session_btn", type="primary"):
                reset_session(clear_all=True)
                st.success("New session started!")
                time.sleep(0.5)
                st.rerun()
        with col2:
            if st.button("Cancel", key="cancel_new_session_btn"):
                st.session_state.confirm_new_session = False
                st.rerun()