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
# Tip: st.cache_data evita que el CSV y el JSON se lean cada vez que mueves un filtro
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
# 2. BARRA LATERAL (SIDEBAR) PARA FILTROS
# =====================================
st.sidebar.header("Filtros del Dashboard")

opciones_metrica = {
    "Pob. 60+": "P_60YMAS",
    "Riqueza": "INDICE_RIQUEZA",
    "Autos": "VPH_AUTOM"
}

# Filtro 1: Métrica
metrica_seleccionada = st.sidebar.selectbox(
    "Selecciona la Métrica a analizar:", 
    list(opciones_metrica.keys())
)
metrica_columna = opciones_metrica[metrica_seleccionada]

# Filtro 2: Alcaldía
lista_alcaldias = ["Todas"] + sorted(ageb_cp_fast["NOM_MUN"].dropna().unique().tolist())
alcaldia_seleccionada = st.sidebar.selectbox("Selecciona Alcaldía:", lista_alcaldias)

# Filtro 3: Código Postal (Se actualiza según la alcaldía seleccionada)
if alcaldia_seleccionada != "Todas":
    df_filtrado_alcaldia = ageb_cp_fast[ageb_cp_fast["NOM_MUN"] == alcaldia_seleccionada]
else:
    df_filtrado_alcaldia = ageb_cp_fast

lista_cps = ["Todos"] + sorted(df_filtrado_alcaldia["CP"].unique().tolist())
cp_seleccionado = st.sidebar.selectbox("Selecciona CP:", lista_cps)

# Switch de Modo Oscuro para el mapa
st.sidebar.markdown("---")
modo_oscuro = st.sidebar.toggle("Mapa en Modo Oscuro", value=True)


# =====================================
# 3. APLICAR FILTROS A LA DATA
# =====================================
df_final = df_filtrado_alcaldia.copy()

if cp_seleccionado != "Todos":
    df_final = df_final[df_final["CP"] == cp_seleccionado]


# =====================================
# 4. RENDERIZAR GRÁFICOS
# =====================================

# Validamos que los filtros no hayan dejado el DataFrame vacío
if df_final.empty:
    st.warning("⚠️ No hay datos para los filtros seleccionados. Intenta otra combinación.")
else:
    # Generar gráficos con la data filtrada
    bar_chart = BarChartGenerator(df_final)
    fig_bar = bar_chart.create_chart(metrica_columna) 

    map_chart = ChoroplethMapGenerator(df_final, cp_geojson)
    fig_map = map_chart.create_map(metrica_columna, modo_oscuro=modo_oscuro)

    # Mostrarlos en dos columnas
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.plotly_chart(fig_map, use_container_width=True)