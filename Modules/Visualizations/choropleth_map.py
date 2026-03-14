import plotly.express as px

class ChoroplethMapGenerator:

    def __init__(self, df, geojson):
        self.df = df.copy() 
        self.geojson = geojson

    # <-- MODIFICACIÓN: Agregamos lat, lon y zoom_level como parámetros
    def create_map(self, metrica, lat=19.4326, lon=-99.1332, zoom_level=10.0, modo_oscuro=True):

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
            zoom=zoom_level, # <-- Usamos la variable de zoom
            center={"lat": lat, "lon": lon}, # <-- Usamos las coordenadas dinámicas
            opacity=0.7,
            color_continuous_scale="RdYlGn"
        )

        fig.update_layout(
            margin={"r":0,"t":40,"l":0,"b":0},
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)"
        )

        return fig