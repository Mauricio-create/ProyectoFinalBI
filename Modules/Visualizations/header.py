"""
# Módulo de Encabezado y Marca

Este módulo centraliza el diseño del encabezado de la aplicación. Su función principal
es renderizar de manera uniforme el logotipo institucional y los metadatos del proyecto 
en la parte superior de todas las vistas.

Utiliza un sistema de columnas de Streamlit para asegurar una alineación profesional
del material gráfico y el texto.
"""
import streamlit as st
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
"""
`Path`: Ruta raíz del proyecto calculada hacia atrás desde la ubicación del módulo 
(`Modules/Visualizations/header.py`) para localizar de forma segura la carpeta de imágenes.
"""

def show_header(text_title: str):
    """
    Renderiza el encabezado institucional en la interfaz de Streamlit.

    **Layout generado:**
    * **Columna 1 (1/7):** Logotipo de la Universidad Panamericana.
    * **Columna 2 (6/7):** Título principal, nivel académico e institución.

    **Args:**
    * `text_title` (str): El título principal que se desea mostrar en el Dashboard.

    **Dependencias:**
    * Requiere que el archivo de imagen `UPlogo.jpg` exista en la carpeta `/imagenes/` 
      en la raíz del proyecto.
    """
    col1, col2 = st.columns([1, 6])
    
    with col1:
        st.image(f"{BASE_DIR}/imagenes/UPlogo.jpg", width=200)
        
    with col2:
        st.title(text_title)
        st.caption("📘 Developed for: *Business Intelligence (Graduate Level)*")
        st.caption("Universidad Panamericana")
