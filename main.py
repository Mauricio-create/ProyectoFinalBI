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

# --- CONFIGURACIÓN DE VISTA (DASHBOARD O DETALLE) ---
if "vista_detalle" not in st.session_state:
    st.session_state.vista_detalle = False

def toggle_vista():
    st.session_state.vista_detalle = not st.session_state.vista_detalle

# --- CARGA DE DATOS ---
AGEB_PATH = BASE_DIR / "Data/Processed/ageb_cp_fast.csv.gz"
GEOJSON_PATH = BASE_DIR / "Data/Processed/cp_geojson.json"

show_header("Dashboard Inteligencia de Negocios CDMX")

@st.cache_data
def load_data():
    df = pd.read_csv(AGEB_PATH, low_memory=False)
    df["CP"] = df["CP"].astype(str).str.zfill(5) 
    with open(GEOJSON_PATH) as f:
        geojson = json.load(f)
    return df, geojson

ageb_cp_fast, cp_geojson = load_data()

# =====================================
# DICCIONARIO DE COORDENADAS
# =====================================
coordenadas_alcaldias = {
    "Azcapotzalco": (19.4869, -99.1859),
    "Coyoacán": (19.3467, -99.1617),
    "Cuajimalpa de Morelos": (19.3692, -99.2991),
    "Gustavo A. Madero": (19.4827, -99.1093),
    "Iztacalco": (19.3952, -99.0977),
    "Iztapalapa": (19.3552, -99.0622),
    "La Magdalena Contreras": (19.3321, -99.2435),
    "Milpa Alta": (19.1922, -99.0225),
    "Álvaro Obregón": (19.3586, -99.2530),
    "Tláhuac": (19.2687, -99.0069),
    "Tlalpan": (19.1555, -99.1931),
    "Xochimilco": (19.2433, -99.1061),
    "Benito Juárez": (19.3806, -99.1611),
    "Cuauhtémoc": (19.4326, -99.1432),
    "Miguel Hidalgo": (19.4312, -99.2001),
    "Venustiano Carranza": (19.4304, -99.0953),
    "Todas": (19.4326, -99.1332)
}

# =====================================
# SESSION STATE Y FUNCIONES
# =====================================
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

# =====================================
# SIDEBAR (FILTROS Y NAVEGACIÓN)
# =====================================
st.sidebar.header("Filtros del Dashboard")

# Botones de Acción: Siempre Negros con letra Blanca
st.sidebar.button("🧹 Limpiar Filtros", on_click=limpiar_filtros, width="stretch")

texto_nav = "📊 Ir a Dashboard" if st.session_state.vista_detalle else "🔍 Ir a Detalle ->"
st.sidebar.button(texto_nav, on_click=toggle_vista, width="stretch")

st.sidebar.markdown("---")

opciones_metrica = {"Pob. 60+": "P_60YMAS", "Riqueza": "INDICE_RIQUEZA", "Autos": "VPH_AUTOM"}
st.sidebar.selectbox("Selecciona la Métrica:", list(opciones_metrica.keys()), key="metrica")
metrica_columna = opciones_metrica[st.session_state.metrica]

lista_alcaldias = ["Todas"] + sorted(ageb_cp_fast["NOM_MUN"].dropna().unique().tolist())
st.sidebar.selectbox("Selecciona Alcaldía:", lista_alcaldias, key="alcaldia", on_change=cambio_alcaldia)

# Filtrado dinámico para la lista de CPs
df_filtrado_alcaldia = ageb_cp_fast[ageb_cp_fast["NOM_MUN"] == st.session_state.alcaldia] if st.session_state.alcaldia != "Todas" else ageb_cp_fast
lista_cps = ["Todos"] + sorted(df_filtrado_alcaldia["CP"].unique().tolist())
st.sidebar.selectbox("Selecciona CP:", lista_cps, key="cp")

st.sidebar.markdown("---")
st.sidebar.slider("Nivel de Zoom:", 1.0, 10.0, step=0.5, key="zoom_ui")
modo_oscuro = st.sidebar.toggle("Tema Oscuro del Tablero", value=True)

# =====================================
# INYECCIÓN DE CSS (BOTONES Y TEMAS)
# =====================================
color_bg_botones = "#262730" 
st.markdown(f"""
    <style>
    /* Forzar estilo en botones de la sidebar */
    [data-testid="stSidebar"] button {{
        background-color: {color_bg_botones} !important;
        color: white !important;
        border: 1px solid #444 !important;
    }}
    [data-testid="stSidebar"] button p {{
        color: white !important;
    }}
    /* Fondos dinámicos */
    .stApp {{ 
        background-color: {"#0E1117" if modo_oscuro else "#FFFFFF"}; 
        color: {"#FAFAFA" if modo_oscuro else "#262730"}; 
    }}
    [data-testid="stSidebar"] {{ 
        background-color: {"#262730" if modo_oscuro else "#F0F2F6"} !important; 
    }}
    </style>
""", unsafe_allow_html=True)

# =====================================
# LÓGICA DE FILTRADO FINAL
# =====================================
df_final = df_filtrado_alcaldia.copy()
if st.session_state.cp != "Todos":
    df_final = df_final[df_final["CP"] == st.session_state.cp]

# =====================================
# RENDERIZADO DE CONTENIDO
# =====================================
if df_final.empty:
    st.warning("⚠️ No hay datos para los filtros seleccionados. Intenta otra combinación.")
else:
    if st.session_state.vista_detalle:
        # --- MODO DETALLE (TABLA) ---
        st.subheader(f"Vista de Detalle: {st.session_state.alcaldia} - {st.session_state.cp}")
        
        # Seleccionamos solo columnas importantes para que sea legible
        columnas_tabla = ["NOM_MUN", "CP", "AGEB", "POBTOT", "P_60YMAS", "INDICE_RIQUEZA", "VPH_AUTOM"]
        df_tabla = df_final[columnas_tabla].copy()
        
        # Renombramos para el usuario final
        df_tabla.columns = ["Alcaldía", "CP", "AGEB", "Pob. Total", "Pob. 60+", "Riqueza", "Autos"]
        
        # Botón de exportar aparece solo aquí
        show_export_button(df_tabla) 
        
        table_gen = TableViewGenerator(df_tabla)
        table_gen.render_table()
        
    else:
        # --- MODO DASHBOARD (GRÁFICAS) ---
        lat_centro, lon_centro = coordenadas_alcaldias.get(st.session_state.alcaldia, (19.4326, -99.1332))
        
        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de Barras
            bar_chart = BarChartGenerator(df_final)
            nivel_b = "CP" if st.session_state.alcaldia != "Todas" else "NOM_MUN"
            fig_bar = bar_chart.create_chart(
                metrica=metrica_columna, 
                nivel=nivel_b,       
                titulo=f"Top 15 - {st.session_state.metrica}",     
                modo_oscuro=modo_oscuro
            )
            st.plotly_chart(fig_bar, width="stretch")

        with col2:
            # Mapa Coroplético
            zoom_real = 8.0 + ((st.session_state.zoom_ui - 1.0) / 9.0) * 4.0
            map_chart = ChoroplethMapGenerator(df_final, cp_geojson)
            fig_map = map_chart.create_map(
                metrica=metrica_columna, 
                lat=lat_centro, 
                lon=lon_centro, 
                zoom_level=zoom_real, 
                modo_oscuro=modo_oscuro
            )
            st.plotly_chart(fig_map, width="stretch")