"""
# Módulo de Gráficos de Barras y Scoring

Este módulo proporciona herramientas para la generación de gráficas de barras interactivas 
utilizando **Plotly Express**. Permite visualizar métricas individuales o calcular 
modelos de scoring ponderados combinando múltiples variables.
"""

import plotly.express as px

class BarChartGenerator:
    """
    Clase encargada de procesar datos y generar visualizaciones de barras y rankings.
    
    **Attributes:**
        df (pd.DataFrame): El conjunto de datos que contiene la información geográfica y censal.
    """

    def __init__(self, df):
        self.df = df

    def create_chart(self, metrica, nivel="NOM_MUN", titulo="Gráfica", modo_oscuro=True):
        """
        Calcula porcentajes de una sola métrica, filtra los 15 mejores y genera la gráfica.
        """
        df_res = self.df.groupby(nivel).agg({
            metrica: "sum",
            "POBTOT": "sum"
        }).reset_index()

        df_res = df_res[df_res["POBTOT"] > 0]
        df_res["Porcentaje (%)"] = (df_res[metrica] / df_res["POBTOT"]) * 100
        df_res = df_res.sort_values("Porcentaje (%)", ascending=False).head(15)
        
        if nivel == "CP":
            df_res["CP"] = df_res["CP"].astype(str).str.zfill(5)

        tema = "plotly_dark" if modo_oscuro else "plotly_white"
        
        nombres_ejes = {"NOM_MUN": "Alcaldía", "CP": "Código Postal"}

        fig = px.bar(
            df_res, x=nivel, y="Porcentaje (%)", color="Porcentaje (%)",
            template=tema, color_continuous_scale="Viridis", title=titulo,
            labels={nivel: nombres_ejes.get(nivel, nivel)} # <-- Traducción del eje X
        )
        return fig

    def create_scoring_chart(self, pesos: dict, nivel="NOM_MUN", titulo="Score de Atractivo", modo_oscuro=True):
        """
        Genera un modelo de scoring ponderado combinando múltiples métricas.

        **Pipeline de Scoring:**
        1. Agrupa las variables seleccionadas y la población total por nivel geográfico.
        2. Normaliza cada variable (la convierte a porcentaje de la población).
        3. Multiplica cada porcentaje por su peso asignado y los suma para obtener el `Score`.
        4. Rankea el Top 15.

        **Args:**
            pesos (dict): Diccionario con las columnas y sus pesos (ej. `{"P_60YMAS": 0.4, ...}`).
                          La suma de los valores de los pesos debe ser idealmente 1.0.
            nivel (str): Nivel de agregación ('NOM_MUN' o 'CP').
            titulo (str): Título de la gráfica.
            modo_oscuro (bool): Aplica el tema oscuro si es `True`.
        """
        metricas = list(pesos.keys())
        cols_a_sumar = metricas + ["POBTOT"]
        

        df_res = self.df.groupby(nivel)[cols_a_sumar].sum().reset_index()
        df_res = df_res[df_res["POBTOT"] > 0]
        

        df_res["Score"] = 0.0
        for metrica, peso in pesos.items():
            pct_metrica = (df_res[metrica] / df_res["POBTOT"]) * 100
            df_res["Score"] += pct_metrica * peso
            
        df_res = df_res.sort_values("Score", ascending=False).head(15)
        
        if nivel == "CP":
            df_res["CP"] = df_res["CP"].astype(str).str.zfill(5)

        tema = "plotly_dark" if modo_oscuro else "plotly_white"


        nombres_ejes = {"NOM_MUN": "Alcaldía", "CP": "Código Postal"}

        fig = px.bar(
            df_res, x=nivel, y="Score", color="Score",
            template=tema, color_continuous_scale="Plasma", title=titulo,
            labels={nivel: nombres_ejes.get(nivel, nivel)} # <-- Traducción del eje X
        )
        return fig