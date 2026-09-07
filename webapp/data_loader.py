# -*- coding: utf-8 -*-
"""Carga centralizada de los datasets reales para toda la app web.

Todas las fuentes son reales (INE + Agencia Tributaria), ver README_DATOS.md
en la raiz del proyecto para el detalle de procedencia de cada fichero.
"""
import json
import os

import pandas as pd
from dash import dcc, html


def grafico_relleno(id_grafico, figura=None):
    """Envuelve un dcc.Graph para que rellene el 100% de su contenedor flex,
    evitando alturas fijas en px que rompen el layout sin scroll."""
    return html.Div(
        dcc.Graph(
            id=id_grafico,
            figure=figura if figura is not None else {},
            config={"displayModeBar": False, "responsive": True},
            style={"position": "absolute", "top": 0, "left": 0, "right": 0, "bottom": 0, "width": "100%", "height": "100%"},
        ),
        style={"position": "relative", "flex": "1 1 auto", "minHeight": 0},
    )


def agregar_indicador_diferencia(fig, x_pos, y_top, y_bottom, color="#14162B", unidad="€", decimales=0, lado="right"):
    """Añade un corchete vertical + etiqueta mostrando la diferencia numérica
    entre dos lineas en el punto x_pos (normalmente el último periodo real).
    x_pos puede ser un valor numerico (eje anual) o una categoria (eje de
    periodos tipo '2026T1'), ya que Plotly acepta ambos en shapes/annotations
    cuando el eje correspondiente ya tiene esos ticks."""
    if y_top is None or y_bottom is None or y_top == y_bottom:
        return fig
    diferencia = y_top - y_bottom
    fig.add_shape(
        type="line", x0=x_pos, x1=x_pos, y0=y_bottom, y1=y_top,
        line=dict(color=color, width=1.5, dash="dot"), xref="x", yref="y",
    )
    for y_extremo in (y_top, y_bottom):
        fig.add_shape(
            type="line", x0=x_pos, x1=x_pos, y0=y_extremo, y1=y_extremo,
            line=dict(color=color, width=1.5), xref="x", yref="y",
        )
    fig.add_annotation(
        x=x_pos, y=(y_top + y_bottom) / 2,
        text=f"  Δ {diferencia:,.{decimales}f}{unidad}".replace(",", "."),
        showarrow=False, xanchor="left" if lado == "right" else "right",
        font=dict(size=9, color=color, family="Inter, sans-serif"),
        align="left", xshift=6 if lado == "right" else -6,
    )
    return fig


TEMA_PLOTLY = dict(
    font=dict(family="Inter, sans-serif", size=11, color="#14162B"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=8, r=8, t=8, b=8),
    autosize=True,
)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_WEB = os.path.join(RAIZ, "data", "web")
DATA_REAL = os.path.join(RAIZ, "data", "real")

# ---------------------------------------------------------------------------
# Paleta de colores fija de toda la aplicacion
# ---------------------------------------------------------------------------
COLOR_TECH = "#F97316"       # naranja
COLOR_HOSTELERIA = "#2563EB"  # azul
COLOR_AMBOS = "#7C4A26"       # marron
COLOR_TECH_SUAVE = "#FED7AA"
COLOR_HOSTELERIA_SUAVE = "#BFDBFE"
COLOR_AMBOS_SUAVE = "#D6B89C"

SECTOR_TECH = "Información y comunicaciones"
SECTOR_HOSTELERIA = "Hostelería"
SECTOR_TOTAL_ANUAL = "Total nacional"
SECTOR_TOTAL_TRIMESTRAL = "Total (todos los sectores)"

MAPA_COLOR_SECTOR = {
    SECTOR_TECH: COLOR_TECH,
    SECTOR_HOSTELERIA: COLOR_HOSTELERIA,
    SECTOR_TOTAL_ANUAL: COLOR_AMBOS,
    SECTOR_TOTAL_TRIMESTRAL: COLOR_AMBOS,
    "Total (todos los sectores)": COLOR_AMBOS,
    "Hostelería y ocio (aproximación AEAT)": COLOR_HOSTELERIA,
}


def _ruta(*partes):
    return os.path.join(DATA_WEB, *partes)


def cargar_serie_anual():
    df = pd.read_csv(_ruta("01_salario_anual_nacional_por_sector_sexo.csv"), sep=";", encoding="utf-8-sig")
    return df


def cargar_serie_trimestral():
    df = pd.read_csv(_ruta("02_coste_laboral_trimestral_por_sector_jornada.csv"), sep=";", encoding="utf-8-sig")
    return df


def cargar_medio_mediano_modal():
    df = pd.read_csv(_ruta("03_salario_medio_mediano_modal_nacional.csv"), sep=";", encoding="utf-8-sig")
    return df


def cargar_ratios_mediana_moda():
    with open(_ruta("ratios_mediana_moda.json"), encoding="utf-8") as f:
        return json.load(f)


def cargar_ccaa_sector():
    df = pd.read_csv(_ruta("04_salarios_por_ccaa_sector_aeat_2024.csv"), sep=";", encoding="utf-8-sig")
    return df


def cargar_ccaa_todos_sectores():
    df = pd.read_csv(_ruta("04b_salarios_por_ccaa_todos_sectores_aeat_2024.csv"), sep=";", encoding="utf-8-sig")
    return df


def cargar_percentiles_reales():
    """Percentiles REALES (media, P10/25/50/75/90) por sector, INE tabla 36829, año 2022
    (última edición de esta estadística especial). El P50 es la mediana real; el INE no
    publica moda (salario mas frecuente) desglosada por sector, solo a nivel nacional
    agregado (16.520,18 EUR en 2024, todos los sectores)."""
    df = pd.read_csv(_ruta("05_percentiles_reales_por_sector.csv"), sep=";", encoding="utf-8-sig")
    return df


MODA_NACIONAL_AGREGADA_2024 = 16520.18

# Sector AEAT (tal como aparece en 04_salarios_por_ccaa_sector_aeat_2024.csv)
# -> sector INE (tal como aparece en 01_salario_anual_nacional_por_sector_sexo.csv)
SECTOR_AEAT_A_INE = {
    SECTOR_TECH: SECTOR_TECH,
    "Hostelería y ocio (aproximación AEAT)": SECTOR_HOSTELERIA,
    "Total (todos los sectores)": SECTOR_TOTAL_ANUAL,
}


def calcular_diferencias_ine_aeat(anio=2024):
    """Compara, para cada sector, el agregado NACIONAL real de la AEAT (el
    mismo valor que se usa para colorear el mapa) contra el dato NACIONAL
    real del INE (EAES) del mismo año. Devuelve un dict por sector AEAT con
    ambos valores y el % de diferencia, calculado sobre los datos reales
    cargados (no hardcodeado), para que se recalcule solo si los ficheros
    de origen cambian."""
    df_ine = cargar_serie_anual()
    df_aeat = cargar_ccaa_sector()
    resultado = {}
    for sector_aeat, sector_ine in SECTOR_AEAT_A_INE.items():
        fila_ine = df_ine[(df_ine["sector"] == sector_ine) & (df_ine["sexo"] == "Ambos sexos") & (df_ine["anio"] == anio)]
        fila_aeat = df_aeat[(df_aeat["sector"] == sector_aeat) & (df_aeat["comunidad_autonoma"] == "Total Nacional")]
        if len(fila_ine) and len(fila_aeat):
            valor_ine = float(fila_ine["salario_medio_anual_eur"].iloc[0])
            valor_aeat = float(fila_aeat["salario_medio_anual_eur"].iloc[0])
            resultado[sector_aeat] = {
                "ine": valor_ine,
                "aeat": valor_aeat,
                "pct_diferencia": (valor_aeat / valor_ine - 1) * 100,
            }
    return resultado


def cargar_ocupados_por_jornada():
    """Personas ocupadas (miles) y % por tipo de jornada y sector, INE EPA
    (tabla 65149), real, trimestral 2008T1-2026T2 -> incluye el trimestre
    2026T2, más reciente que cualquier otra serie de la app. Incluye también
    tipo_jornada='Total' (todas las jornadas) y sector='Total nacional'
    (toda la economía), usados para calcular la cuota de empleo por sector."""
    df = pd.read_csv(_ruta("06_ocupados_por_jornada_sector.csv"), sep=";", encoding="utf-8-sig")
    return df


def calcular_participacion_empleo(sector):
    """Personas empleadas en un sector y su % sobre el total de ocupados en
    España, real, INE EPA, último trimestre disponible (misma fuente que
    cargar_ocupados_por_jornada)."""
    df = cargar_ocupados_por_jornada()
    ultimo_periodo = df["periodo"].max()
    sub = df[(df["periodo"] == ultimo_periodo) & (df["tipo_jornada"] == "Total")]
    fila_sector = sub[(sub["sector"] == sector) & (sub["unidad"] == "Valor absoluto")]
    fila_total = sub[(sub["sector"] == SECTOR_TOTAL_ANUAL) & (sub["unidad"] == "Valor absoluto")]
    if not len(fila_sector) or not len(fila_total):
        return None
    personas_miles = float(fila_sector["valor"].iloc[0])
    total_miles = float(fila_total["valor"].iloc[0])
    return {
        "personas": personas_miles * 1000,
        "pct_sobre_total": personas_miles / total_miles * 100,
        "periodo": ultimo_periodo,
    }


def cargar_geojson_ccaa():
    with open(os.path.join(DATA_REAL, "spain_ccaa.geojson"), encoding="utf-8") as f:
        return json.load(f)


# Mapeo entre el nombre de CCAA usado en los datos de la AEAT/INE y el
# "name"/"cod_ccaa" usado en el geojson (codeforgermany/click_that_hood).
CCAA_A_GEOJSON = {
    "Andalucía": {"name": "Andalucia", "cod_ccaa": "01"},
    "Aragón": {"name": "Aragon", "cod_ccaa": "02"},
    "Asturias, Principado de": {"name": "Asturias", "cod_ccaa": "03"},
    "Balears, Illes": {"name": "Baleares", "cod_ccaa": "04"},
    "Canarias": {"name": "Canarias", "cod_ccaa": "05"},
    "Cantabria": {"name": "Cantabria", "cod_ccaa": "06"},
    "Castilla y León": {"name": "Castilla-Leon", "cod_ccaa": "07"},
    "Castilla - La Mancha": {"name": "Castilla-La Mancha", "cod_ccaa": "08"},
    "Cataluña": {"name": "Cataluña", "cod_ccaa": "09"},
    "Comunitat Valenciana": {"name": "Valencia", "cod_ccaa": "10"},
    "Extremadura": {"name": "Extremadura", "cod_ccaa": "11"},
    "Galicia": {"name": "Galicia", "cod_ccaa": "12"},
    "Madrid, Comunidad de": {"name": "Madrid", "cod_ccaa": "13"},
    "Murcia, Región de": {"name": "Murcia", "cod_ccaa": "14"},
    "Rioja, La": {"name": "La Rioja", "cod_ccaa": "17"},
    "Ceuta": {"name": "Ceuta", "cod_ccaa": "18"},
    "Melilla": {"name": "Melilla", "cod_ccaa": "19"},
}

# NOTA IMPORTANTE SOBRE COBERTURA: la estadistica "Mercado de Trabajo y
# Pensiones en las Fuentes Tributarias" de la AEAT NO incluye Pais Vasco ni
# Navarra, ya que ambos territorios tienen Hacienda Foral propia (Concierto
# Economico / Convenio) y no declaran el IRPF ante la Agencia Tributaria
# estatal. Por eso no existen en el dataset real y se muestran en el mapa
# como "sin dato disponible (regimen fiscal foral)".
CCAA_SIN_DATO_AEAT = {
    "Pais Vasco": "16",
    "Navarra": "15",
}

# Centroides aproximados (lon, lat) de cada CCAA, usados solo para colocar la
# etiqueta de texto con el salario sobre el mapa (no son datos estadisticos).
CCAA_CENTROIDE = {
    "Andalucía": (-4.6, 37.4),
    "Aragón": (-1.0, 41.4),
    "Asturias, Principado de": (-6.0, 43.2),
    "Balears, Illes": (2.9, 39.4),
    "Canarias": (-15.6, 28.3),
    "Cantabria": (-4.1, 43.2),
    "Castilla y León": (-4.6, 41.6),
    "Castilla - La Mancha": (-3.0, 39.4),
    "Cataluña": (1.6, 41.8),
    "Comunitat Valenciana": (-0.6, 39.4),
    "Extremadura": (-6.1, 39.2),
    "Galicia": (-7.9, 42.7),
    "Madrid, Comunidad de": (-3.7, 40.4),
    "Murcia, Región de": (-1.5, 38.0),
    "Rioja, La": (-2.5, 42.3),
    "Ceuta": (-5.3, 35.7),
    "Melilla": (-2.9, 35.1),
}
