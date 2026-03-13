import streamlit as st
import io

class TableViewGenerator:
    def __init__(self, df):
        self.df = df

    def render_table(self):
        # st.dataframe permite filtrado nativo (clic en cabeceras y Ctrl+F)
        st.dataframe(
            self.df, 
            use_container_width=True, 
            hide_index=True
        )

    def download_excel(self):
        # Generar Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            self.df.to_excel(writer, index=False, sheet_name='Detalle')
        
        return output.getvalue()

def show_export_button(df):
    # Convertir a CSV o Excel
    csv = df.to_csv(index=False).encode('utf-8')
    
    st.sidebar.download_button(
        label="📥 Exportar CSV",
        data=csv,
        file_name="detalle_cdmx.csv",
        mime="text/csv",
        use_container_width=True
    )