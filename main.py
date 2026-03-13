#from Modules.geodata_pipeline import GeoDataPipeline
from Modules.bar_chart import BarChartGenerator
from Modules.choropleth_map import ChoroplethMapGenerator
from Modules.header import show_header
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

AGEB = BASE_DIR / "Data/Processed/ageb_cp_fast.csv.gz"
GEOJSON = BASE_DIR / "Data/Processed/cp_geojson.json"

show_header("Dashboard Inteligencia de Negocios CDMX")

# 1. Cargar Datos
@st.cache_data
def load_data():
    df = pd.read_csv(AGEB, low_memory=False)
    # Aseguramos el formato del CP desde que entra
    df["CP"] = df["CP"].astype(str).str.zfill(5) 
    with open(GEOJSON) as f:
        geojson = json.load(f)
    return df, geojson

ageb_cp_fast, cp_geojson = load_data()


# =====================================
# DICCIONARIO DE COORDENADAS (Centros de Alcaldías)
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
    "Todas": (19.4326, -99.1332) # Centro genérico CDMX
}

# =====================================
# CONFIGURACIÓN DEL ESTADO DE SESIÓN (SESSION STATE)
# =====================================
if "metrica" not in st.session_state:
    st.session_state.metrica = "Pob. 60+"
if "alcaldia" not in st.session_state:
    st.session_state.alcaldia = "Todas"
if "cp" not in st.session_state:
    st.session_state.cp = "Todos"
if "zoom_ui" not in st.session_state:
    st.session_state.zoom_ui = 5.5 # Equivalente a 10.0 en Mapbox

# Función que ejecuta el botón de limpiar
def limpiar_filtros():
    st.session_state.metrica = "Pob. 60+"
    st.session_state.alcaldia = "Todas"
    st.session_state.cp = "Todos"
    st.session_state.zoom_ui = 5.5 # Reinicia al zoom medio

# Función para auto-hacer zoom y resetear el CP cuando se cambia la Alcaldía
def cambio_alcaldia():
    st.session_state.cp = "Todos" # Resetea el CP para evitar errores
    if st.session_state.alcaldia != "Todas":
        st.session_state.zoom_ui = 8.5 # Acerca el zoom si elige una alcaldía
    else:
        st.session_state.zoom_ui = 5.5 # Aleja el zoom si elige "Todas"


# =====================================
# 2. BARRA LATERAL (SIDEBAR) PARA FILTROS
# =====================================
st.sidebar.header("Filtros del Dashboard")

# BOTÓN LIMPIAR FILTROS
st.sidebar.button("🧹 Limpiar Filtros", on_click=limpiar_filtros, use_container_width=True)
st.sidebar.markdown("---")

opciones_metrica = {
    "Pob. 60+": "P_60YMAS",
    "Riqueza": "INDICE_RIQUEZA",
    "Autos": "VPH_AUTOM"
}

# Filtro 1: Métrica (Conectado al session_state mediante "key")
st.sidebar.selectbox(
    "Selecciona la Métrica a analizar:", 
    list(opciones_metrica.keys()),
    key="metrica"
)
metrica_columna = opciones_metrica[st.session_state.metrica]

# Filtro 2: Alcaldía (Conectado al session_state y a la función on_change)
lista_alcaldias = ["Todas"] + sorted(ageb_cp_fast["NOM_MUN"].dropna().unique().tolist())
st.sidebar.selectbox(
    "Selecciona Alcaldía:", 
    lista_alcaldias,
    key="alcaldia",
    on_change=cambio_alcaldia
)

# Filtro 3: Código Postal (Se actualiza según la alcaldía)
if st.session_state.alcaldia != "Todas":
    df_filtrado_alcaldia = ageb_cp_fast[ageb_cp_fast["NOM_MUN"] == st.session_state.alcaldia]
else:
    df_filtrado_alcaldia = ageb_cp_fast

lista_cps = ["Todos"] + sorted(df_filtrado_alcaldia["CP"].unique().tolist())
st.sidebar.selectbox("Selecciona CP:", lista_cps, key="cp")

st.sidebar.markdown("---")


# SLIDER DE ZOOM (Rango 1 a 10 visible para el usuario)
st.sidebar.slider("Nivel de Zoom del Mapa:", min_value=1.0, max_value=10.0, step=0.5, key="zoom_ui")

# Switch de Modo Oscuro
modo_oscuro = st.sidebar.toggle("Mapa en Modo Oscuro", value=True)


# =====================================
# 3. APLICAR FILTROS A LA DATA
# =====================================
df_final = df_filtrado_alcaldia.copy()

if st.session_state.cp != "Todos":
    df_final = df_final[df_final["CP"] == st.session_state.cp]


# =====================================
# 4. RENDERIZAR GRÁFICOS
# =====================================

if df_final.empty:
    st.warning("⚠️ No hay datos para los filtros seleccionados. Intenta otra combinación.")
else:
    # 1. Obtener coordenadas centrales
    lat_centro, lon_centro = coordenadas_alcaldias.get(st.session_state.alcaldia, (19.4326, -99.1332))

    # 2. Lógica Dinámica para la Gráfica de Barras
    nombre_metrica_legible = st.session_state.metrica # Ej. "Pob. 60+"
    
    if st.session_state.alcaldia == "Todas":
        nivel_barras = "NOM_MUN"
        titulo_barras = f"Top 15 Alcaldías - {nombre_metrica_legible}"
    else:
        nivel_barras = "CP"
        titulo_barras = f"Top 15 CPs en {st.session_state.alcaldia} - {nombre_metrica_legible}"

    # 3. Generar Gráficas
    bar_chart = BarChartGenerator(df_final)
    fig_bar = bar_chart.create_chart(
        metrica=metrica_columna, 
        nivel=nivel_barras,       # Pasamos si agrupa por Alcaldía o CP
        titulo=titulo_barras,     # Pasamos el texto del título
        modo_oscuro=modo_oscuro
    ) 

    # Convertir el zoom del UI (1-10) al zoom de Mapbox (8-12)
    zoom_real_mapbox = 8.0 + ((st.session_state.zoom_ui - 1.0) / 9.0) * 4.0

    map_chart = ChoroplethMapGenerator(df_final, cp_geojson)
    fig_map = map_chart.create_map(
        metrica=metrica_columna, 
        lat=lat_centro, 
        lon=lon_centro, 
        zoom_level=zoom_real_mapbox, 
        modo_oscuro=modo_oscuro
    )

    # 4. Mostrar columnas
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.plotly_chart(fig_map, use_container_width=True)