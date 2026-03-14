import streamlit as st
import json
import pandas as pd
from pathlib import Path
from Modules.Visualizations.bar_chart import BarChartGenerator
from Modules.Visualizations.choropleth_map import ChoroplethMapGenerator
from Modules.Visualizations.header import show_header
from Modules.Visualizations.table_view import TableViewGenerator, show_export_button

st.set_page_config(layout="wide",page_title="BI CDMX")

def init_session_state(): 
    defaults = {
        "vista_detalle": False, 
        "metrica": "Pob. 60+", 
        "alcaldia": "Todas", 
        "cp":"Todos", 
        "zoom_ui": 5.5
    }

    for key, val in defaults.items(): 
        if key not in st.session_state: 
            st.session_state[key] = val


def apply_styles(modo_oscuro): 
    color_bg_sidebar = "#262730" if modo_oscuro else "#f0f2f6"
    color_bg_app = "#0E1117" if modo_oscuro else "#FFFFFF"
    color_text = "#FAFAFA" if modo_oscuro else "#262730"
    
    # Color de los botones (siempre oscuros según tu código original)
    color_btn_bg = "#262730"
    color_btn_text = "white"

    st.markdown(f"""
        <style>
            /* Fondo de la App y color de texto general */
            .stApp {{ 
                background-color: {color_bg_app}; 
                color: {color_text}; 
            }}

            /* Fondo de la Sidebar */
            [data-testid="stSidebar"] {{ 
                background-color: {color_bg_sidebar} !important; 
            }}

            /* Forzar color de texto en TODA la sidebar (Headers, Labels, Textos) */
            [data-testid="stSidebar"] .stMarkdown p, 
            [data-testid="stSidebar"] label, 
            [data-testid="stSidebar"] h1, 
            [data-testid="stSidebar"] h2, 
            [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] .stWidgetLabel p {{
                color: {color_text} !important;
            }}

            /* Estilo específico para los botones de la sidebar */
            [data-testid="stSidebar"] button {{
                background-color: {color_btn_bg} !important;
                color: {color_btn_text} !important;
                border: 1px solid #444 !important;
            }}
            
            [data-testid="stSidebar"] button p {{ 
                color: {color_btn_text} !important; 
            }}

            /* Ajuste para el slider y otros widgets */
            [data-testid="stSidebar"] .stSlider {{
                color: {color_text} !important;
            }}
        </style>
        """, unsafe_allow_html=True)
    
@st.cache_data
def load_all_data(path): 
    df = pd.read_csv(f"{path}/Data/Processed/ageb_cp_fast.csv.gz")
    df["CP"] = df["CP"].astype(str).str.zfill(5)

    with open(f"{path}/Data/Processed/cp_geojson.json") as f: 
        geojson = json.load(f)

    return df, geojson

def get_coordenadas():
    return {
        "Azcapotzalco": (19.4869, -99.1859), "Coyoacán": (19.3467, -99.1617),
        "Cuajimalpa de Morelos": (19.3692, -99.2991), "Gustavo A. Madero": (19.4827, -99.1093),
        "Iztacalco": (19.3952, -99.0977), "Iztapalapa": (19.3552, -99.0622),
        "La Magdalena Contreras": (19.3321, -99.2435), "Milpa Alta": (19.1922, -99.0225),
        "Álvaro Obregón": (19.3586, -99.2530), "Tláhuac": (19.2687, -99.0069),
        "Tlalpan": (19.1555, -99.1931), "Xochimilco": (19.2433, -99.1061),
        "Benito Juárez": (19.3806, -99.1611), "Cuauhtémoc": (19.4326, -99.1432),
        "Miguel Hidalgo": (19.4312, -99.2001), "Venustiano Carranza": (19.4304, -99.0953),
        "Todas": (19.4326, -99.1332)
    }

def render_sidebar(df): 
    st.sidebar.header("Filtros del Dashboard")

    col_nav1, col_nav2 = st.sidebar.columns(2)
    
    # Botón Limpiar
    if col_nav1.button("🧹 Limpiar", use_container_width=True): 
        st.session_state.metrica = "Pob. 60+"
        st.session_state.alcaldia = "Todas"
        st.session_state.cp = "Todos"
        st.session_state.zoom_ui = 5.5
        st.rerun()

    # Botón de Cambio de Vista
    texto_btn = "📊 Dashboard" if st.session_state.vista_detalle else "🔍 Detalle"
    if col_nav2.button(texto_btn, use_container_width=True):
        st.session_state.vista_detalle = not st.session_state.vista_detalle
        st.rerun()

    st.sidebar.markdown("---")

    # --- Métrica ---
    opciones_metrica = {"Pob. 60+": "P_60YMAS", "Riqueza": "INDICE_RIQUEZA", "Autos": "VPH_AUTOM"}
    lista_metrica = list(opciones_metrica.keys())
    # Forzamos el índice basado en lo que hay en session_state
    idx_metrica = lista_metrica.index(st.session_state.metrica)
    metrica_label = st.sidebar.selectbox("Métrica:", lista_metrica, index=idx_metrica, key="metrica")
    
    # --- Alcaldía ---
    alcaldias = ["Todas"] + sorted(df["NOM_MUN"].dropna().unique().tolist())
    idx_alc = alcaldias.index(st.session_state.alcaldia) if st.session_state.alcaldia in alcaldias else 0
    
    st.sidebar.selectbox(
        "Alcaldía:", 
        alcaldias, 
        index=idx_alc,
        key="alcaldia", 
        on_change=lambda: st.session_state.update({
            "cp": "Todos", 
            "zoom_ui": 8.5 if st.session_state.alcaldia != "Todas" else 5.5
        })
    )
    
    # --- Código Postal ---
    df_muni = df[df["NOM_MUN"] == st.session_state.alcaldia] if st.session_state.alcaldia != "Todas" else df
    lista_cp = ["Todos"] + sorted(df_muni["CP"].unique().tolist())
    
    # Manejo de error por si el CP seleccionado no existe en la nueva alcaldía
    idx_cp = lista_cp.index(st.session_state.cp) if st.session_state.cp in lista_cp else 0
    st.sidebar.selectbox("Código Postal:", lista_cp, index=idx_cp, key="cp")

    st.sidebar.markdown("---")
    
    # --- Slider y Toggle ---
    st.sidebar.slider("Zoom:", 1.0, 10.0, step=0.5, key="zoom_ui")
    
    # Nota: El toggle necesita el parámetro 'value' vinculado al estado
    oscuro = st.sidebar.toggle("Tema Oscuro", value=True)
    
    return opciones_metrica[metrica_label], oscuro

def render_dashboard_view(df, geojson, metrica_col, modo_oscuro): 
    coords = get_coordenadas()
    lat, lon = coords.get(st.session_state.alcaldia, coords["Todas"])
    zoom_real = 8.0 + ((st.session_state.zoom_ui - 1.0)/9.0)*4.0

    col1, col2 = st.columns(2)

    with col1: 
        nivel = "CP" if st.session_state.alcaldia != "Todas" else "NOM_MUN"
        fig_bar = BarChartGenerator(df).create_chart(metrica_col,nivel,f"Top 15 - {st.session_state.metrica}", modo_oscuro)
        st.plotly_chart(fig_bar, width="stretch")

    with col2: 
        fig_map = ChoroplethMapGenerator(df, geojson).create_map(metrica_col,lat,lon,zoom_real,modo_oscuro)
        st.plotly_chart(fig_map, width="stretch")


def render_detail_view(df): 
    st.subheader(f"Vista de Detalle: {st.session_state.alcaldia} - {st.session_state.cp}")
    cols = ["NOM_MUN", "CP", "AGEB", "POBTOT", "P_60YMAS", "INDICE_RIQUEZA", "VPH_AUTOM"]
    df_tabla = df[cols].copy()
    df_tabla.columns = ["Alcaldía", "CP", "AGEB", "Pob. Total", "Pob. 60+", "Riqueza", "Autos"]

    show_export_button(df_tabla)
    TableViewGenerator(df_tabla).render_table()
    
