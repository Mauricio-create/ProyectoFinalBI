import plotly.express as px

class ChoroplethMapGenerator:

    def __init__(self, df, geojson):
        self.df = df.copy() # Usamos .copy() para no alterar el df original
        self.geojson = geojson

    def create_map(self, metrica, modo_oscuro=True):

        # 1. CORRECCIÓN: Asegurar que el CP vuelva a ser string de 5 dígitos
        # (Porque pd.read_csv() convierte "01000" en 1000 y rompe el cruce con el json)
        self.df["CP"] = self.df["CP"].astype(str).str.zfill(5)

        df_map = self.df.groupby("CP").agg({
            metrica: "sum",
            "POBTOT": "sum"
        }).reset_index()

        df_map = df_map[df_map["POBTOT"] > 0]

        df_map["Porcentaje (%)"] = (
            df_map[metrica] / df_map["POBTOT"]
        ) * 100

        # 2. CORRECCIÓN: Como self.df viene de un CSV, ya no es un GeoDataFrame.
        # Quitamos la lógica de .to_crs() y .centroid y usamos el centro fijo de la CDMX
        lat = 19.4326
        lon = -99.1332

        mapa = "carto-darkmatter" if modo_oscuro else "carto-positron"

        fig = px.choropleth_mapbox(
            df_map,
            geojson=self.geojson,
            locations="CP",
            featureidkey="properties.CP",
            color="Porcentaje (%)",
            mapbox_style=mapa,
            zoom=10,
            center={"lat": lat, "lon": lon},
            opacity=0.7,
            color_continuous_scale="RdYlGn"
        )

        # TIP EXTRA: Hacer el fondo transparente para que se funda bonito con Streamlit
        fig.update_layout(
            margin={"r":0,"t":40,"l":0,"b":0},
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)"
        )

        return fig