"""
# Módulo de Gráficos de Barras Comparativos

Este módulo proporciona herramientas para la generación de gráficas de barras interactivas 
utilizando **Plotly Express**. Está diseñado para visualizar métricas sociodemográficas 
normalizadas por población total a diferentes niveles geográficos (Alcaldía o Código Postal).
"""

import plotly.express as px

class BarChartGenerator:
    """
    Clase encargada de procesar datos y generar visualizaciones de barras.
    
    Permite transformar datos crudos en rankings de los "Top 15" elementos basados 
    en una métrica porcentual.
    
    **Attributes:**
        df (pd.DataFrame): El conjunto de datos que contiene la información geográfica y censal.
    """

    def __init__(self, df):
        """
        Inicializa el generador con un DataFrame.

        **Args:**
            df (pd.DataFrame): DataFrame con columnas de métrica, población y nivel geográfico.
        """
        self.df = df

    def create_chart(self, metrica, nivel="NOM_MUN", titulo="Gráfica", modo_oscuro=True):
        """
        Calcula porcentajes, filtra los 15 mejores resultados y genera la figura de Plotly.

        La función realiza el siguiente pipeline de datos:
        1. **Agrupación**: Agrupa por el nivel especificado (`CP` o `NOM_MUN`).
        2. **Normalización**: Calcula el porcentaje como `(métrica / POBTOT) * 100`.
        3. **Ranking**: Ordena de mayor a menor y selecciona los primeros 15 registros.
        4. **Estilo**: Aplica el tema oscuro o claro según se requiera.

        **Args:**
            metrica (str): La columna numérica a analizar (ej. 'P_60YMAS').
            nivel (str): El nivel de agregación: `'NOM_MUN'` (Alcaldía) o `'CP'` (Código Postal).
            titulo (str): Título que se mostrará en la parte superior del gráfico.
            modo_oscuro (bool): Si es `True`, usa el tema 'plotly_dark'. Si es `False`, 'plotly_white'.

        **Returns:**
            plotly.graph_objects.Figure: Objeto de figura interactivo para Streamlit.
        """

        df_res = self.df.groupby(nivel).agg({
            metrica: "sum",
            "POBTOT": "sum"
        }).reset_index()

        df_res = df_res[df_res["POBTOT"] > 0]

        df_res["Porcentaje (%)"] = (
            df_res[metrica] / df_res["POBTOT"]
        ) * 100

        df_res = df_res.sort_values(
            "Porcentaje (%)",
            ascending=False
        ).head(15)

        
        if nivel == "CP":
            df_res["CP"] = df_res["CP"].astype(str).str.zfill(5)

        tema = "plotly_dark" if modo_oscuro else "plotly_white"

        fig = px.bar(
            df_res,
            x=nivel,
            y="Porcentaje (%)",
            color="Porcentaje (%)",
            template=tema,
            color_continuous_scale="Viridis",
            title=titulo 
        )

        return fig