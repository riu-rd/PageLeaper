def apply_custom_styles():
    """Apply custom CSS styles"""
    return """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
    </style>
    """