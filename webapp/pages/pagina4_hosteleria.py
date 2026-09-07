# -*- coding: utf-8 -*-
"""Página 4: Detalle completo del sector Hostelería."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dash
import plotly.graph_objects as go
from dash import html, dcc, callback, Input, Output

import data_loader as dl

dash.register_page(__name__, path="/detalle-hosteleria", name="Hostelería")

SECTOR = dl.SECTOR_HOSTELERIA
COLOR = dl.COLOR_HOSTELERIA

df_anual = dl.cargar_serie_anual()
df_trim = dl.cargar_serie_trimestral()

fila_2024 = df_anual[(df_anual["sector"] == SECTOR) & (df_anual["sexo"] == "Ambos sexos") & (df_anual["anio"] == 2024)]
salario_2024 = float(fila_2024["salario_medio_anual_eur"].iloc[0]) if len(fila_2024) else None
fila_2008 = df_anual[(df_anual["sector"] == SECTOR) & (df_anual["sexo"] == "Ambos sexos") & (df_anual["anio"] == 2008)]
salario_2008 = float(fila_2008["salario_medio_anual_eur"].iloc[0]) if len(fila_2008) else None
crecimiento_pct = ((salario_2024 / salario_2008) - 1) * 100 if salario_2008 else None

hombres_2024 = df_anual[(df_anual["sector"] == SECTOR) & (df_anual["sexo"] == "Hombres") & (df_anual["anio"] == 2024)]["salario_medio_anual_eur"]
mujeres_2024 = df_anual[(df_anual["sector"] == SECTOR) & (df_anual["sexo"] == "Mujeres") & (df_anual["anio"] == 2024)]["salario_medio_anual_eur"]
brecha_genero = None
if len(hombres_2024) and len(mujeres_2024):
    brecha_genero = (1 - float(mujeres_2024.iloc[0]) / float(hombres_2024.iloc[0])) * 100

df_ocupados = dl.cargar_ocupados_por_jornada()
_ultimo_periodo_ocup = df_ocupados["periodo"].max()
_sub_ocup = df_ocupados[(df_ocupados["sector"] == SECTOR) & (df_ocupados["periodo"] == _ultimo_periodo_ocup)]
pct_parcial = _sub_ocup[(_sub_ocup["tipo_jornada"] == "Jornada a tiempo parcial") & (_sub_ocup["unidad"] == "Porcentaje")]["valor"]
personas_parcial = _sub_ocup[(_sub_ocup["tipo_jornada"] == "Jornada a tiempo parcial") & (_sub_ocup["unidad"] == "Valor absoluto")]["valor"]
pct_parcial = float(pct_parcial.iloc[0]) if len(pct_parcial) else None
personas_parcial_miles = float(personas_parcial.iloc[0]) if len(personas_parcial) else None

participacion_empleo = dl.calcular_participacion_empleo(SECTOR)


def kpi(valor, titulo, sub, id_valor=None):
    return html.Div([
        html.P(valor, className="kpi-value", style={"color": COLOR}, id=id_valor) if id_valor else html.P(valor, className="kpi-value", style={"color": COLOR}),
        html.P(titulo, className="kpi-label"),
        html.P(sub, className="kpi-sub"),
    ], className="card-modern", style={"justifyContent": "center"})


layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Hostelería", className="page-title", style={"color": COLOR}),
            html.P("CNAE Sección I · serie nacional 100% real. Ranking por Comunidad Autónoma: ver página Mapa.", className="page-subtitle"),
        ]),
        html.Div([
            dcc.RadioItems(
                id="toggle-unidad-pagina",
                options=[
                    {"label": "€/año · €/hora", "value": "defecto"},
                    {"label": "Todo en €/mes", "value": "mes"},
                ],
                value="defecto", className="segmented-control", inputStyle={"display": "none"},
            ),
        ], className="control-bar", style={"flex": "0 0 auto"}),
    ], className="page-header"),

    html.Div([
        kpi("", "Salario medio 2024", "INE EAES · real", id_valor="kpi-salario-2024-host"),
        kpi(f"{crecimiento_pct:+.1f}%", "Crecimiento 2008→2024", "acumulado · real"),
        kpi(f"{brecha_genero:.1f}%" if brecha_genero else "—", "Brecha de género 2024", "mujeres vs hombres"),
        kpi(f"{pct_parcial:.1f}%" if pct_parcial else "—",
            "En jornada parcial",
            f"{personas_parcial_miles*1000:,.0f} personas · INE EPA {_ultimo_periodo_ocup}".replace(",", ".")),
        kpi(f"{participacion_empleo['pct_sobre_total']:.1f}%" if participacion_empleo else "—",
            "del empleo total en España",
            (f"{participacion_empleo['personas']:,.0f} personas · INE EPA {participacion_empleo['periodo']}".replace(",", ".")
             if participacion_empleo else "")),
    ], className="content-grid", style={"gridTemplateColumns": "repeat(5, 1fr)", "gridTemplateRows": "1fr", "flex": "0 0 100px"}),

    html.Div([
        html.Div([
            html.Div("Salario medio anual por sexo · real 2008-2024", className="card-modern-header", style={"marginBottom": "2px"}),
            html.P("€/mes = dato anual real ÷ 12 (media orientativa)", className="small-muted", style={"margin": "0 0 6px 0"}),
            dl.grafico_relleno("g4-anual"),
        ], className="card-modern"),
        html.Div([
            html.Div("Coste laboral según jornada · real 2008T1-2026T1", className="card-modern-header", style={"marginBottom": "2px"}),
            html.P(f"{pct_parcial:.1f}% de la plantilla trabaja a tiempo parcial (INE EPA {_ultimo_periodo_ocup}, real)"
                   if pct_parcial else "", className="small-muted", style={"margin": "0 0 6px 0"}),
            dl.grafico_relleno("g4-jornada"),
        ], className="card-modern"),
    ], className="content-grid", style={"gridTemplateColumns": "1fr 1fr", "gridTemplateRows": "1fr", "flex": "1 1 0"}),
], style={"height": "100%", "display": "flex", "flexDirection": "column", "padding": "16px 24px", "gap": "12px"})


@callback(
    Output("g4-anual", "figure"),
    Output("kpi-salario-2024-host", "children"),
    Input("toggle-unidad-pagina", "value"),
)
def actualizar_g4_anual(unidad):
    divisor = 12 if unidad == "mes" else 1
    fig = go.Figure()
    ultimo_por_sexo, ultimo_anio_sexo = {}, None
    for sexo, dash_style in [("Ambos sexos", "solid"), ("Hombres", "dot"), ("Mujeres", "dash")]:
        sub = df_anual[(df_anual["sector"] == SECTOR) & (df_anual["sexo"] == sexo) & (~df_anual["es_estimacion"])].sort_values("anio")
        y = sub["salario_medio_anual_eur"] / divisor
        fig.add_trace(go.Scatter(x=sub["anio"], y=y, mode="lines+markers", name=sexo,
                                  line=dict(dash=dash_style, color=COLOR, width=2), marker=dict(size=4)))
        if len(sub):
            ultimo_por_sexo[sexo] = float(y.iloc[-1])
            ultimo_anio_sexo = int(sub["anio"].iloc[-1])
    dl.agregar_indicador_diferencia(fig, ultimo_anio_sexo, ultimo_por_sexo.get("Hombres"), ultimo_por_sexo.get("Mujeres"))
    etiqueta_y = "€/año" if unidad == "defecto" else "€/mes (media)"
    fig.update_layout(**dict(dl.TEMA_PLOTLY, margin=dict(l=8, r=60, t=8, b=8)),
                       legend=dict(orientation="h", y=1.15, font=dict(size=9)),
                       xaxis=dict(tickfont=dict(size=9)),
                       yaxis=dict(tickfont=dict(size=9), title=etiqueta_y, title_font=dict(size=10)))
    texto_kpi = f"{salario_2024/divisor:,.0f} €".replace(",", ".")
    return fig, texto_kpi


@callback(Output("g4-jornada", "figure"), Input("toggle-unidad-pagina", "value"))
def actualizar_g4_jornada(unidad):
    metrica = "coste_salarial_eur_mes" if unidad == "mes" else "coste_hora_efectiva_eur"
    sub_trim = df_trim[df_trim["sector"] == SECTOR].sort_values(["tipo_jornada", "anio", "trimestre"])
    fig = go.Figure()
    colores = {"Ambas jornadas": "#1E3A8A", "Jornada a tiempo completo": COLOR, "Jornada a tiempo parcial": "#93C5FD"}
    for jornada, color in colores.items():
        sub = sub_trim[sub_trim["tipo_jornada"] == jornada]
        fig.add_trace(go.Scatter(x=sub["periodo"], y=sub[metrica], mode="lines", name=jornada, line=dict(color=color, width=2)))
    periodos_t = sorted(sub_trim["periodo"].unique())
    sub_completa = sub_trim[sub_trim["tipo_jornada"] == "Jornada a tiempo completo"]
    sub_parcial = sub_trim[sub_trim["tipo_jornada"] == "Jornada a tiempo parcial"]
    if len(sub_completa) and len(sub_parcial):
        dl.agregar_indicador_diferencia(
            fig, sub_completa["periodo"].iloc[-1],
            float(sub_completa[metrica].iloc[-1]), float(sub_parcial[metrica].iloc[-1]),
            decimales=1,
        )
    etiqueta_y = "€ / hora efectiva" if metrica == "coste_hora_efectiva_eur" else "€ / mes"
    fig.update_layout(**dict(dl.TEMA_PLOTLY, margin=dict(l=8, r=60, t=8, b=8)),
                       legend=dict(orientation="h", y=1.15, font=dict(size=9)),
                       xaxis=dict(tickmode="array", tickvals=periodos_t[::10], tickfont=dict(size=9)),
                       yaxis=dict(tickfont=dict(size=9), title=etiqueta_y, title_font=dict(size=10)))
    return fig
