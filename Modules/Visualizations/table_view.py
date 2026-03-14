import streamlit as st
import pandas as pd

class TableViewGenerator:
    def __init__(self, df):
        self.df = df

    def render_table(self):
        # Actualizado: width="stretch" en lugar de use_container_width
        st.dataframe(
            self.df, 
            width="stretch", 
            hide_index=True
        )

def show_export_button(df):
    csv = df.to_csv(index=False).encode('utf-8')
    
    # Actualizado: width="stretch" en lugar de use_container_width
    st.sidebar.download_button(
        label="📥 Exportar CSV",
        data=csv,
        file_name="detalle_cdmx.csv",
        mime="text/csv",
        width="stretch"
    )