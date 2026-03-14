"""
# Orquestador Principal del Dashboard BI - CDMX

Este módulo actúa como el punto de entrada principal para la aplicación de Streamlit. 
Se encarga de:
1. Configurar el entorno y las rutas base (`BASE_DIR`).
2. Gestionar el flujo de datos filtrados entre la barra lateral y las vistas.
3. Controlar la navegación entre la **Vista de Dashboard** y la **Vista de Detalle**.

El diseño sigue un patrón modular donde la lógica de negocio y visualización reside en `Modules/`.
"""

#from Modules.ETL.geodata_pipeline import GeoDataPipeline
from Modules.Visualizations.header import show_header
from Modules.Streamlit.config import init_session_state, load_all_data, render_sidebar, apply_styles,render_detail_view,render_dashboard_view
from pathlib import Path
import streamlit as st


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
    """
    Función principal que ejecuta la lógica de la aplicación.
    
    Esta función orquestra el ciclo de vida de la sesión de Streamlit:
    1. **Inicialización**: Configura el `session_state` y carga los datos procesados.
    2. **UI/UX**: Renderiza el encabezado, la barra lateral y aplica los estilos CSS dinámicos.
    3. **Filtrado**: Aplica filtros de **Alcaldía** y **Código Postal** al DataFrame maestro.
    4. **Renderizado**: Decide qué vista mostrar basándose en el estado de navegación.

    **Filtros aplicados:**
    * `NOM_MUN`: Nombre del municipio o alcaldía seleccionado.
    * `CP`: Código Postal (normalizado como string de 5 dígitos).
    """
    init_session_state()
    df_raw, geojson = load_all_data(BASE_DIR) # Cargamos los datos originales

    show_header("Dashboard Inteligencia de Negocios CDMX")
    
    metrica_col, modo_oscuro = render_sidebar(df_raw)
    apply_styles(modo_oscuro)


    df_final = df_raw.copy()

    if st.session_state.alcaldia != "Todas":
        df_final = df_final[df_final["NOM_MUN"] == st.session_state.alcaldia]
    
    if st.session_state.cp != "Todos":
        df_final = df_final[df_final["CP"].astype(str) == str(st.session_state.cp)]

    if df_final.empty:
        st.warning(f"⚠️ No hay datos para: {st.session_state.alcaldia} - CP: {st.session_state.cp}")
        return

    if st.session_state.vista_detalle:
        render_detail_view(df_final)
    else:
        render_dashboard_view(df_final, geojson, metrica_col, modo_oscuro)


if __name__ == "__main__": 
    main()