"""
# Módulo de Mapas Coropléticos Interactivos

Este módulo se especializa en la representación espacial de datos sociodemográficos 
utilizando **Mapbox** y **Plotly Express**. Su función principal es vincular un 
conjunto de datos estadísticos con un archivo GeoJSON de códigos postales de la CDMX.
"""
import plotly.express as px

class ChoroplethMapGenerator:
    """
    Clase para la generación de mapas temáticos basados en áreas geográficas.

    Se encarga de procesar la geometría y los indicadores para renderizar un mapa 
    con colores proporcionales a la métrica seleccionada.

    **Attributes:**
        df (pd.DataFrame): DataFrame con información censal por AGEB/CP.
        geojson (dict): Diccionario en formato GeoJSON que contiene las geometrías de los Códigos Postales.
    """

    def __init__(self, df, geojson):
        """
        Inicializa el generador de mapas.

        **Args:**
            df (pd.DataFrame): Fuente de datos (se crea una copia interna para evitar efectos secundarios).
            geojson (dict): Estructura de datos geográfica con llaves coincidentes con el DataFrame.
        """
        self.df = df.copy() 
        self.geojson = geojson


    def create_map(self, metrica, lat=19.4326, lon=-99.1332, zoom_level=10.0, modo_oscuro=True):
        """
        Calcula indicadores por Código Postal y genera una figura Mapbox.

        El proceso de renderizado incluye:
        1. **Normalización de CP**: Asegura que el Código Postal tenga 5 dígitos (z-fill).
        2. **Agregación Espacial**: Suma la métrica y población a nivel de CP.
        3. **Normalización de Datos**: Calcula el porcentaje relativo a la población total.
        4. **Localización**: Centra el mapa dinámicamente según la Alcaldía seleccionada.

        **Args:**
            metrica (str): Nombre de la columna de datos a visualizar.
            lat (float): Latitud para el centro del mapa. Por defecto 19.4326 (CDMX Centro).
            lon (float): Longitud para el centro del mapa. Por defecto -99.1332 (CDMX Centro).
            zoom_level (float): Nivel de acercamiento inicial (típicamente entre 8.0 y 14.0).
            modo_oscuro (bool): Si es `True`, usa el estilo 'carto-darkmatter'. Si es `False`, 'carto-positron'.

        **Returns:**
            plotly.graph_objects.Figure: Figura de Plotly con el mapa coroplético renderizado.
        """
        self.df["CP"] = self.df["CP"].astype(str).str.zfill(5)

        df_map = self.df.groupby("CP").agg({
            metrica: "sum",
            "POBTOT": "sum"
        }).reset_index()

        df_map = df_map[df_map["POBTOT"] > 0]

        df_map["Porcentaje (%)"] = (
            df_map[metrica] / df_map["POBTOT"]
        ) * 100

        mapa = "carto-darkmatter" if modo_oscuro else "carto-positron"

        fig = px.choropleth_mapbox(
            df_map,
            geojson=self.geojson,
            locations="CP",
            featureidkey="properties.CP",
            color="Porcentaje (%)",
            mapbox_style=mapa,
            zoom=zoom_level, 
            center={"lat": lat, "lon": lon}, 
            opacity=0.7,
            color_continuous_scale="RdYlGn"
        )

        fig.update_layout(
            margin={"r":0,"t":40,"l":0,"b":0},
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)"
        )

        return fig