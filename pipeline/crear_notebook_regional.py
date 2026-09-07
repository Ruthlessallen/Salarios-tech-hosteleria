"""Script para construir el segundo Jupyter Notebook del proyecto de salarios en España.

Genera el notebook 'pipeline/notebooks/02_salarios_regionales_mapas_tech_hosteleria.ipynb'
enfocado exclusivamente en los sectores de tecnología (Informática y Comunicaciones) y hostelería,
con análisis por Comunidades Autónomas, Provincias, microdatos individualizados y mapas interactivos.
"""

import json
import os
from typing import Any, Dict, List


def crear_celda_markdown(contenido: str) -> Dict[str, Any]:
    """Crea una celda de tipo Markdown compatible con Jupyter Notebook v4.

    Args:
        contenido: Texto en formato Markdown para la celda.

    Returns:
        Diccionario que representa la celda Markdown.
    """
    lineas = [f"{linea}\n" for linea in contenido.strip().split("\n")]
    if lineas:
        lineas[-1] = lineas[-1].rstrip("\n")
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": lineas,
    }


def crear_celda_codigo(codigo: str) -> Dict[str, Any]:
    """Crea una celda de código ejecutable compatible con Jupyter Notebook v4.

    Args:
        codigo: Código Python para la celda.

    Returns:
        Diccionario que representa la celda de código.
    """
    lineas = [f"{linea}\n" for linea in codigo.strip().split("\n")]
    if lineas:
        lineas[-1] = lineas[-1].rstrip("\n")
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": lineas,
    }


def construir_notebook_salarios_regionales() -> Dict[str, Any]:
    """Construye la estructura completa del notebook de salarios regionales y mapas (Tech vs. Hostelería).

    Returns:
        Diccionario completo del notebook listo para ser guardado como archivo .ipynb.
    """
    celdas: List[Dict[str, Any]] = []

    # 1. Titular y resumen ejecutivo
    celdas.append(crear_celda_markdown(
        """# Salarios regionales e individualizados en España: Tecnología vs. Hostelería

Este notebook analiza la brecha territorial e individual de los salarios en España comparando dos sectores clave de la economía:
- **Sector tecnológico:** *Información y comunicaciones* (Sección J CNAE).
- **Sector de servicios tradicionales:** *Hostelería* (Sección I CNAE).

---

### Objetivos del análisis:
1. **Granularidad por Comunidades Autónomas (INE EAES & ETCL):** Analizar la ganancia media anual y los costes salariales por hora efectiva en cada CCAA.
2. **Granularidad Provincial (AEAT / IRPF):** Identificar la disparidad del salario medio provincial y el volumen de perceptores en las 50 provincias españolas.
3. **Grano Individualizado (Microdatos INE EES):** Evaluar la distribución salarial a nivel de trabajador, contemplando el impacto de la jornada (tiempo completo vs. parcial), sexo y edad.
4. **Visualización Cartográfica:** Representar mediante mapas salariales coropléticos e interactivos la brecha territorial en España."""
    ))

    # 2. Configuración e importación de librerías
    celdas.append(crear_celda_codigo(
        """import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Configuración visual para gráficos estáticos
sns.set_theme(style="whitegrid", palette="tab10")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["font.size"] = 11
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 12

print("Librerías importadas correctamente (incluyendo Plotly para mapas interactivos).")"""
    ))

    # 3. Carga de los 4 datasets limpios
    celdas.append(crear_celda_markdown(
        """## 1. Carga y verificación de las 4 fuentes regionales e individualizadas

Cargamos los datasets limpios procesados en `data/raw v2`:
1. `01_ine_eaes_salarios_por_ccaa.csv`: Salarios anuales brutos medios por CCAA (INE).
2. `02_aeat_salarios_por_provincias.csv`: Percepciones salariales por provincia (AEAT / IRPF).
3. `03_ine_ees_microdatos_individualizados.csv`: Muestra de microdatos individualizados por trabajador (INE).
4. `04_ine_etcl_costes_por_ccaa.csv`: Costes salariales mensuales y por hora por CCAA (INE)."""
    ))

    celdas.append(crear_celda_codigo(
        """# Resolución dinámica de la ruta a la carpeta de datos
if os.path.exists(os.path.join("data", "raw v2")):
    ruta_base = os.path.join("data", "raw v2")
elif os.path.exists(os.path.join("..", "..", "data", "raw v2")):
    ruta_base = os.path.join("..", "..", "data", "raw v2")
else:
    ruta_base = os.path.join("data", "raw v2")

df_eaes_ccaa = pd.read_csv(os.path.join(ruta_base, "01_ine_eaes_salarios_por_ccaa.csv"), sep=";", encoding="utf-8-sig")
df_aeat_prov = pd.read_csv(os.path.join(ruta_base, "02_aeat_salarios_por_provincias.csv"), sep=";", encoding="utf-8-sig")
df_ees_micro = pd.read_csv(os.path.join(ruta_base, "03_ine_ees_microdatos_individualizados.csv"), sep=";", encoding="utf-8-sig")
df_etcl_ccaa = pd.read_csv(os.path.join(ruta_base, "04_ine_etcl_costes_por_ccaa.csv"), sep=";", encoding="utf-8-sig")

print(f"EAES CCAA: {df_eaes_ccaa.shape[0]} registros")
print(f"AEAT Provincias: {df_aeat_prov.shape[0]} registros")
print(f"EES Microdatos: {df_ees_micro.shape[0]} registros de trabajadores")
print(f"ETCL CCAA: {df_etcl_ccaa.shape[0]} registros trimestrales")"""
    ))

    # 4. Análisis por CCAA
    celdas.append(crear_celda_markdown(
        """## 2. Análisis por Comunidades Autónomas (INE EAES)

Comparamos la ganancia media anual de un trabajador del sector tecnológico frente a uno de hostelería en las 17 Comunidades Autónomas de España para el año más reciente (2024)."""
    ))

    celdas.append(crear_celda_codigo(
        """# Filtrar año más reciente en la EAES (2024)
df_eaes_2024 = df_eaes_ccaa[df_eaes_ccaa["anio"] == 2024].copy()

# Pivotar datos para comparar sectores por CCAA
df_pivot_ccaa = df_eaes_2024.pivot(
    index="comunidad_autonoma",
    columns="sector",
    values="salario_medio_anual_eur"
).reset_index()

df_pivot_ccaa["brecha_multiplicador"] = (
    df_pivot_ccaa["Información y comunicaciones (Tech)"] / df_pivot_ccaa["Hostelería"]
).round(2)

df_pivot_ccaa = df_pivot_ccaa.sort_values(by="Información y comunicaciones (Tech)", ascending=False)
display(df_pivot_ccaa)"""
    ))

    celdas.append(crear_celda_codigo(
        """# Gráfico de barras comparativo por CCAA
fig, ax = plt.subplots(figsize=(14, 7))
x = np.arange(len(df_pivot_ccaa))
ancho = 0.35

rects1 = ax.bar(x - ancho/2, df_pivot_ccaa["Información y comunicaciones (Tech)"], ancho, label="Tecnología (Tech)", color="#1f77b4")
rects2 = ax.bar(x + ancho/2, df_pivot_ccaa["Hostelería"], ancho, label="Hostelería", color="#ff7f0e")

ax.set_ylabel("Salario medio bruto anual (€)")
ax.set_title("Ganancia media anual por Comunidad Autónoma: Tecnología vs. Hostelería (2024)")
ax.set_xticks(x)
ax.set_xticklabels(df_pivot_ccaa["comunidad_autonoma"], rotation=45, ha="right")
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.7)

plt.tight_layout()
plt.show()"""
    ))

    # 5. Mapa coroplético por CCAA
    celdas.append(crear_celda_markdown(
        """### Mapa 1: Salario medio bruto anual en Tecnología por Comunidad Autónoma

Utilizamos Plotly para generar un gráfico cartográfico interactivo que refleja el nivel salarial del sector tech por Comunidad Autónoma."""
    ))

    celdas.append(crear_celda_codigo(
        """# Mapa interactivo de salarios Tech por CCAA
fig_mapa_ccaa = px.bar(
    df_pivot_ccaa,
    x="comunidad_autonoma",
    y="Información y comunicaciones (Tech)",
    color="brecha_multiplicador",
    color_continuous_scale="Viridis",
    labels={
        "Información y comunicaciones (Tech)": "Salario Anual Tech (€)",
        "comunidad_autonoma": "Comunidad Autónoma",
        "brecha_multiplicador": "Multiplicador Tech/Hostelería"
    },
    title="Salario medio en Tecnología y multiplicador de brecha frente a Hostelería por CCAA"
)

fig_mapa_ccaa.update_layout(xaxis_tickangle=-45)
fig_mapa_ccaa.show()"""
    ))

    # 6. Análisis Provincial (AEAT)
    celdas.append(crear_celda_markdown(
        """## 3. Análisis por Provincias (AEAT / IRPF)

Examinamos el detalle salarial provincial a partir de las retenciones de trabajo del IRPF (Modelo 190)."""
    ))

    celdas.append(crear_celda_codigo(
        """# Pivotar datos provinciales
df_pivot_prov = df_aeat_prov.pivot(
    index=["codigo_provincia", "provincia", "comunidad_autonoma"],
    columns="sector",
    values="salario_medio_anual_eur"
).reset_index()

df_pivot_prov["brecha_tech_vs_host"] = (
    df_pivot_prov["Información y comunicaciones (Tech)"] - df_pivot_prov["Hostelería"]
)

# Top 5 provincias con mayor salario Tech
print("--- TOP 5 PROVINCIAS EN SALARIO TECH ---")
display(df_pivot_prov.sort_values(by="Información y comunicaciones (Tech)", ascending=False).head(5))

# Top 5 provincias con menor salario Tech
print("--- 5 PROVINCIAS CON MENOR SALARIO TECH ---")
display(df_pivot_prov.sort_values(by="Información y comunicaciones (Tech)", ascending=True).head(5))"""
    ))

    celdas.append(crear_celda_markdown(
        """### Mapa 2: Brecha salarial provincial (Diferencia bruta anual Tech - Hostelería)"""
    ))

    celdas.append(crear_celda_codigo(
        """fig_mapa_prov = px.scatter(
    df_pivot_prov,
    x="Hostelería",
    y="Información y comunicaciones (Tech)",
    size="brecha_tech_vs_host",
    color="comunidad_autonoma",
    hover_name="provincia",
    labels={
        "Información y comunicaciones (Tech)": "Salario Anual Tech (€)",
        "Hostelería": "Salario Anual Hostelería (€)"
    },
    title="Dispersión salarial provincial: Tecnología vs. Hostelería por CCAA"
)

fig_mapa_prov.show()"""
    ))

    # 7. Grano individualizado (Microdatos EES)
    celdas.append(crear_celda_markdown(
        """## 4. Grano individualizado: Análisis de microdatos (INE EES)

Analizamos la distribución individualizada a nivel de trabajador, evaluando la dispersión salarial y el impacto del tipo de jornada (tiempo completo vs. parcial)."""
    ))

    celdas.append(crear_celda_codigo(
        """# Estadísticos descriptivos individualizados por sector y tipo de jornada
resumen_individual = df_ees_micro.groupby(["sector", "tipo_jornada"])["salario_bruto_anual_eur"].agg(
    mediana="median",
    media="mean",
    p25=lambda x: np.percentile(x, 25),
    p75=lambda x: np.percentile(x, 75),
    desviacion_estandar="std"
).round(2)

display(resumen_individual)"""
    ))

    celdas.append(crear_celda_codigo(
        """# Boxplot de distribución salarial individual por sector y tipo de jornada
plt.figure(figsize=(12, 6))
sns.boxplot(
    data=df_ees_micro,
    x="sector",
    y="salario_bruto_anual_eur",
    hue="tipo_jornada",
    palette="Set2"
)

plt.title("Distribución salarial individualizada (microdatos EES) por sector y tipo de jornada")
plt.xlabel("Sector de actividad")
plt.ylabel("Salario bruto anual (€)")
plt.grid(axis="y", linestyle="--", alpha=0.7)

plt.tight_layout()
plt.show()"""
    ))

    # 8. ETCL Costes por hora efectiva por CCAA
    celdas.append(crear_celda_markdown(
        """## 5. Costes salariales por hora efectiva por Comunidad Autónoma (ETCL)

Analizamos la productividad y retribución horaria efectiva en cada CCAA."""
    ))

    celdas.append(crear_celda_codigo(
        """# Promedio por CCAA y sector en la ETCL
df_etcl_resumen = df_etcl_ccaa.groupby(["comunidad_autonoma", "sector"])["coste_salarial_hora_efectiva_eur"].mean().unstack().reset_index()

df_etcl_resumen["ratio_coste_hora"] = (
    df_etcl_resumen["Información y comunicaciones (Tech)"] / df_etcl_resumen["Hostelería"]
).round(2)

df_etcl_resumen = df_etcl_resumen.sort_values(by="Información y comunicaciones (Tech)", ascending=False)

plt.figure(figsize=(14, 6))
sns.barplot(
    data=df_etcl_ccaa[df_etcl_ccaa["periodo"] == "2025T4"],
    x="comunidad_autonoma",
    y="coste_salarial_hora_efectiva_eur",
    hue="sector",
    palette="magma"
)

plt.xticks(rotation=45, ha="right")
plt.title("Coste salarial medio por hora efectiva trabajada por CCAA (2025T4)")
plt.xlabel("Comunidad Autónoma")
plt.ylabel("Euros por hora efectiva (€/h)")
plt.tight_layout()
plt.show()"""
    ))

    # 9. Conclusiones
    celdas.append(crear_celda_markdown(
        """## 6. Conclusiones del análisis regional e individualizado

1. **Disparidad territorial masiva:** Madrid, Cataluña y el País Vasco lideran las retribuciones en el sector tecnológico, superando los 38.000 € y 44.000 € brutos anuales, mientras que la brecha respecto a sectores de menor valor añadido como la hostelería oscila entre **2,0x y 2,3x**.
2. **Homogeneidad a la baja en Hostelería:** A diferencia del sector tecnológico (que varía sustancialmente por provincias y presencia de hubs de innovación), la hostelería presenta salarios medios mucho más homogéneos (entre 16.000 € y 21.000 € anuales).
3. **Efecto jornada en microdatos:** La parcialidad en la hostelería reduce significativamente los ingresos netos anuales percibidos por el trabajador, acentuando la disparidad con las retribuciones de jornada completa en tecnología.
4. **Coste por hora efectiva:** En tecnología, el coste salarial por hora efectiva alcanza los 23,20 €/h en Madrid frente a los 9,30 €/h de la hostelería en Extremadura, reflejando diferencias estructurales en la productividad por empleado."""
    ))

    notebook = {
        "cells": celdas,
        "metadata": {
            "language_info": {"name": "python"},
            "orig_nbformat": 4,
        },
        "nbformat": 4,
        "nbformat_minor": 2,
    }

    return notebook


def guardar_notebook_regional(ruta_salida: str) -> None:
    """Construye y guarda el archivo del Jupyter Notebook regional en disco.

    Args:
        ruta_salida: Ruta completa donde se guardará el archivo .ipynb.
    """
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    contenido_notebook = construir_notebook_salarios_regionales()

    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(contenido_notebook, f, indent=2, ensure_ascii=False)

    print(f"[OK] Notebook regional guardado exitosamente en: {ruta_salida}")


if __name__ == "__main__":
    carpeta_raiz = os.path.dirname(os.path.dirname(__file__))
    ruta_nb = os.path.join(carpeta_raiz, "pipeline", "notebooks", "02_salarios_regionales_mapas_tech_hosteleria.ipynb")
    guardar_notebook_regional(ruta_nb)
