# -*- coding: utf-8 -*-
"""Página 1: Mapa de CCAA con salario medio (y mediana/moda estimada) por sector."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dash
import plotly.graph_objects as go
import plotly.express as px
from dash import html, dcc, callback, Input, Output

import data_loader as dl

dash.register_page(__name__, path="/mapa", name="Mapa")

df_ccaa = dl.cargar_ccaa_sector()
geojson = dl.cargar_geojson_ccaa()
df_percentiles = dl.cargar_percentiles_reales()
df_ine_anual = dl.cargar_serie_anual()
diferencias_ine_aeat = dl.calcular_diferencias_ine_aeat()

# --- Las 3 cifras de "salario medio en España" que circulan y no coinciden ---
_fila_ine_total = df_ine_anual[(df_ine_anual["sector"] == "Total nacional") & (df_ine_anual["sexo"] == "Ambos sexos") & (df_ine_anual["anio"] == 2024)]
MEDIA_INE_TOTAL = float(_fila_ine_total["salario_medio_anual_eur"].iloc[0])
MEDIA_AEAT_TOTAL = diferencias_ine_aeat.get("Total (todos los sectores)", {}).get("aeat")
_fila_mediana_total = df_percentiles[(df_percentiles["sector"] == "Total nacional") & (df_percentiles["medida"] == "Percentil 50")]
MEDIANA_INE_TOTAL = float(_fila_mediana_total["valor_eur"].iloc[0])

TIRA_CIFRAS_NACIONALES = html.Div([
    html.Span("¿Cuál es el \"salario medio\" de España? Depende de a quién le preguntes:", className="small-muted", style={"marginRight": "10px"}),
    html.Span([html.Strong(f"{MEDIA_INE_TOTAL:,.0f} €".replace(",", ".")), " media INE (EAES 2024)"], className="tag tag-real"),
    html.Span([html.Strong(f"{MEDIA_AEAT_TOTAL:,.0f} €".replace(",", ".")), " media AEAT (2024)"], className="tag tag-approx", style={"marginLeft": "6px"}),
    html.Span([html.Strong(f"{MEDIANA_INE_TOTAL:,.0f} €".replace(",", ".")), " mediana INE (2022)"], className="tag tag-est", style={"marginLeft": "6px"}),
    html.Span(" ⓘ", className="tag tag-approx", style={"marginLeft": "6px"}, title=(
        "Las tres cifras son reales, de fuentes oficiales, y describen cosas distintas del mismo país el mismo año "
        "(aprox.): la MEDIA se dispara con los sueldos altos; la MEDIANA (lo que cobra el español que está justo "
        "en el medio) suele ser más representativa; la AEAT usa registros fiscales reales (incluye a quien trabajó "
        "solo parte del año) y por eso sale más baja que la media del INE. Si has visto '24.000€' en algún sitio, "
        "es casi seguro que se refiere a la AEAT o a la mediana, no a la media que suele salir en los titulares."
    )),
], className="card-modern", style={
    "flex": "0 0 auto", "flexDirection": "row", "flexWrap": "wrap", "alignItems": "center",
    "padding": "10px 16px", "gap": "4px",
})

OPCIONES_SECTOR = [
    {"label": "🟠 Tecnología", "value": dl.SECTOR_TECH},
    {"label": "🔵 Hostelería (aprox.)", "value": "Hostelería y ocio (aproximación AEAT)"},
    {"label": "🟤 Total", "value": "Total (todos los sectores)"},
]

# El sector de la AEAT (mapa) no usa exactamente los mismos nombres que el
# sector de la tabla de percentiles reales del INE (36829) -> se traduce aquí.
SECTOR_AEAT_A_PERCENTIL = {
    dl.SECTOR_TECH: dl.SECTOR_TECH,
    "Hostelería y ocio (aproximación AEAT)": dl.SECTOR_HOSTELERIA,
    "Total (todos los sectores)": "Total nacional",
}

layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Mapa salarial por Comunidad Autónoma", className="page-title"),
            html.P([
                "Mapa y ranking por CCAA: datos REALES de la Agencia Tributaria (IRPF 2024, única "
                "fuente con desglose regional). Cifras nacionales: INE. ",
                html.Span("ⓘ", className="tag tag-approx", title=(
                    "El INE NO publica ningún cruce oficial de sector (Tech/Hostelería) por Comunidad "
                    "Autónoma o provincia — por eso el mapa usa la AEAT, la única fuente con ese desglose. "
                    "La AEAT (registros fiscales, Modelo 190) y el INE (encuesta EAES) miden el salario "
                    "medio con metodologías distintas y dan cifras distintas para el mismo sector y año: "
                    "la AEAT sale entre un 10% y un 19% más baja según el sector (ver nota bajo cada "
                    "gráfico). País Vasco y Navarra no aparecen en la AEAT: tienen Hacienda Foral propia. "
                    "Hostelería no está aislada por CCAA: se usa la bolsa AEAT 'Otros servicios personales "
                    "y de ocio', la aproximación real más cercana. La mediana (P50) es real pero de 2022 "
                    "(INE, tabla 36829, sin edición más reciente por sector) y solo a nivel nacional."
                )),
            ], className="page-subtitle"),
        ]),
        html.Div([
            dcc.RadioItems(
                id="toggle-unidad-pagina",
                options=[
                    {"label": "€/año", "value": "defecto"},
                    {"label": "€/mes", "value": "mes"},
                ],
                value="defecto", className="segmented-control", inputStyle={"display": "none"},
            ),
        ], className="control-bar", style={"flex": "0 0 auto"}),
    ], className="page-header"),

    TIRA_CIFRAS_NACIONALES,

    html.Div([
        dcc.RadioItems(
            id="selector-sector-mapa",
            options=OPCIONES_SECTOR,
            value=dl.SECTOR_TECH,
            className="segmented-control",
            inputStyle={"display": "none"},
        ),
    ], className="selector-sector-wrap"),

    html.Div([
        html.Div([
            html.Div("Mapa por comunidad autónoma", className="card-modern-header"),
            html.Div(
                dcc.Graph(id="mapa-ccaa", config={"displayModeBar": False, "responsive": True},
                          style={"height": "100%", "width": "100%"}),
                style={"flex": "1 1 auto", "minHeight": 0},
            ),
        ], className="card-modern"),

        html.Div(id="panel-estadisticas", className="card-modern"),

        html.Div([
            html.Div("Ranking por CCAA", className="card-modern-header", style={"marginBottom": "2px"}),
            html.P("Datos AEAT (única fuente regional) — no comparar € a € con el INE",
                   className="small-muted", style={"margin": "0 0 6px 0"}),
            dl.grafico_relleno("ranking-ccaa"),
        ], className="card-modern"),
    ], className="content-grid", style={"gridTemplateColumns": "1.3fr 0.85fr 1fr", "gridTemplateRows": "1fr"}),
], style={"height": "100%", "display": "flex", "flexDirection": "column", "padding": "16px 24px", "gap": "12px"})


@callback(
    Output("mapa-ccaa", "figure"),
    Output("panel-estadisticas", "children"),
    Output("ranking-ccaa", "figure"),
    Input("selector-sector-mapa", "value"),
    Input("toggle-unidad-pagina", "value"),
)
def actualizar_mapa(sector_elegido, unidad):
    divisor = 12 if unidad == "mes" else 1
    etiqueta_unidad = "€/año" if unidad == "defecto" else "€/mes (media)"
    color_principal = dl.MAPA_COLOR_SECTOR.get(sector_elegido, dl.COLOR_AMBOS)
    sub = df_ccaa[(df_ccaa["sector"] == sector_elegido) & (df_ccaa["comunidad_autonoma"] != "Total Nacional")].copy()
    sub["cod_ccaa"] = sub["comunidad_autonoma"].map(lambda x: dl.CCAA_A_GEOJSON.get(x, {}).get("cod_ccaa"))
    sub = sub.dropna(subset=["cod_ccaa"])
    sub["salario_mostrado"] = sub["salario_medio_anual_eur"] / divisor

    escala = [[0, "#FFFFFF"], [1, color_principal]]

    fig_mapa = go.Figure(go.Choropleth(
        geojson=geojson,
        locations=sub["cod_ccaa"],
        z=sub["salario_mostrado"],
        featureidkey="properties.cod_ccaa",
        colorscale=escala,
        marker_line_color="white",
        marker_line_width=1,
        colorbar=dict(title=etiqueta_unidad, thickness=12, len=0.75, tickfont=dict(size=9)),
        customdata=sub["comunidad_autonoma"],
        hovertemplate="<b>%{customdata}</b><br>%{z:,.0f} €<extra></extra>",
    ))
    # Etiqueta de texto fija con el salario sobre cada CCAA (sustituye la necesidad
    # de pasar el ratón por encima para ver el número).
    sub["lon"] = sub["comunidad_autonoma"].map(lambda x: dl.CCAA_CENTROIDE.get(x, (None, None))[0])
    sub["lat"] = sub["comunidad_autonoma"].map(lambda x: dl.CCAA_CENTROIDE.get(x, (None, None))[1])
    sub["etiqueta"] = sub["salario_mostrado"].map(lambda v: f"{v/1000:,.1f}k€".replace(",", "."))
    fig_mapa.add_trace(go.Scattergeo(
        lon=sub["lon"], lat=sub["lat"], mode="text",
        text=sub["etiqueta"],
        textfont=dict(size=9, color="#14162B", family="Inter, sans-serif"),
        hoverinfo="skip", showlegend=False,
    ))

    fig_mapa.update_geos(
        fitbounds="locations",
        visible=True,
        showcountries=True, countrycolor="#E7E9F3",
        showcoastlines=True, coastlinecolor="#E7E9F3",
        showland=True, landcolor="#F5F6FA",
        showocean=True, oceancolor="#FFFFFF",
        projection_type="mercator",
        bgcolor="rgba(0,0,0,0)",
    )
    tema_mapa = dict(dl.TEMA_PLOTLY, margin=dict(l=0, r=0, t=0, b=0))
    fig_mapa.update_layout(**tema_mapa, coloraxis_showscale=False)
    fig_mapa.update_traces(selector=dict(type="choropleth"), showscale=False)

    sector_ine = dl.SECTOR_AEAT_A_INE.get(sector_elegido)
    fila_ine = df_ine_anual[(df_ine_anual["sector"] == sector_ine) & (df_ine_anual["sexo"] == "Ambos sexos") & (df_ine_anual["anio"] == 2024)]
    media_ine = float(fila_ine["salario_medio_anual_eur"].iloc[0]) / divisor if len(fila_ine) else None

    comparativa = diferencias_ine_aeat.get(sector_elegido, {})
    media_aeat = comparativa.get("aeat")
    media_aeat = media_aeat / divisor if media_aeat is not None else None
    pct_diferencia = comparativa.get("pct_diferencia")

    sector_percentil = SECTOR_AEAT_A_PERCENTIL.get(sector_elegido)
    fila_mediana = df_percentiles[(df_percentiles["sector"] == sector_percentil) & (df_percentiles["medida"] == "Percentil 50")]
    mediana_real = float(fila_mediana["valor_eur"].iloc[0]) / divisor if len(fila_mediana) else None
    moda_mostrada = dl.MODA_NACIONAL_AGREGADA_2024 / divisor

    def bloque_kpi(valor, etiqueta, tag_texto, tag_clase):
        return html.Div([
            html.P(valor, className="kpi-value", style={"color": color_principal}),
            html.P(etiqueta, className="kpi-label"),
            html.Span(tag_texto, className=f"tag {tag_clase}"),
        ], style={"marginBottom": "14px"})

    nota_comparativa = None
    if media_aeat is not None and pct_diferencia is not None:
        sentido = "más bajo" if pct_diferencia < 0 else "más alto"
        nota_comparativa = html.Div([
            html.P("Dato AEAT usado para el mapa", className="kpi-label", style={"marginBottom": "2px"}),
            html.P(f"{media_aeat:,.0f} € — un {abs(pct_diferencia):.1f}% {sentido} que el INE.",
                   className="kpi-sub"),
            html.P("No existen datos oficiales del INE cruzando sector y Comunidad Autónoma/provincia; "
                   "la AEAT (registros fiscales) y el INE (encuesta) miden con metodologías distintas.",
                   className="kpi-sub", style={"marginTop": "4px"}),
        ], style={"marginTop": "6px", "paddingTop": "10px", "borderTop": "1px dashed var(--border)"})

    etiqueta_kpi = "Salario medio anual" if unidad == "defecto" else "Salario medio mensual (media)"
    etiqueta_mediana = "Mediana (P50)" if unidad == "defecto" else "Mediana (P50) mensual"
    panel = [
        html.Div("Estadísticas nacionales", className="card-modern-header"),
        html.Div([
            bloque_kpi(f"{media_ine:,.0f} €" if media_ine else "—", etiqueta_kpi, "REAL · INE 2024", "tag-real"),
            bloque_kpi(f"{mediana_real:,.0f} €" if mediana_real else "—", etiqueta_mediana, "REAL · INE 2022", "tag-real"),
            nota_comparativa,
            html.Div([
                html.P("El INE no publica moda por sector.", className="kpi-label", style={"marginBottom": "2px"}),
                html.P(f"Moda general de España (todos los sectores, 2024): {moda_mostrada:,.0f} €",
                       className="kpi-sub"),
            ], style={"marginTop": "6px", "paddingTop": "10px", "borderTop": "1px dashed var(--border)"}),
        ], style={"overflowY": "auto", "flex": "1 1 auto", "minHeight": 0}),
    ]

    orden = sub.sort_values("salario_mostrado", ascending=True)
    fig_ranking = px.bar(
        orden, x="salario_mostrado", y="comunidad_autonoma", orientation="h",
        color_discrete_sequence=[color_principal],
        labels={"salario_mostrado": "", "comunidad_autonoma": ""},
    )
    fig_ranking.update_traces(hovertemplate="<b>%{y}</b><br>%{x:,.0f} €<extra></extra>")
    etiqueta_ranking = "€ / año (salario medio)" if unidad == "defecto" else "€ / mes (media)"
    fig_ranking.update_layout(
        **dict(dl.TEMA_PLOTLY, margin=dict(l=8, r=8, t=8, b=30)),
        yaxis=dict(tickfont=dict(size=9)),
        xaxis=dict(tickfont=dict(size=9), title=etiqueta_ranking, title_font=dict(size=10)),
    )

    return fig_mapa, panel, fig_ranking
