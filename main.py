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
show_header("Mi primera GUI en Streamlit")

ageb_cp_fast = pd.read_csv(AGEB)
with open(GEOJSON) as f:
    cp_geojson = json.load(f)


# gráfico de barras
bar_chart = BarChartGenerator(ageb_cp_fast)
fig_bar = bar_chart.create_chart("P_60YMAS")


# mapa
#map_chart = ChoroplethMapGenerator(ageb_cp_fast, cp_geojson)
#fig_map = map_chart.create_map("P_60YMAS")


col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_bar, use_container_width=True)

#with col2:
    #st.plotly_chart(fig_map, use_container_width=True)
