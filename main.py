#from Modules.geodata_pipeline import GeoDataPipeline
from Modules.bar_chart import BarChartGenerator
from Modules.choropleth_map import ChoroplethMapGenerator
from Modules.header import show_header
from Modules.table_view import TableViewGenerator, show_export_button
from pathlib import Path
import streamlit as st
import json
import pandas as pd

st.set_page_config(layout="wide")

BASE_DIR = Path(__file__).resolve().parent

#---------------------------------------------------------------------------------
#Sección de código donde se hace la carga de datos
#CENSO_CSV = BASE_DIR / "Data/AGEB/conjunto_de_datos_ageb_urbana_09_cpv2020.csv"
#AGEB_SHP = BASE_DIR / "Data/shape/AGEB_urb_2010_5.shp"
#CP_SHP = BASE_DIR / "Data/shape_cp/CP_09CDMX_v7.shp"

#@st.cache_data(show_spinner="Procesando datos geoespaciales...", ttl=None)
#def run_pipeline_cached(version="1"):
#    pipeline = GeoDataPipeline(
#        CENSO_CSV,
#        AGEB_SHP,
#        CP_SHP
#    )
#    return pipeline.run_pipeline()

#ageb_cp_fast, cp_geojson = run_pipeline_cached("1")

#ageb_cp_fast.to_csv("ageb_cp_fast.csv.gz",index=False)

#with open("cp_geojson.json", "w") as f:
#    json.dump(cp_geojson, f)
#-----------------------------------------------------------------------------

# --- CONTROL DE VISTA ---
if "vista_detalle" not in st.session_state:
    st.session_state.vista_detalle = False

def toggle_vista():
    st.session_state.vista_detalle = not st.session_state.vista_detalle

# --- CARGA DE DATOS ---
AGEB = BASE_DIR / "Data/Processed/ageb_cp_fast.csv.gz"
GEOJSON = BASE_DIR / "Data/Processed/cp_geojson.json"

show_header("Dashboard Inteligencia de Negocios CDMX")

@st.cache_data
def load_data():
    df = pd.read_csv(AGEB, low_memory=False)
    df["CP"] = df["CP"].astype(str).str.zfill(5) 
    with open(GEOJSON) as f:
        geojson = json.load(f)
    return df, geojson

ageb_cp_fast, cp_geojson = load_data()

# --- ESTADO DE SESIÓN Y FILTROS ---
if "metrica" not in st.session_state: st.session_state.metrica = "Pob. 60+"
if "alcaldia" not in st.session_state: st.session_state.alcaldia = "Todas"
if "cp" not in st.session_state: st.session_state.cp = "Todos"
if "zoom_ui" not in st.session_state: st.session_state.zoom_ui = 5.5 

def limpiar_filtros():
    st.session_state.metrica = "Pob. 60+"
    st.session_state.alcaldia = "Todas"
    st.session_state.cp = "Todos"
    st.session_state.zoom_ui = 5.5 

def cambio_alcaldia():
    st.session_state.cp = "Todos" 
    st.session_state.zoom_ui = 8.5 if st.session_state.alcaldia != "Todas" else 5.5

# --- SIDEBAR ---
st.sidebar.header("Filtros del Dashboard")

# Actualizado a width="stretch"
st.sidebar.button("🧹 Limpiar Filtros", on_click=limpiar_filtros, width="stretch")

texto_btn = "📊 Ir a Dashboard" if st.session_state.vista_detalle else "🔍 Ir a Detalle ->"
st.sidebar.button(texto_btn, on_click=toggle_vista, width="stretch")

st.sidebar.markdown("---")
opciones_metrica = {"Pob. 60+": "P_60YMAS", "Riqueza": "INDICE_RIQUEZA", "Autos": "VPH_AUTOM"}
st.sidebar.selectbox("Métrica:", list(opciones_metrica.keys()), key="metrica")
metrica_columna = opciones_metrica[st.session_state.metrica]

lista_alcaldias = ["Todas"] + sorted(ageb_cp_fast["NOM_MUN"].dropna().unique().tolist())
st.sidebar.selectbox("Alcaldía:", lista_alcaldias, key="alcaldia", on_change=cambio_alcaldia)

df_filtrado_alcaldia = ageb_cp_fast[ageb_cp_fast["NOM_MUN"] == st.session_state.alcaldia] if st.session_state.alcaldia != "Todas" else ageb_cp_fast
lista_cps = ["Todos"] + sorted(df_filtrado_alcaldia["CP"].unique().tolist())
st.sidebar.selectbox("CP:", lista_cps, key="cp")

st.sidebar.markdown("---")
st.sidebar.slider("Zoom:", 1.0, 10.0, step=0.5, key="zoom_ui")
modo_oscuro = st.sidebar.toggle("Tema Oscuro", value=True)

# --- CSS PARA BOTONES NEGROS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] button {
        background-color: #262730 !important;
        color: white !important;
        border: 1px solid #444 !important;
    }
    [data-testid="stSidebar"] button p {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

if modo_oscuro:
    st.markdown('<style>.stApp { background-color: #0E1117; color: #FAFAFA; } [data-testid="stSidebar"] { background-color: #262730; }</style>', unsafe_allow_html=True)
else:
    st.markdown('<style>.stApp { background-color: #FFFFFF; color: #262730; } [data-testid="stSidebar"] { background-color: #F0F2F6; }</style>', unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
df_final = df_filtrado_alcaldia.copy()
if st.session_state.cp != "Todos":
    df_final = df_final[df_final["CP"] == st.session_state.cp]

# --- RENDERIZADO ---
if df_final.empty:
    st.warning("⚠️ Sin datos.")
else:
    if st.session_state.vista_detalle:
        st.subheader(f"Detalle de Datos: {st.session_state.alcaldia}")
        show_export_button(df_final)
        table_gen = TableViewGenerator(df_final)
        table_gen.render_table()
    else:
        # Dashboard: width="stretch" en los charts
        col1, col2 = st.columns(2)
        with col1:
            bar_chart = BarChartGenerator(df_final)
            fig_bar = bar_chart.create_chart(metrica_columna, 
                                           nivel="CP" if st.session_state.alcaldia != "Todas" else "NOM_MUN",
                                           modo_oscuro=modo_oscuro)
            st.plotly_chart(fig_bar, width="stretch")
        
        with col2:
            from Modules.choropleth_map import ChoroplethMapGenerator
            lat_centro, lon_centro = (19.4326, -99.1332) # Simplificado para el ejemplo
            zoom_real = 8.0 + ((st.session_state.zoom_ui - 1.0) / 9.0) * 4.0
            map_chart = ChoroplethMapGenerator(df_final, cp_geojson)
            fig_map = map_chart.create_map(metrica_columna, lat_centro, lon_centro, zoom_real, modo_oscuro)
            st.plotly_chart(fig_map, width="stretch")