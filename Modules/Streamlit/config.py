"""
# Módulo de Configuración y Utilidades de Interfaz (Streamlit)

Este módulo centraliza la lógica de control de la aplicación, gestionando:
1. **Estado de Sesión**: Inicialización y persistencia de filtros.
2. **Estilos Dinámicos**: Inyección de CSS para temas claro y oscuro.
3. **Controladores de Vista**: Renderizado de la barra lateral y gestión de navegación.
4. **Carga de Datos**: Manejo de caché para optimizar el rendimiento.
"""

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
    """
    Inicializa las variables del `st.session_state` con valores por defecto.
    
    Asegura que la aplicación no falle al intentar acceder a filtros antes de 
    que el usuario interactúe con la barra lateral.
    """
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
    """
    Inyecta CSS personalizado en la aplicación basándose en el tema seleccionado.
    
    **Elementos personalizados:**
    * Fondos de aplicación y barra lateral.
    * Colores de texto para etiquetas, encabezados y párrafos.
    * Estilo de botones y sliders para mantener consistencia visual.

    **Args:**
        modo_oscuro (bool): Determina si se aplican colores de alto contraste (oscuro) 
        o colores institucionales suaves (claro).
    """
    color_bg_sidebar = "#262730" if modo_oscuro else "#f0f2f6"
    color_bg_app = "#0E1117" if modo_oscuro else "#FFFFFF"
    color_text = "#FAFAFA" if modo_oscuro else "#262730"

   


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
    """
    Carga los datasets procesados desde el almacenamiento local.
    
    Utiliza el decorador `@st.cache_data` para evitar lecturas de disco repetitivas 
    en cada interacción del usuario.

    **Args:**
        path (Path): Ruta base del proyecto.

    **Returns:**
        tuple: (pd.DataFrame, dict) conteniendo el CSV de AGEB y el JSON de polígonos.
    """
    df = pd.read_csv(f"{path}/Data/Processed/ageb_cp_fast.csv.gz")
    df["CP"] = df["CP"].astype(str).str.zfill(5)

    with open(f"{path}/Data/Processed/cp_geojson.json") as f:
        geojson = json.load(f)

    return df, geojson


def get_coordenadas():
    """
    Diccionario maestro de coordenadas geográficas.
    
    **Returns:**
        dict: Mapeo de nombres de Alcaldías a tuplas `(latitud, longitud)`.
    """
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
    """
    Renderiza los controles de filtrado y navegación en el lateral.
    
    **Funcionalidades:**
    * **Limpiar**: Resetea el `session_state` a valores iniciales.
    * **Cambio de Vista**: Alterna entre el Tablero visual y el Detalle tabular.
    * **Selectores**: Filtros dinámicos de métrica, alcaldía y CP (con cascada).

    **Returns:**
        tuple: (str, bool) Métrica seleccionada y estado del modo oscuro.
    """
    st.sidebar.header("Filtros del Dashboard")
    col_nav1, col_nav2 = st.sidebar.columns(2)
    if col_nav1.button("🧹 Limpiar", width="stretch"):
        st.session_state.metrica, st.session_state.alcaldia = "Pob. 60+", "Todas"
        st.session_state.cp, st.session_state.zoom_ui = "Todos", 5.5
        st.rerun()

    texto_btn = "📊 Tablero" if st.session_state.vista_detalle else "🔍 Detalle"

    if col_nav2.button(texto_btn, width="stretch"):
        st.session_state.vista_detalle = not st.session_state.vista_detalle
        st.rerun()

    st.sidebar.markdown("---")


    opciones_metrica = {"Pob. 60+": "P_60YMAS", "Riqueza": "INDICE_RIQUEZA", "Autos": "VPH_AUTOM"}
    metrica_label = st.sidebar.selectbox("Métrica:", list(opciones_metrica.keys()), key="metrica")

    alcaldias = ["Todas"] + sorted(df["NOM_MUN"].dropna().unique().tolist())
    st.sidebar.selectbox("Alcaldía:", alcaldias, key="alcaldia", on_change=lambda: st.session_state.update({"cp": "Todos", "zoom_ui": 8.5 if st.session_state.alcaldia != "Todas" else 5.5}))


    df_muni = df[df["NOM_MUN"] == st.session_state.alcaldia] if st.session_state.alcaldia != "Todas" else df
    st.sidebar.selectbox("Código Postal:", ["Todos"] + sorted(df_muni["CP"].unique().tolist()), key="cp")

    st.sidebar.markdown("---")

    st.sidebar.slider("Zoom:", 1.0, 10.0, step=0.5, key="zoom_ui")

    oscuro = st.sidebar.toggle("Tema Oscuro", value=True)

    return opciones_metrica[metrica_label], oscuro


def render_dashboard_view(df, geojson, metrica_col, modo_oscuro):
    """
    Orquestador de la vista visual (Gráficas + Mapa).
    """
    coords = get_coordenadas()
    lat, lon = coords.get(st.session_state.alcaldia, coords["Todas"])
    zoom_real = 8.0 + ((st.session_state.zoom_ui - 1.0)/9.0)*4.0
    
    col1, col2 = st.columns(2)

    with col1:
        nivel = "CP" if st.session_state.alcaldia != "Todas" else "NOM_MUN"
        
        usar_score = st.toggle("Activar Modelo de Score Comercial", value=False)
        
        if usar_score:
            mis_pesos = {
                "INDICE_RIQUEZA": 0.40,
                "P_60YMAS": 0.40,
                "VPH_AUTOM": 0.20
            }
            fig_bar = BarChartGenerator(df).create_scoring_chart(
                pesos=mis_pesos,
                nivel=nivel,
                titulo="Top 15 - Índice Comercial (Score)", 
                modo_oscuro=modo_oscuro
            )
        else:
            fig_bar = BarChartGenerator(df).create_chart(
                metrica=metrica_col,
                nivel=nivel,
                titulo=f"Top 15 - {st.session_state.metrica}",
                modo_oscuro=modo_oscuro
            )
            
        st.plotly_chart(fig_bar, width="stretch")


    with col2:
        df_map = df.copy()
        
        if usar_score:
            df_map["SCORE"] = (
                (df_map["INDICE_RIQUEZA"] / df_map["POBTOT"]) * 0.40 +
                (df_map["P_60YMAS"] / df_map["POBTOT"]) * 0.40 +
                (df_map["VPH_AUTOM"] / df_map["POBTOT"]) * 0.20
            ) * 100
            df_map["SCORE"] = df_map["SCORE"].fillna(0)
            metrica_mapa = "SCORE"
        else:
            metrica_mapa = metrica_col
            
        fig_map = ChoroplethMapGenerator(df_map, geojson).create_map(metrica_mapa, lat, lon, zoom_real, modo_oscuro)
        st.plotly_chart(fig_map, width="stretch")

def render_detail_view(df):
    """
    Orquestador de la vista de datos crudos y exportación.
    """
    st.subheader(f"Vista de Detalle: {st.session_state.alcaldia} - {st.session_state.cp}")
    cols = ["NOM_MUN", "CP", "AGEB", "POBTOT", "P_60YMAS", "INDICE_RIQUEZA", "VPH_AUTOM"]
    df_tabla = df[cols].copy()
    df_tabla.columns = ["Alcaldía", "CP", "AGEB", "Pob. Total", "Pob. 60+", "Riqueza", "Autos"]

    show_export_button(df_tabla)

    TableViewGenerator(df_tabla).render_table() 