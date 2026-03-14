import streamlit as st
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def show_header(text_title: str):
    # Layout: logo + title side by side
    col1, col2 = st.columns([1, 6])
    
    with col1:
        st.image(f"{BASE_DIR}/imagenes/UPlogo.jpg", width=200)
        
    with col2:
        st.title(text_title)
        st.caption("📘 Developed for: *Business Intelligence (Graduate Level)*")
        st.caption("Universidad Panamericana")
