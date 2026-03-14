"""
# Módulo de Visualización de Datos Tabulares

Este módulo se encarga de la representación de datos en formato de tabla interactiva 
dentro de la interfaz de Streamlit. Además, provee utilidades para la extracción 
y descarga de la información filtrada por el usuario.
"""
import streamlit as st
import pandas as pd

class TableViewGenerator:
    """
    Clase especializada en el renderizado de DataFrames de Pandas.

    Optimiza la visualización de datos permitiendo que la tabla ocupe todo el ancho 
    disponible y eliminando elementos que puedan causar ruido visual.

    **Attributes:**
        df (pd.DataFrame): El conjunto de datos ya filtrado que se desea mostrar.
    """
    def __init__(self, df):
        """
        Inicializa el generador de tablas.

        **Args:**
            df (pd.DataFrame): DataFrame con la selección de columnas finales para la vista de detalle.
        """
        self.df = df

    def render_table(self):
        """
        Muestra el DataFrame en la aplicación principal utilizando `st.dataframe`.

        **Configuración de visualización:**
        * `width="stretch"`: La tabla se ajusta dinámicamente al ancho del contenedor.
        * `hide_index=True`: Se oculta la columna de índices de Pandas para una vista más limpia.
        """
        st.dataframe(
            self.df, 
            width="stretch", 
            hide_index=True
        )

def show_export_button(df):
    """
    Crea un botón de descarga en la barra lateral para exportar los datos.

    La función convierte el DataFrame actual a formato CSV codificado en UTF-8 
    para asegurar la compatibilidad con caracteres especiales (acentos y eñes).

    **Args:**
        df (pd.DataFrame): El DataFrame que el usuario ha filtrado y desea descargar.

    **Detalles del archivo de salida:**
    * **Nombre:** `detalle_cdmx.csv`
    * **Codificación:** `utf-8`
    * **Ubicación:** Barra lateral (`st.sidebar`).
    """
    csv = df.to_csv(index=False).encode('utf-8')
    
    st.sidebar.download_button(
        label="📥 Exportar CSV",
        data=csv,
        file_name="detalle_cdmx.csv",
        mime="text/csv",
        width="stretch"
    )