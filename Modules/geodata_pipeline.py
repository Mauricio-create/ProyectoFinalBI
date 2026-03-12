# geo_data_pipeline.py

import pandas as pd
import geopandas as gpd
import numpy as np
import json


class GeoDataPipeline:

    def __init__(self, censo_path, ageb_path, cp_path):
        self.censo_path = censo_path
        self.ageb_path = ageb_path
        self.cp_path = cp_path

        self.censo = None
        self.ageb = None
        self.cp = None
        self.ageb_cp = None
        self.cp_geojson = None


    # 1. Carga de datos
    def load_data(self):

        self.censo = pd.read_csv(self.censo_path, low_memory=False)

        self.ageb = gpd.read_file(self.ageb_path,engine="pyogrio").to_crs(epsg=4326)

        self.cp = gpd.read_file(self.cp_path,engine="pyogrio").to_crs(epsg=4326)


    # 2. Crear CVEGEO
    def build_cvegeo(self):

        self.censo["CVEGEO"] = (
            self.censo["ENTIDAD"].astype(str).str.zfill(2) +
            self.censo["MUN"].astype(str).str.zfill(3) +
            self.censo["LOC"].astype(str).str.zfill(4) +
            self.censo["AGEB"].astype(str).str.zfill(4)
        )


    # 3. Merge Censo + AGEB
    def merge_census(self):

        self.ageb = self.ageb.merge(
            self.censo,
            on="CVEGEO",
            how="left"
        ).replace(["*", "N/D"], np.nan)


    # 4. Limpieza columnas
    def clean_columns(self):

        cols = ["POBTOT", "P_60YMAS", "VPH_PC", "VPH_INTER", "VPH_AUTOM"]

        for col in cols:
            self.ageb[col] = pd.to_numeric(self.ageb[col], errors="coerce")


    # 5. Preparar CP
    def prepare_cp(self):

        self.cp = self.cp.rename(columns={"d_cp": "CP"})
        self.cp["CP"] = self.cp["CP"].astype(str).str.zfill(5)

        self.cp_geojson = json.loads(self.cp.to_json())

    # 6. Spatial Join
    def spatial_join(self):

        self.ageb_cp = gpd.sjoin(
            self.ageb,
            self.cp[["CP", "geometry"]],
            how="left",
            predicate="intersects"
        )


    # 7. Feature Engineering
    def create_features(self):

        self.ageb_cp["INDICE_RIQUEZA"] = self.ageb_cp[
            ["VPH_PC", "VPH_INTER", "VPH_AUTOM"]
        ].sum(axis=1)

 
    # 8. Pipeline completo
    def run_pipeline(self):

        self.load_data()
        self.build_cvegeo()
        self.merge_census()
        self.clean_columns()
        self.prepare_cp()
        self.spatial_join()
        self.create_features()

        return self.ageb_cp, self.cp_geojson