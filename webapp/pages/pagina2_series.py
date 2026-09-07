# -*- coding: utf-8 -*-
"""Página 2 (Comparativa): series temporales (anual EAES y trimestral ETCL) más
la brecha salarial Tech vs Hostelería por provincia (AEAT). Un único toggle de
unidad (por defecto / €·mes) controla los TRES gráficos de la página a la vez."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dash
import plotly.graph_objects as go
from dash import html, dcc, callback, Input, Output

import data_loader as dl

dash.register_page(__name__, path="/", name="Comparativa")

df_anual = dl.cargar_serie_anual()
df_trim = dl.cargar_serie_trimestral()
df_ccaa = dl.cargar_ccaa_sector()

# --- KPIs fijos: multiplicador Tech/Hostelería y su evolución, real ---
def _valor_anual(sector, anio):
    fila = df_anual[(df_anual["sector"] == sector) & (df_anual["sexo"] == "Ambos sexos") & (df_anual["anio"] == anio) & (~df_anual["es_estimacion"])]
    return float(fila["salario_medio_anual_eur"].iloc[0]) if len(fila) else None

_tech_2024 = _valor_anual(dl.SECTOR_TECH, 2024)
_host_2024 = _valor_anual(dl.SECTOR_HOSTELERIA, 2024)
_tech_2008 = _valor_anual(dl.SECTOR_TECH, 2008)
_host_2008 = _valor_anual(dl.SECTOR_HOSTELERIA, 2008)
MULTIPLICADOR_2024 = _tech_2024 / _host_2024
MULTIPLICADOR_2008 = _tech_2008 / _host_2008
CAMBIO_BRECHA = MULTIPLICADOR_2024 - MULTIPLICADOR_2008
ANOS_TRABAJO = _tech_2024 / _host_2024  # mismos años de un hostelero para igualar 1 año de un tecnólogo


def kpi(valor, titulo, sub, color=dl.COLOR_AMBOS):
    return html.Div([
        html.P(valor, className="kpi-value", style={"color": color}),
        html.P(titulo, className="kpi-label"),
        html.P(sub, className="kpi-sub"),
    ], className="card-modern", style={"justifyContent": "center"})


sub_tech = df_ccaa[(df_ccaa["sector"] == dl.SECTOR_TECH) & (df_ccaa["comunidad_autonoma"] != "Total Nacional")][["comunidad_autonoma", "salario_medio_anual_eur"]].rename(columns={"salario_medio_anual_eur": "tech"})
sub_host = df_ccaa[(df_ccaa["sector"] == "Hostelería y ocio (aproximación AEAT)") & (df_ccaa["comunidad_autonoma"] != "Total Nacional")][["comunidad_autonoma", "salario_medio_anual_eur"]].rename(columns={"salario_medio_anual_eur": "hosteleria"})
DF_DIFERENCIAL_BASE = sub_tech.merge(sub_host, on="comunidad_autonoma")
DF_DIFERENCIAL_BASE["diferencia"] = DF_DIFERENCIAL_BASE["tech"] - DF_DIFERENCIAL_BASE["hosteleria"]
DF_DIFERENCIAL_BASE = DF_DIFERENCIAL_BASE.sort_values("diferencia")

layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Comparativa: Tecnología vs Hostelería", className="page-title"),
            html.P("Serie real INE (EAES 2008-2024, ETCL 2008T1-2026T1) y brecha por provincia (AEAT 2024, aproximación en Hostelería).", className="page-subtitle"),
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
        kpi(f"{MULTIPLICADOR_2024:.2f}x", "Tech gana... más que Hostelería (2024)", "salario medio anual · real"),
        kpi(f"{MULTIPLICADOR_2008:.2f}x", "Mismo multiplicador en 2008", "la brecha ya existía hace 16 años"),
        kpi(f"{CAMBIO_BRECHA:+.2f}x", "Cambio en la brecha 2008→2024", "la brecha se ha ampliado" if CAMBIO_BRECHA > 0 else "la brecha se ha reducido"),
        kpi(f"{ANOS_TRABAJO:.1f} años", "de un hostelero", "para igualar el sueldo de 1 año de un tecnólogo"),
    ], className="content-grid", style={"gridTemplateColumns": "repeat(4, 1fr)", "gridTemplateRows": "1fr", "flex": "0 0 100px"}),

    html.Div([
        html.Div([
            html.Div([
                html.Div("Salario medio bruto anual (EAES)", className="card-modern-header", style={"marginBottom": "2px"}),
                html.P("€/mes = dato anual real ÷ 12 (media orientativa, no la paga real de tu nómina) · Δ = diferencia Tech − Hostelería",
                       className="small-muted", style={"margin": "0 0 6px 0"}),
                html.Div([
                    dcc.Dropdown(
                        id="selector-sexo-anual",
                        options=[{"label": s, "value": s} for s in ["Ambos sexos", "Hombres", "Mujeres"]],
                        value="Ambos sexos", clearable=False, style={"width": 180},
                    ),
                ], className="control-bar"),
                dl.grafico_relleno("grafico-serie-anual"),
            ], className="card-modern", style={"flex": "1 1 0"}),

            html.Div([
                html.Div("Coste laboral (ETCL) · real 2008T1-2026T1", className="card-modern-header", style={"marginBottom": "2px"}),
                html.P("Δ = diferencia Tech − Hostelería en el último periodo",
                       className="small-muted", style={"margin": "0 0 6px 0"}),
                html.Div([
                    dcc.Dropdown(
                        id="selector-jornada-trim",
                        options=[{"label": j, "value": j} for j in df_trim["tipo_jornada"].unique()],
                        value="Ambas jornadas", clearable=False, style={"width": 180},
                    ),
                ], className="control-bar"),
                dl.grafico_relleno("grafico-serie-trimestral"),
            ], className="card-modern", style={"flex": "1 1 0"}),
        ], style={"display": "flex", "flexDirection": "column", "gap": "12px", "minHeight": 0, "flex": "1 1 0"}),

        html.Div([
            html.Div("Brecha salarial por provincia · AEAT 2024 (única fuente regional)", className="card-modern-header", style={"marginBottom": "2px"}),
            html.P("Barra apilada: azul = salario Hostelería (aprox.), naranja = lo extra que gana Tech encima. El total de la barra es el salario Tech.",
                   className="small-muted", style={"margin": "0 0 6px 0"}),
            dl.grafico_relleno("grafico-diferencial-ccaa"),
        ], className="card-modern", style={"flex": "1 1 0"}),
    ], className="content-grid", style={"gridTemplateColumns": "1fr 1fr", "gridTemplateRows": "1fr", "flex": "1 1 0"}),
], style={"height": "100%", "display": "flex", "flexDirection": "column", "padding": "16px 24px", "gap": "12px"})


@callback(
    Output("grafico-serie-anual", "figure"),
    Input("selector-sexo-anual", "value"),
    Input("toggle-unidad-pagina", "value"),
)
def actualizar_serie_anual(sexo, unidad):
    divisor = 12 if unidad == "mes" else 1
    fig = go.Figure()
    ultimo_valor = {}
    ultimo_anio = None
    for sector in [dl.SECTOR_TECH, dl.SECTOR_HOSTELERIA, dl.SECTOR_TOTAL_ANUAL]:
        sub = df_anual[(df_anual["sector"] == sector) & (df_anual["sexo"] == sexo) & (~df_anual["es_estimacion"])].sort_values("anio")
        color = dl.MAPA_COLOR_SECTOR.get(sector, dl.COLOR_AMBOS)
        y = sub["salario_medio_anual_eur"] / divisor
        fig.add_trace(go.Scatter(
            x=sub["anio"], y=y, mode="lines+markers",
            name=sector, line=dict(color=color, width=3), marker=dict(size=5),
        ))
        if len(sub):
            ultimo_valor[sector] = float(y.iloc[-1])
            ultimo_anio = int(sub["anio"].iloc[-1])
    dl.agregar_indicador_diferencia(
        fig, ultimo_anio,
        ultimo_valor.get(dl.SECTOR_TECH), ultimo_valor.get(dl.SECTOR_HOSTELERIA),
        color="#14162B", decimales=0,
    )
    anio_min = int(df_anual[~df_anual["es_estimacion"]]["anio"].min())
    anio_max = int(df_anual[~df_anual["es_estimacion"]]["anio"].max())
    etiqueta_y = "€/año" if unidad == "defecto" else "€/mes (media)"
    fig.update_layout(
        **dict(dl.TEMA_PLOTLY, margin=dict(l=8, r=55, t=8, b=8)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=9)),
        xaxis=dict(tickfont=dict(size=9), dtick=4, tickformat="d", range=[anio_min - 0.5, anio_max + 0.5]),
        yaxis=dict(tickfont=dict(size=9), title=etiqueta_y, title_font=dict(size=10)),
    )
    return fig


@callback(
    Output("grafico-serie-trimestral", "figure"),
    Input("selector-jornada-trim", "value"),
    Input("toggle-unidad-pagina", "value"),
)
def actualizar_serie_trimestral(jornada, unidad):
    metrica = "coste_salarial_eur_mes" if unidad == "mes" else "coste_hora_efectiva_eur"
    fig = go.Figure()
    ultimo_valor = {}
    ultimo_periodo = None
    for sector in [dl.SECTOR_TECH, dl.SECTOR_HOSTELERIA, dl.SECTOR_TOTAL_TRIMESTRAL]:
        sub = df_trim[(df_trim["sector"] == sector) & (df_trim["tipo_jornada"] == jornada)].sort_values(["anio", "trimestre"])
        color = dl.MAPA_COLOR_SECTOR.get(sector, dl.COLOR_AMBOS)
        fig.add_trace(go.Scatter(
            x=sub["periodo"], y=sub[metrica], mode="lines", name=sector,
            line=dict(color=color, width=2.5),
        ))
        if len(sub):
            ultimo_valor[sector] = float(sub[metrica].iloc[-1])
            ultimo_periodo = sub["periodo"].iloc[-1]
    dl.agregar_indicador_diferencia(
        fig, ultimo_periodo,
        ultimo_valor.get(dl.SECTOR_TECH), ultimo_valor.get(dl.SECTOR_HOSTELERIA),
        color="#14162B", decimales=1,
    )
    etiqueta_y = "€/hora" if unidad == "defecto" else "€/mes"
    periodos = sub["periodo"].tolist()
    fig.update_layout(
        **dict(dl.TEMA_PLOTLY, margin=dict(l=8, r=55, t=8, b=8)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=9)),
        xaxis=dict(tickmode="array", tickvals=periodos[::8], tickfont=dict(size=9)),
        yaxis=dict(title=etiqueta_y, title_font=dict(size=10), tickfont=dict(size=9)),
    )
    return fig


@callback(Output("grafico-diferencial-ccaa", "figure"), Input("toggle-unidad-pagina", "value"))
def actualizar_diferencial_ccaa(unidad):
    divisor = 12 if unidad == "mes" else 1
    df = DF_DIFERENCIAL_BASE
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["hosteleria"] / divisor, y=df["comunidad_autonoma"], orientation="h",
        name="Hostelería (aprox.)", marker_color=dl.COLOR_HOSTELERIA,
        hovertemplate="<b>%{y}</b><br>Hostelería: %{x:,.0f} €<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=df["diferencia"] / divisor, y=df["comunidad_autonoma"], orientation="h",
        name="Extra que gana Tech", marker_color=dl.COLOR_TECH,
        customdata=df["tech"] / divisor,
        hovertemplate="<b>%{y}</b><br>Tech: %{customdata:,.0f} €<br>Diferencia: %{x:,.0f} €<extra></extra>",
    ))
    etiqueta_x = "€ / año" if unidad == "defecto" else "€ / mes (media)"
    fig.update_layout(
        **dict(dl.TEMA_PLOTLY, margin=dict(l=8, r=8, t=8, b=30)),
        barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=9)),
        yaxis=dict(tickfont=dict(size=9)),
        xaxis=dict(tickfont=dict(size=9), title=f"{etiqueta_x} (azul = Hostelería, + naranja = extra Tech)", title_font=dict(size=10)),
    )
    return fig
