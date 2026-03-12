from Modules.geodata_pipeline import GeoDataPipeline
from Modules.bar_chart import BarChartGenerator
from Modules.choropleth_map import ChoroplethMapGenerator
from Modules.header import show_header
from pathlib import Path
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent

CENSO_CSV = BASE_DIR / "Data/AGEB/conjunto_de_datos_ageb_urbana_09_cpv2020.csv"
AGEB_SHP = BASE_DIR / "Data/shape/AGEB_urb_2010_5.shp"
CP_SHP = BASE_DIR / "Data/shape_cp/CP_09CDMX_v7.shp"


pipeline = GeoDataPipeline(
    CENSO_CSV,
    AGEB_SHP,
    CP_SHP
)

#ageb_cp_fast, cp_geojson = pipeline.run_pipeline()
st.set_page_config(layout="wide")
show_header("Mi primera GUI en Streamlit")
#print(ageb_cp_fast)

# gráfico de barras
#bar_chart = BarChartGenerator(ageb_cp_fast)
#fig_bar = bar_chart.create_chart("P_60YMAS")


# mapa
#map_chart = ChoroplethMapGenerator(ageb_cp_fast, cp_geojson)
#fig_map = map_chart.create_map("P_60YMAS")


#fig_bar.show()
#fig_map.show()
