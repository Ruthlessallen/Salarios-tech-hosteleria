# -*- coding: utf-8 -*-
"""App principal: Salarios Tech vs Hosteleria en España (datos reales INE + AEAT)."""
import dash
from dash import Dash, html, dcc, Input, Output, callback

FUENTE_GOOGLE = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[FUENTE_GOOGLE],
    title="Salarios Tech vs Hostelería España",
)
server = app.server

PAGINAS_NAV = [
    ("/", "Comparativa"),
    ("/mapa", "Mapa"),
    ("/detalle-tech", "Tecnología"),
    ("/detalle-hosteleria", "Hostelería"),
]

app.layout = html.Div([
    dcc.Location(id="url-actual"),
    html.Div([
        html.Div([
            html.Div("💶", className="brand-badge"),
            html.Span("Salarios Tech vs Hostelería"),
        ], className="brand"),
        html.Div(id="nav-pills", className="nav-pills-custom"),
        html.Div(
            "Fuentes reales: INE (EAES/ETCL) + Agencia Tributaria 2024 · estimaciones marcadas explícitamente",
            className="info-badge",
        ),
    ], className="top-nav"),
    html.Div(dash.page_container, className="page-wrap"),
], className="app-shell")


@callback(Output("nav-pills", "children"), Input("url-actual", "pathname"))
def actualizar_nav(pathname):
    hijos = []
    for ruta, etiqueta in PAGINAS_NAV:
        clase = "active" if pathname == ruta else ""
        hijos.append(dcc.Link(etiqueta, href=ruta, className=clase))
    return hijos


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=8050)
