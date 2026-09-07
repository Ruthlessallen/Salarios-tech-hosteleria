"""Módulo para descargar y generar archivos CSV en bruto desde las fuentes oficiales del INE.

Este script realiza dos tareas principales:
1. Descarga directamente las tablas completas en formato CSV publicadas por el INE en su portal de datos abiertos.
2. Procesa y exporta en formato CSV estructurado las series específicas de salarios anuales (EAES),
   costes mensuales (ETCL) y costes por hora efectiva para hostelería y tecnología.
"""

import csv
import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List


def descargar_tabla_csv_ine(id_tabla: int, ruta_destino: str) -> bool:
    """Descarga una tabla completa oficial en formato CSV desde el portal del INE.

    Args:
        id_tabla: Identificador numérico de la tabla en el INE (por ejemplo, 28185, 6039 o 6041).
        ruta_destino: Ruta completa donde se guardará el archivo CSV descargado.

    Returns:
        True si la descarga se completó satisfactoriamente, False en caso de error.
    """
    url = f"https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/{id_tabla}.csv"
    cabeceras = {"User-Agent": "Mozilla/5.0 (compatible; DescargaCSVINE/1.0)"}
    peticion = urllib.request.Request(url, headers=cabeceras)

    try:
        with urllib.request.urlopen(peticion, timeout=30) as respuesta:
            contenido = respuesta.read()
            with open(ruta_destino, "wb") as archivo_salida:
                archivo_salida.write(contenido)
            print(f"Descargada tabla oficial {id_tabla} ({len(contenido):,} bytes) en: {ruta_destino}")
            return True
    except urllib.error.HTTPError as error_http:
        print(f"Error HTTP al descargar tabla {id_tabla}: {error_http.code} - {error_http.reason}")
        return False
    except urllib.error.URLError as error_url:
        print(f"Error de red al descargar tabla {id_tabla}: {error_url.reason}")
        return False


def exportar_csv_salarios_anuales(datos_anuales: Dict[str, Any], ruta_salida: str) -> None:
    """Exporta las series históricas de la Encuesta Anual de Estructura Salarial (EAES) a formato CSV.

    Args:
        datos_anuales: Estructura de diccionario con las series anuales por sector y género.
        ruta_salida: Ruta del archivo CSV de destino.
    """
    filas = []
    nombres_sectores = {
        "sector_tecnologico": "Información y comunicaciones (Tech)",
        "hosteleria": "Hostelería",
        "total_nacional": "Total nacional",
    }
    nombres_generos = {
        "ambos": "Ambos sexos",
        "hombres": "Hombres",
        "mujeres": "Mujeres",
    }

    for clave_sector, generos in datos_anuales.items():
        etiqueta_sector = nombres_sectores.get(clave_sector, clave_sector)
        for clave_genero, info_serie in generos.items():
            etiqueta_genero = nombres_generos.get(clave_genero, clave_genero)
            codigo_ine = info_serie.get("codigo_ine", "")
            historico = info_serie.get("historico", {})
            for anio, salario in sorted(historico.items()):
                filas.append({
                    "anio": anio,
                    "sector": etiqueta_sector,
                    "genero": etiqueta_genero,
                    "codigo_serie_ine": codigo_ine,
                    "salario_medio_anual_bruto_eur": salario,
                })

    with open(ruta_salida, "w", newline="", encoding="utf-8-sig") as archivo_csv:
        campos = ["anio", "sector", "genero", "codigo_serie_ine", "salario_medio_anual_bruto_eur"]
        escritor = csv.DictWriter(archivo_csv, fieldnames=campos, delimiter=";")
        escritor.writeheader()
        escritor.writerows(filas)

    print(f"Exportado archivo de salarios anuales ({len(filas)} registros) en: {ruta_salida}")


def exportar_csv_costes_trimestrales(datos_trimestrales: Dict[str, Any], ruta_salida: str) -> None:
    """Exporta las series de la Encuesta Trimestral de Coste Laboral (ETCL) por mes y trabajador a formato CSV.

    Args:
        datos_trimestrales: Estructura con datos mensuales del coste salarial por sector.
        ruta_salida: Ruta del archivo CSV de destino.
    """
    filas = []
    nombres_sectores = {
        "sector_tecnologico": "Información y comunicaciones (Tech)",
        "hosteleria": "Hostelería",
        "total_nacional": "Total nacional",
    }

    for clave_sector, info_sector in datos_trimestrales.items():
        etiqueta_sector = nombres_sectores.get(clave_sector, clave_sector)
        codigo_ine = info_sector.get("codigo_ine", "")
        for punto in info_sector.get("datos", []):
            filas.append({
                "anio": punto.get("anio"),
                "trimestre": punto.get("trimestre"),
                "periodo": punto.get("periodo_etiqueta"),
                "sector": etiqueta_sector,
                "codigo_serie_ine": codigo_ine,
                "coste_salarial_mensual_eur": punto.get("coste_salarial_mes_eur"),
            })

    with open(ruta_salida, "w", newline="", encoding="utf-8-sig") as archivo_csv:
        campos = ["anio", "trimestre", "periodo", "sector", "codigo_serie_ine", "coste_salarial_mensual_eur"]
        escritor = csv.DictWriter(archivo_csv, fieldnames=campos, delimiter=";")
        escritor.writeheader()
        escritor.writerows(filas)

    print(f"Exportado archivo de costes mensuales ({len(filas)} registros) en: {ruta_salida}")


def exportar_csv_costes_hora(datos_hora: Dict[str, Any], ruta_salida: str) -> None:
    """Exporta las series de coste por hora efectiva de la ETCL a formato CSV.

    Args:
        datos_hora: Estructura con datos de coste salarial por hora trabajada.
        ruta_salida: Ruta del archivo CSV de destino.
    """
    filas = []
    nombres_sectores = {
        "sector_tecnologico": "Información y comunicaciones (Tech)",
        "hosteleria": "Hostelería",
        "total_nacional": "Total nacional",
    }

    for clave_sector, info_sector in datos_hora.items():
        etiqueta_sector = nombres_sectores.get(clave_sector, clave_sector)
        codigo_ine = info_sector.get("codigo_ine", "")
        for punto in info_sector.get("datos", []):
            filas.append({
                "anio": punto.get("anio"),
                "trimestre": punto.get("trimestre"),
                "periodo": punto.get("periodo_etiqueta"),
                "sector": etiqueta_sector,
                "codigo_serie_ine": codigo_ine,
                "coste_hora_efectiva_eur": punto.get("coste_hora_eur"),
            })

    with open(ruta_salida, "w", newline="", encoding="utf-8-sig") as archivo_csv:
        campos = ["anio", "trimestre", "periodo", "sector", "codigo_serie_ine", "coste_hora_efectiva_eur"]
        escritor = csv.DictWriter(archivo_csv, fieldnames=campos, delimiter=";")
        escritor.writeheader()
        escritor.writerows(filas)

    print(f"Exportado archivo de costes por hora ({len(filas)} registros) en: {ruta_salida}")


def exportar_csv_resumen_comparativo(analisis: Dict[str, Any], ruta_salida: str) -> None:
    """Exporta una tabla resumen con los principales indicadores comparativos entre sectores a CSV.

    Args:
        analisis: Métricas comparativas calculadas (anuales, mensuales y por hora).
        ruta_salida: Ruta del archivo CSV de destino.
    """
    comp_anual = analisis.get("comparativa_anual", {})
    comp_trim = analisis.get("comparativa_trimestral", {})
    comp_hora = analisis.get("comparativa_hora", {})

    sal_anual = comp_anual.get("salario_medio_bruto_anual", {})
    sal_mes = comp_trim.get("coste_salarial_mensual_eur", {})
    sal_hora = comp_hora.get("coste_hora_eur", {})

    filas = [
        {
            "indicador": "Salario medio anual bruto (EAES)",
            "periodo": str(comp_anual.get("anio_referencia", "")),
            "unidad": "Euros anuales",
            "sector_tecnologico": sal_anual.get("sector_tecnologico_eur"),
            "hosteleria": sal_anual.get("hosteleria_eur"),
            "total_nacional": sal_anual.get("total_nacional_eur"),
            "ratio_tech_vs_hosteleria": comp_anual.get("multiplo_tech_vs_hosteleria"),
            "diferencia_absoluta_tech_hosteleria": comp_anual.get("diferencia_absoluta_tech_hosteleria_eur"),
        },
        {
            "indicador": "Coste salarial mensual medio (ETCL)",
            "periodo": str(comp_trim.get("periodo_referencia", "")),
            "unidad": "Euros por trabajador y mes",
            "sector_tecnologico": sal_mes.get("sector_tecnologico"),
            "hosteleria": sal_mes.get("hosteleria"),
            "total_nacional": sal_mes.get("total_nacional"),
            "ratio_tech_vs_hosteleria": comp_trim.get("multiplo_tech_vs_hosteleria"),
            "diferencia_absoluta_tech_hosteleria": comp_trim.get("diferencia_mensual_eur"),
        },
        {
            "indicador": "Coste salarial por hora efectiva (ETCL)",
            "periodo": str(comp_hora.get("periodo_referencia", "")),
            "unidad": "Euros por hora efectiva",
            "sector_tecnologico": sal_hora.get("sector_tecnologico"),
            "hosteleria": sal_hora.get("hosteleria"),
            "total_nacional": sal_hora.get("total_nacional"),
            "ratio_tech_vs_hosteleria": comp_hora.get("multiplo_tech_vs_hosteleria"),
            "diferencia_absoluta_tech_hosteleria": comp_hora.get("diferencia_hora_eur"),
        },
    ]

    with open(ruta_salida, "w", newline="", encoding="utf-8-sig") as archivo_csv:
        campos = [
            "indicador",
            "periodo",
            "unidad",
            "sector_tecnologico",
            "hosteleria",
            "total_nacional",
            "ratio_tech_vs_hosteleria",
            "diferencia_absoluta_tech_hosteleria",
        ]
        escritor = csv.DictWriter(archivo_csv, fieldnames=campos, delimiter=";")
        escritor.writeheader()
        escritor.writerows(filas)

    print(f"Exportado resumen comparativo en: {ruta_salida}")


def ejecutar_descargas_y_exportaciones(carpeta_salida: str = "data/raw") -> None:
    """Orquesta la descarga directa de tablas oficiales y la exportación de series en formato CSV.

    Args:
        carpeta_salida: Carpeta de destino donde se guardarán todos los archivos CSV.
    """
    os.makedirs(carpeta_salida, exist_ok=True)
    print(f"Directorio de destino preparado: {os.path.abspath(carpeta_salida)}\n")

    print("--- 1. DESCARGA DIRECTA DE TABLAS COMPLETAS DEL INE EN CSV ---")
    tablas_oficiales = [
        (28185, os.path.join(carpeta_salida, "ine_tabla_28185_estructura_salarial_anual.csv")),
        (6039, os.path.join(carpeta_salida, "ine_tabla_6039_coste_salarial_trimestral.csv")),
        (6041, os.path.join(carpeta_salida, "ine_tabla_6041_coste_hora_efectiva.csv")),
    ]

    for id_tabla, ruta in tablas_oficiales:
        descargar_tabla_csv_ine(id_tabla, ruta)

    print("\n--- 2. EXPORTACIÓN DE SERIES ESPECÍFICAS A CSV ---")
    ruta_json = os.path.join(os.getcwd(), "datos_salarios_espana.json")
    if os.path.exists(ruta_json):
        with open(ruta_json, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        exportar_csv_salarios_anuales(
            datos.get("series_anuales_eaes", {}),
            os.path.join(carpeta_salida, "salarios_anuales_eaes.csv"),
        )
        exportar_csv_costes_trimestrales(
            datos.get("series_trimestrales_etcl", {}),
            os.path.join(carpeta_salida, "costes_salariales_trimestrales_etcl.csv"),
        )
        exportar_csv_costes_hora(
            datos.get("series_coste_hora", {}),
            os.path.join(carpeta_salida, "costes_por_hora_etcl.csv"),
        )
        exportar_csv_resumen_comparativo(
            datos.get("analisis_comparativo", {}),
            os.path.join(carpeta_salida, "comparativa_resumen_tech_vs_hosteleria.csv"),
        )
    else:
        print("Aviso: No se encontró 'datos_salarios_espana.json'. Ejecuta 'consultar_salarios_ine.py' primero.")

    print(f"\nProceso finalizado con éxito. Todos los archivos CSV se encuentran en '{carpeta_salida}'.")


if __name__ == "__main__":
    ejecutar_descargas_y_exportaciones()
