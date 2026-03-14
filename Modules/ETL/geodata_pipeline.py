"""
# Módulo de Procesamiento de Datos Geoespaciales (ETL)

Este módulo contiene la lógica para transformar los datos crudos del Censo de Población 
y Vivienda 2020 en un conjunto de datos enriquecido y vinculado geográficamente.

El pipeline realiza una intersección espacial entre las áreas estadísticas (AGEB) 
y los Códigos Postales de la CDMX, permitiendo agregar información socioeconómica 
a nivel de CP.
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import json


class GeoDataPipeline:
    """
    Orquestador del flujo ETL (Extract, Transform, Load) para datos censales y geográficos.

    **Attributes:**
        censo_path (str): Ruta al archivo CSV con datos del Censo INEGI.
        ageb_path (str): Ruta al archivo vectorial (Shapefile/GeoJSON) de AGEBs urbanas.
        cp_path (str): Ruta al archivo vectorial de Códigos Postales.
        ageb_cp (gpd.GeoDataFrame): Resultado final tras el procesamiento.
        cp_geojson (dict): Diccionario GeoJSON listo para visualizaciones en mapas.
    """

    def __init__(self, censo_path, ageb_path, cp_path):
        """
        Inicializa el pipeline definiendo las rutas de las fuentes de datos.
        """
        self.censo_path = censo_path
        self.ageb_path = ageb_path
        self.cp_path = cp_path

        self.censo = None
        self.ageb = None
        self.cp = None
        self.ageb_cp = None
        self.cp_geojson = None


    def load_data(self):
        """
        Carga los archivos desde el disco y normaliza los sistemas de referencia (CRS).
        
        **Acciones:**
        * Lee CSV y archivos vectoriales usando `pyogrio` para mayor velocidad.
        * Reproyecta las capas geográficas a **EPSG:4326** (WGS 84), estándar para web.
        """
        self.censo = pd.read_csv(self.censo_path, low_memory=False)
        self.ageb = gpd.read_file(self.ageb_path, engine="pyogrio").to_crs(epsg=4326)
        self.cp = gpd.read_file(self.cp_path, engine="pyogrio").to_crs(epsg=4326)


    def build_cvegeo(self):
        """
        Construye el identificador único `CVEGEO` para el censo.
        
        La clave se genera concatenando:
        `ENTIDAD` (2) + `MUN` (3) + `LOC` (4) + `AGEB` (4).
        Se utiliza `zfill` para asegurar que los ceros a la izquierda se mantengan.
        """
        self.censo["CVEGEO"] = (
            self.censo["ENTIDAD"].astype(str).str.zfill(2) +
            self.censo["MUN"].astype(str).str.zfill(3) +
            self.censo["LOC"].astype(str).str.zfill(4) +
            self.censo["AGEB"].astype(str).str.zfill(4)
        )


    def merge_census(self):
        """
        Une la geometría de las AGEBs con los datos tabulares del censo.
        
        **Lógica:**
        * Realiza un `left join` sobre `CVEGEO`.
        * Filtra solo datos correspondientes a la CDMX (Entidad '09').
        * Reemplaza carácteres especiales del INEGI (`*`, `N/D`) por valores nulos reales.
        """
        self.ageb = self.ageb.merge(
            self.censo,
            on="CVEGEO",
            how="left"
        ).replace(["*", "N/D"], np.nan)
        
        self.ageb = self.ageb[self.ageb["CVEGEO"].str[:2] == "09"]


    def clean_columns(self):
        """
        Convierte columnas clave de texto a formato numérico.
        
        Afecta variables de población y equipamiento de vivienda como `VPH_PC`, 
        `VPH_INTER` y `VPH_AUTOM`.
        """
        cols = ["POBTOT", "P_60YMAS", "VPH_PC", "VPH_INTER", "VPH_AUTOM"]
        for col in cols:
            self.ageb[col] = pd.to_numeric(self.ageb[col], errors="coerce")


    def prepare_cp(self):
        """
        Limpia la capa de Códigos Postales y genera la estructura GeoJSON.
        
        Asegura que la columna `CP` sea un string de 5 dígitos y elimina espacios en blanco.
        """
        if "d_cp" in self.cp.columns:
            self.cp = self.cp.rename(columns={"d_cp": "CP"})
            
        self.cp["CP"] = self.cp["CP"].astype(str).str.strip().str.zfill(5)
        self.cp_geojson = json.loads(self.cp.to_json())

        for f in self.cp_geojson["features"]:
            f["properties"]["CP"] = str(f["properties"]["CP"]).strip().zfill(5)


    def spatial_join(self):
        """
        Realiza la vinculación espacial (Spatial Join) entre AGEBs y CP.
        
        **Metodología:**
        1. Calcula el **centroide** de cada AGEB para reducir el polígono a un punto.
        2. Ejecuta un `sjoin` con el predicado `within` para determinar en qué polígono 
           de Código Postal cae cada centroide.
        """
        ageb_points = self.ageb.copy()
        ageb_points["geometry"] = self.ageb.geometry.centroid

        self.ageb_cp = gpd.sjoin(
            ageb_points,
            self.cp[["CP", "geometry"]],
            how="left",
            predicate="within" 
        )
        
        self.ageb_cp = self.ageb_cp[self.ageb_cp["CP"].notna()]
        self.ageb_cp["CP"] = self.ageb_cp["CP"].astype(str).str.strip().str.zfill(5)



    def create_features(self):
        """
        Genera variables calculadas adicionales.
        
        Crea el `INDICE_RIQUEZA` sumando viviendas con computadora, internet y automóvil.
        """
        self.ageb_cp["INDICE_RIQUEZA"] = (
            self.ageb_cp["VPH_PC"] + 
            self.ageb_cp["VPH_INTER"] + 
            self.ageb_cp["VPH_AUTOM"]
        )

 

    def run_pipeline(self):
        """
        Ejecuta el flujo completo de ETL en el orden lógico de dependencias.

        **Returns:**
            tuple: (ageb_cp: gpd.GeoDataFrame, cp_geojson: dict)
        """
        self.load_data()
        self.build_cvegeo()
        self.merge_census()
        self.clean_columns()
        self.prepare_cp()
        self.spatial_join()
        self.create_features()

        return self.ageb_cp, self.cp_geojson