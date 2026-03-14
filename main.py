#from Modules.ETL.geodata_pipeline import GeoDataPipeline
from Modules.Visualizations.header import show_header
from Modules.Streamlit.config import init_session_state, load_all_data, render_sidebar, apply_styles,render_detail_view,render_dashboard_view
from pathlib import Path
import streamlit as st
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

def main(): 
    init_session_state()
    df, geojson = load_all_data(BASE_DIR)

    show_header("Dashboard Inteligencia de Negocios CDMX")
    metrica_col, modo_oscuro = render_sidebar(df)
    apply_styles(modo_oscuro)

    df_final = df.copy()
    if st.session_state.alcaldia != "Todas":
        df_final = df_final[df_final["NOM_MUN"] == st.session_state.alcaldia]
    if st.session_state.cp != "Todos":
        df_final = df_final[df_final["CP"] == st.session_state.cp]

    if df_final.empty:
        st.warning("⚠️ No hay datos para los filtros seleccionados.")
        return

    if st.session_state.vista_detalle:
        render_detail_view(df_final)
    else:
        render_dashboard_view(df_final, geojson, metrica_col, modo_oscuro)


if __name__ == "__main__": 
    main()