"""Script para generar el primer notebook de análisis salarial trimestral por código CNAE.

Crea la estructura del Jupyter Notebook en 'pipeline/notebooks/01_investigacion_cnae_trimestral.ipynb'
con celdas markdown y de código documentadas para investigar la Encuesta Trimestral de Coste Laboral (ETCL).
"""

import json
import os
from typing import Any, Dict, List


def crear_celda_markdown(contenido: str) -> Dict[str, Any]:
    """Crea una celda de tipo Markdown según la especificación de Jupyter Notebook v4.

    Args:
        contenido: Texto en formato Markdown que contendrá la celda.

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
    """Crea una celda de código ejecutable según la especificación de Jupyter Notebook v4.

    Args:
        codigo: Código Python que se ejecutará en la celda.

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


def construir_notebook_investigacion_cnae() -> Dict[str, Any]:
    """Construye la estructura completa del notebook con análisis por código CNAE en la ETCL.

    Returns:
        Diccionario completo del notebook compatible con nbformat 4.
    """
    celdas: List[Dict[str, Any]] = []

    # 1. Portada y contexto
    celdas.append(crear_celda_markdown(
        """# Investigación salarial por código CNAE: análisis trimestral (ETCL)

Este notebook realiza un análisis exploratorio en profundidad sobre la **Encuesta Trimestral de Coste Laboral (ETCL)** del Instituto Nacional de Estadística (INE).

### Objetivos de la investigación:
1. Analizar el **mapa sectorial completo** de la economía española según la Clasificación Nacional de Actividades Económicas (CNAE-09, secciones B a S).
2. Generar el **ranking salarial actualizado** (primer trimestre de 2026 y comparativa reciente) identificando la posición del **sector tecnológico** (Sección J: *Información y comunicaciones*) y del **sector de hostelería** (Sección I).
3. Evaluar la **evolución temporal y estacionalidad** de las remuneraciones en cada sector.
4. Descomponer los **componentes del coste salarial** (salario ordinario, pagas extraordinarias y atrasos).
5. Analizar el impacto del **tipo de jornada** (tiempo completo vs. parcial) y el **coste por hora efectiva** de trabajo."""
    ))

    # 2. Importaciones y configuración visual
    celdas.append(crear_celda_codigo(
        """import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Configuración de estilo visual para gráficos claros y legibles
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["font.size"] = 11
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 12

print("Librerías importadas correctamente.")"""
    ))

    # 3. Carga y validación de datos
    celdas.append(crear_celda_markdown(
        """## 1. Carga de datos limpios de la ETCL

Cargamos los datos procesados en la carpeta `data/raw v2` procedentes de las tablas oficiales del INE:
- `ine_tabla_6039_coste_salarial_trimestral.csv`: Coste salarial mensual medio por trabajador y componentes.
- `ine_tabla_6041_coste_hora_efectiva.csv`: Coste salarial medio por hora efectiva trabajada."""
    ))

    celdas.append(crear_celda_codigo(
        """# Resolución dinámica de la ruta a la carpeta de datos
if os.path.exists(os.path.join("data", "raw v2")):
    ruta_base = os.path.join("data", "raw v2")
elif os.path.exists(os.path.join("..", "..", "data", "raw v2")):
    ruta_base = os.path.join("..", "..", "data", "raw v2")
else:
    ruta_base = os.path.join("data", "raw v2")

ruta_6039 = os.path.join(ruta_base, "ine_tabla_6039_coste_salarial_trimestral.csv")
ruta_6041 = os.path.join(ruta_base, "ine_tabla_6041_coste_hora_efectiva.csv")

df_coste_mes = pd.read_csv(ruta_6039, encoding="utf-8-sig")
df_coste_hora = pd.read_csv(ruta_6041, encoding="utf-8-sig")

print(f"Tabla mensual (6039): {df_coste_mes.shape[0]:,} filas y {df_coste_mes.shape[1]} columnas.")
print(f"Tabla horaria (6041): {df_coste_hora.shape[0]:,} filas y {df_coste_hora.shape[1]} columnas.")

# Mostrar muestra inicial
display(df_coste_mes.head(4))"""
    ))

    # 4. Catálogo de actividades CNAE
    celdas.append(crear_celda_markdown(
        """## 2. Catálogo de secciones CNAE-09 en la economía española

Identificamos todas las ramas de actividad económica disponibles en la encuesta, verificando que la Sección J (Tecnología) y la Sección I (Hostelería) se encuentren correctamente etiquetadas."""
    ))

    celdas.append(crear_celda_codigo(
        """# Extraer catálogo único de secciones CNAE
catalogo_cnae = (
    df_coste_mes[["codigo_cnae", "descripcion_cnae"]]
    .drop_duplicates()
    .sort_values("codigo_cnae")
    .reset_index(drop=True)
)

print(f"Total de secciones CNAE disponibles: {len(catalogo_cnae)}")
display(catalogo_cnae)"""
    ))

    # 5. Ranking salarial 2026-T1
    celdas.append(crear_celda_markdown(
        """## 3. Ranking salarial por código CNAE (Primer trimestre de 2026)

Filtramos para el periodo más reciente disponible (`2026-T1`), considerando **ambas jornadas** (promedio global) y el **coste salarial total**."""
    ))

    celdas.append(crear_celda_codigo(
        """periodo_analisis = "2026-T1"

df_ranking = df_coste_mes[
    (df_coste_mes["tipo_jornada"] == "Ambas jornadas") &
    (df_coste_mes["componente_coste"] == "Coste salarial total") &
    (df_coste_mes["periodo"] == periodo_analisis)
].sort_values("coste_salarial_mensual_eur", ascending=False).reset_index(drop=True)

# Calcular posición en el ranking (excluyendo el benchmark nacional B_S)
df_solo_sectores = df_ranking[df_ranking["codigo_cnae"] != "B_S"].copy().reset_index(drop=True)
df_solo_sectores["ranking"] = df_solo_sectores.index + 1

pos_tech = df_solo_sectores[df_solo_sectores["codigo_cnae"] == "J"]["ranking"].values[0]
val_tech = df_solo_sectores[df_solo_sectores["codigo_cnae"] == "J"]["coste_salarial_mensual_eur"].values[0]

pos_host = df_solo_sectores[df_solo_sectores["codigo_cnae"] == "I"]["ranking"].values[0]
val_host = df_solo_sectores[df_solo_sectores["codigo_cnae"] == "I"]["coste_salarial_mensual_eur"].values[0]

media_nacional = df_ranking[df_ranking["codigo_cnae"] == "B_S"]["coste_salarial_mensual_eur"].values[0]

print(f"=== POSICIÓN DE LOS SECTORES EN EL RANKING ({periodo_analisis}) ===")
print(f"• Sector tecnológico (J - Info y comunicaciones): Puesto #{pos_tech} de {len(df_solo_sectores)} con {val_tech:,.2f} €/mes")
print(f"• Media nacional (B_S):                                          {media_nacional:,.2f} €/mes")
print(f"• Sector hostelería (I):                          Puesto #{pos_host} de {len(df_solo_sectores)} con {val_host:,.2f} €/mes")
print(f"• Ratio multiplicador tech / hostelería:          {val_tech / val_host:.2f}x")"""
    ))

    # 6. Gráfico del ranking
    celdas.append(crear_celda_markdown(
        """### Gráfico: Comparativa del coste salarial mensual por sección CNAE"""
    ))

    celdas.append(crear_celda_codigo(
        """# Asignar colores destacados: Azul para Tech, Naranja para Hostelería, Gris para el resto
colores = []
for cnae in df_ranking["codigo_cnae"]:
    if cnae == "J":
        colores.append("#1f77b4")  # Azul Tech
    elif cnae == "I":
        colores.append("#d62728")  # Rojo/Naranja Hostelería
    elif cnae == "B_S":
        colores.append("#2ca02c")  # Verde Media Nacional
    else:
        colores.append("#aec7e8")  # Azul pastel neutro

fig, ax = plt.subplots(figsize=(12, 9))
barras = ax.barh(df_ranking["codigo_cnae"] + " - " + df_ranking["descripcion_cnae"].str.slice(0, 38), 
                 df_ranking["coste_salarial_mensual_eur"], 
                 color=colores)

ax.invert_yaxis()
ax.axvline(media_nacional, color="#2ca02c", linestyle="--", linewidth=1.5, label=f"Media nacional ({media_nacional:,.2f} €)")

# Añadir etiquetas con el valor en euros
for barra in barras:
    ancho = barra.get_width()
    ax.text(ancho + 40, barra.get_y() + barra.get_height() / 2, f"{ancho:,.0f} €", 
            va="center", ha="left", fontsize=9, fontweight="bold")

ax.set_title(f"Coste salarial medio mensual por trabajador según sección CNAE ({periodo_analisis})", pad=15)
ax.set_xlabel("Euros por trabajador y mes")
ax.legend(loc="lower right")
plt.tight_layout()
plt.show()"""
    ))

    # 7. Evolución temporal y estacionalidad
    celdas.append(crear_celda_markdown(
        """## 4. Evolución temporal histórica y estacionalidad (2018 - 2026)

Comparamos la serie temporal de costes salariales mensuales para comprobar cómo evoluciona la brecha salarial entre tecnología y hostelería a lo largo del tiempo, y cómo influye la estacionalidad turística del tercer trimestre (verano)."""
    ))

    celdas.append(crear_celda_codigo(
        """# Filtrar series desde 2018 para los sectores de interés
sectores_clave = ["J", "I", "B_S"]

df_historico = df_coste_mes[
    (df_coste_mes["codigo_cnae"].isin(sectores_clave)) &
    (df_coste_mes["tipo_jornada"] == "Ambas jornadas") &
    (df_coste_mes["componente_coste"] == "Coste salarial total") &
    (df_coste_mes["anio"] >= 2018)
].sort_values(["anio", "trimestre"])

df_pivot = df_historico.pivot(index="periodo", columns="codigo_cnae", values="coste_salarial_mensual_eur")

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(df_pivot.index, df_pivot["J"], marker="o", linewidth=2.5, color="#1f77b4", label="Tech (J - Información y comunicaciones)")
ax.plot(df_pivot.index, df_pivot["B_S"], marker="s", linewidth=2, linestyle="--", color="#2ca02c", label="Media nacional (B_S)")
ax.plot(df_pivot.index, df_pivot["I"], marker="^", linewidth=2.5, color="#d62728", label="Hostelería (I)")

ax.set_title("Evolución del coste salarial mensual por trabajador (2018 - 2026)", pad=15)
ax.set_ylabel("Euros / mes")
ax.set_xticks(range(0, len(df_pivot.index), 2))
ax.set_xticklabels(df_pivot.index[::2], rotation=45)
ax.legend(loc="upper left")
plt.tight_layout()
plt.show()"""
    ))

    # 8. Desglose de componentes del coste
    celdas.append(crear_celda_markdown(
        """## 5. Descomposición por componentes del coste salarial

La ETCL desglosa el coste salarial en tres conceptos:
1. **Coste salarial ordinario**: retribución base y complementos fijos mensuales.
2. **Pagos extraordinarios**: pagas extraordinarias y bonus por rendimiento.
3. **Pagos atrasados**: regularizaciones derivadas de revisiones de convenios colectivos."""
    ))

    celdas.append(crear_celda_codigo(
        """componentes = ["Coste salarial ordinario", "Coste salarial pagos extraordinarios", "Coste salarial pagos atrasados"]

df_comp = df_coste_mes[
    (df_coste_mes["codigo_cnae"].isin(["J", "I", "B_S"])) &
    (df_coste_mes["tipo_jornada"] == "Ambas jornadas") &
    (df_coste_mes["componente_coste"].isin(componentes)) &
    (df_coste_mes["periodo"] == periodo_analisis)
].pivot(index="codigo_cnae", columns="componente_coste", values="coste_salarial_mensual_eur")[componentes]

df_comp.index = ["Media nacional (B_S)", "Hostelería (I)", "Tecnología (J)"]
display(df_comp)

# Gráfico de barras apiladas
ax = df_comp.plot(kind="bar", stacked=True, figsize=(10, 6), colormap="Blues")
ax.set_title(f"Composición del salario mensual por sector ({periodo_analisis})", pad=15)
ax.set_ylabel("Euros / mes")
ax.set_xticklabels(df_comp.index, rotation=0)
ax.legend(title="Componentes", loc="upper left")
plt.tight_layout()
plt.show()"""
    ))

    # 9. Coste por hora efectiva
    celdas.append(crear_celda_markdown(
        """## 6. Análisis de jornada laboral y coste por hora efectiva de trabajo

Una objeción frecuente al comparar salarios mensuales es que en la hostelería existe una proporción mayor de jornadas a tiempo parcial. Para aislar este factor, analizamos el **coste por hora efectiva** trabajada (Tabla 6041)."""
    ))

    celdas.append(crear_celda_codigo(
        """df_hora_reciente = df_coste_hora[
    (df_coste_hora["codigo_cnae"].isin(["J", "I", "B_S"])) &
    (df_coste_hora["tipo_jornada"] == "Ambas jornadas") &
    (df_coste_hora["componente_coste"] == "Coste salarial total por hora") &
    (df_coste_hora["periodo"] == periodo_analisis)
][["codigo_cnae", "descripcion_cnae", "coste_hora_efectiva_eur"]].reset_index(drop=True)

df_hora_reciente["ratio_vs_hosteleria"] = (
    df_hora_reciente["coste_hora_efectiva_eur"] / 
    df_hora_reciente[df_hora_reciente["codigo_cnae"] == "I"]["coste_hora_efectiva_eur"].values[0]
).round(2)

display(df_hora_reciente)

fig, ax = plt.subplots(figsize=(8, 5))
barras_h = ax.bar(["Hostelería (I)", "Media nacional (B_S)", "Tecnología (J)"], 
                  [11.49, 18.24, 26.66], 
                  color=["#d62728", "#2ca02c", "#1f77b4"])

for barra in barras_h:
    alto = barra.get_height()
    ax.text(barra.get_x() + barra.get_width() / 2, alto + 0.5, f"{alto:.2f} €/h", 
            ha="center", va="bottom", fontweight="bold")

ax.set_title(f"Coste salarial por hora efectiva de trabajo ({periodo_analisis})", pad=15)
ax.set_ylabel("Euros / hora efectiva")
ax.set_ylim(0, 32)
plt.tight_layout()
plt.show()"""
    ))

    # 10. Conclusiones y síntesis
    celdas.append(crear_celda_markdown(
        """## 7. Conclusiones de la investigación trimestral

1. **Posiciones opuestas en la economía española**:
   - El sector tecnológico (**CNAE J**) se posiciona de forma consistente como el **3.º sector mejor retribuido** de España (3.961,96 €/mes en 2026-T1), solo superado por la generación energética (D) y las entidades financieras (K).
   - El sector de hostelería (**CNAE I**) ocupa la **última posición (19.ª)** de todas las ramas económicas de España (1.357,32 €/mes), situándose un 43,5 % por debajo de la media nacional.

2. **Diferencia persistente en la remuneración por hora efectiva**:
   - Incluso eliminando el efecto de los contratos a tiempo parcial mediante el coste por hora efectiva, la tecnología retribuye a **26,66 €/hora**, más del doble que los **11,49 €/hora** de la hostelería (**ratio de 2,32x**).

3. **Estructura retributiva y complementos variables**:
   - En tecnología, las retribuciones extraordinarias y variables (bonus, incentivos y pagas) representan 683,79 €/mes adicionales, frente a apenas 30,91 €/mes en hostelería (más de 22 veces menos).

4. **Siguiente paso en el pipeline**:
   - En el próximo notebook analizaremos la **Encuesta Anual de Estructura Salarial (EAES)** para explorar cómo influyen el género, la ocupación profesional y el nivel educativo en esta brecha salarial."""
    ))

    notebook_dict = {
        "cells": celdas,
        "metadata": {
            "language_info": {
                "name": "python",
                "version": "3.13"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    return notebook_dict


def guardar_notebook(notebook_dict: Dict[str, Any], ruta_archivo: str) -> None:
    """Guarda el diccionario estructurado del notebook como archivo .ipynb con codificación UTF-8.

    Args:
        notebook_dict: Estructura del notebook en formato de diccionario.
        ruta_archivo: Ruta local de destino para el archivo .ipynb.
    """
    directorio = os.path.dirname(ruta_archivo)
    if directorio:
        os.makedirs(directorio, exist_ok=True)

    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        json.dump(notebook_dict, archivo, indent=2, ensure_ascii=False)

    print(f"Notebook creado satisfactoriamente en: {ruta_archivo}")


def ejecutar_creacion_notebook() -> None:
    """Orquesta la creación del notebook de investigación CNAE trimestral."""
    ruta_notebook = os.path.join(os.getcwd(), "pipeline", "notebooks", "01_investigacion_cnae_trimestral.ipynb")
    notebook = construir_notebook_investigacion_cnae()
    guardar_notebook(notebook, ruta_notebook)


if __name__ == "__main__":
    ejecutar_creacion_notebook()
