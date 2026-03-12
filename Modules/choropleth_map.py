import plotly.express as px


class ChoroplethMapGenerator:

    def __init__(self, df, geojson):
        self.df = df
        self.geojson = geojson

    def create_map(self, metrica, modo_oscuro=True):

        df_map = self.df.groupby("CP").agg({
            metrica: "sum",
            "POBTOT": "sum"
        }).reset_index()

        df_map = df_map[df_map["POBTOT"] > 0]

        df_map["Porcentaje (%)"] = (
            df_map[metrica] / df_map["POBTOT"]
        ) * 100

        centroide_seguro = (
            self.df.to_crs(epsg=3857)
            .centroid
            .to_crs(epsg=4326)
        )

        lat = centroide_seguro.y.mean()
        lon = centroide_seguro.x.mean()

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

        fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

        return fig