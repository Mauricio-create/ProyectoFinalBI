import plotly.express as px

class BarChartGenerator:

    def __init__(self, df):
        self.df = df

    def create_chart(self, metrica, nivel="NOM_MUN", titulo="Gráfica", modo_oscuro=True):

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