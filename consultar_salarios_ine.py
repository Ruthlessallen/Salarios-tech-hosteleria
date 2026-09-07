"""Módulo para consultar y analizar salarios en España mediante la API oficial del INE.

Este script extrae información oficial del Instituto Nacional de Estadística (INE),
específicamente de:
1. La Encuesta Anual de Estructura Salarial (EAES).
2. La Encuesta Trimestral de Coste Laboral (ETCL).

Compara los sectores de información y comunicaciones (sector tecnológico) y hostelería
frente a la media del total nacional.
"""

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


def consultar_serie_ine(codigo_serie: str, n_ultimos: int = 10) -> Optional[Dict[str, Any]]:
    """Consulta una serie temporal en la API WSTempus del INE.

    Args:
        codigo_serie: Código alfanumérico identificador de la serie en el INE (por ejemplo, 'EAES282').
        n_ultimos: Número de observaciones recientes a recuperar. Por defecto es 10.

    Returns:
        Diccionario con la respuesta JSON del INE o None si ocurre un error durante la petición.
    """
    url = f"https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/{codigo_serie}?nult={n_ultimos}"
    cabeceras = {"User-Agent": "Mozilla/5.0 (compatible; AnalisisSalarios/1.0)"}
    peticion = urllib.request.Request(url, headers=cabeceras)

    try:
        with urllib.request.urlopen(peticion, timeout=15) as respuesta:
            contenido = respuesta.read().decode("utf-8")
            return json.loads(contenido)
    except urllib.error.HTTPError as error_http:
        print(f"Error HTTP al consultar serie {codigo_serie}: {error_http.code} - {error_http.reason}")
        return None
    except urllib.error.URLError as error_url:
        print(f"Error de red al consultar serie {codigo_serie}: {error_url.reason}")
        return None
    except json.JSONDecodeError as error_json:
        print(f"Error al decodificar respuesta JSON para {codigo_serie}: {error_json}")
        return None


def obtener_salarios_anuales(n_anios: int = 6) -> Dict[str, Any]:
    """Obtiene los salarios medios brutos anuales desde la Encuesta Anual de Estructura Salarial (EAES).

    Recupera series para ambos sexos, hombres y mujeres en los sectores de
    información y comunicaciones (sector tech), hostelería y total nacional.

    Args:
        n_anios: Cantidad de años recientes a consultar.

    Returns:
        Diccionario estructurado con las series históricas por sector y género.
    """
    definiciones_series = {
        "total_nacional": {
            "ambos": ("EAES291", "Total nacional (ambos sexos)"),
            "hombres": ("EAES253", "Total nacional (hombres)"),
            "mujeres": ("EAES272", "Total nacional (mujeres)"),
        },
        "sector_tecnologico": {
            "ambos": ("EAES282", "Información y comunicaciones (ambos sexos)"),
            "hombres": ("EAES244", "Información y comunicaciones (hombres)"),
            "mujeres": ("EAES263", "Información y comunicaciones (mujeres)"),
        },
        "hosteleria": {
            "ambos": ("EAES283", "Hostelería (ambos sexos)"),
            "hombres": ("EAES245", "Hostelería (hombres)"),
            "mujeres": ("EAES264", "Hostelería (mujeres)"),
        },
    }

    resultado: Dict[str, Any] = {}

    for clave_sector, generos in definiciones_series.items():
        resultado[clave_sector] = {}
        for clave_genero, (codigo, descripcion) in generos.items():
            datos_raw = consultar_serie_ine(codigo, n_ultimos=n_anios)
            serie_datos: Dict[int, float] = {}
            if datos_raw and "Data" in datos_raw:
                for punto in datos_raw["Data"]:
                    anio = punto.get("Anyo")
                    valor = punto.get("Valor")
                    if anio is not None and valor is not None:
                        serie_datos[int(anio)] = float(valor)
            resultado[clave_sector][clave_genero] = {
                "codigo_ine": codigo,
                "descripcion": descripcion,
                "historico": dict(sorted(serie_datos.items())),
            }

    return resultado


def obtener_costes_salariales_trimestrales(n_trimestres: int = 12) -> Dict[str, Any]:
    """Obtiene el coste salarial mensual por trabajador desde la Encuesta Trimestral de Coste Laboral (ETCL).

    Recupera el coste salarial total promedio mensual para el sector tecnológico,
    el sector de hostelería y la media nacional.

    Args:
        n_trimestres: Número de trimestres recientes a consultar.

    Returns:
        Diccionario con las series trimestrales del coste salarial medio por mes.
    """
    series_etcl = {
        "total_nacional": ("ETCL1527", "Media nacional (industria, construcción y servicios)"),
        "sector_tecnologico": ("ETCL1711", "Información y comunicaciones"),
        "hosteleria": ("ETCL1715", "Hostelería"),
    }

    resultado: Dict[str, Any] = {}

    for sector, (codigo, descripcion) in series_etcl.items():
        datos_raw = consultar_serie_ine(codigo, n_ultimos=n_trimestres)
        serie_trimestral: List[Dict[str, Any]] = []
        if datos_raw and "Data" in datos_raw:
            # Los trimestres en INE suelen usar FK_Periodo: 19=1T, 20=2T, 21=3T, 22=4T
            for punto in sorted(datos_raw["Data"], key=lambda p: (p.get("Anyo", 0), p.get("FK_Periodo", 0))):
                anio = punto.get("Anyo")
                periodo = punto.get("FK_Periodo")
                valor = punto.get("Valor")
                num_trimestre = (periodo - 18) if isinstance(periodo, int) and 19 <= periodo <= 22 else periodo
                serie_trimestral.append({
                    "anio": anio,
                    "trimestre": f"T{num_trimestre}" if isinstance(num_trimestre, int) else str(periodo),
                    "periodo_etiqueta": f"{anio}-T{num_trimestre}",
                    "coste_salarial_mes_eur": valor,
                })
        resultado[sector] = {
            "codigo_ine": codigo,
            "descripcion": descripcion,
            "unidad": "Euros por trabajador y mes",
            "datos": serie_trimestral,
        }

    return resultado


def obtener_costes_por_hora(n_trimestres: int = 8) -> Dict[str, Any]:
    """Obtiene el coste salarial por hora efectiva de trabajo desde la ETCL del INE.

    Args:
        n_trimestres: Número de trimestres recientes a consultar.

    Returns:
        Diccionario con el coste salarial medio por hora trabajada por sector.
    """
    series_hora = {
        "total_nacional": ("ETCL1767", "Media nacional por hora"),
        "sector_tecnologico": ("ETCL1867", "Información y comunicaciones por hora"),
        "hosteleria": ("ETCL1868", "Hostelería por hora"),
    }

    resultado: Dict[str, Any] = {}

    for sector, (codigo, descripcion) in series_hora.items():
        datos_raw = consultar_serie_ine(codigo, n_ultimos=n_trimestres)
        serie_hora: List[Dict[str, Any]] = []
        if datos_raw and "Data" in datos_raw:
            for punto in sorted(datos_raw["Data"], key=lambda p: (p.get("Anyo", 0), p.get("FK_Periodo", 0))):
                anio = punto.get("Anyo")
                periodo = punto.get("FK_Periodo")
                valor = punto.get("Valor")
                num_trimestre = (periodo - 18) if isinstance(periodo, int) and 19 <= periodo <= 22 else periodo
                serie_hora.append({
                    "anio": anio,
                    "trimestre": f"T{num_trimestre}" if isinstance(num_trimestre, int) else str(periodo),
                    "periodo_etiqueta": f"{anio}-T{num_trimestre}",
                    "coste_hora_eur": valor,
                })
        resultado[sector] = {
            "codigo_ine": codigo,
            "descripcion": descripcion,
            "unidad": "Euros por hora efectiva",
            "datos": serie_hora,
        }

    return resultado


def procesar_y_comparar_datos(
    datos_anuales: Dict[str, Any],
    datos_trimestrales: Dict[str, Any],
    datos_hora: Dict[str, Any],
) -> Dict[str, Any]:
    """Calcula indicadores comparativos y brechas entre el sector tecnológico y hostelería.

    Args:
        datos_anuales: Datos extraídos de la encuesta anual de estructura salarial.
        datos_trimestrales: Datos mensuales/trimestrales de coste salarial.
        datos_hora: Datos de coste salarial por hora efectiva.

    Returns:
        Diccionario con métricas comparativas consolidadas (ratios, diferencias y porcentajes).
    """
    # Comparativa anual con el último año disponible en común
    hist_tech = datos_anuales.get("sector_tecnologico", {}).get("ambos", {}).get("historico", {})
    hist_host = datos_anuales.get("hosteleria", {}).get("ambos", {}).get("historico", {})
    hist_tot = datos_anuales.get("total_nacional", {}).get("ambos", {}).get("historico", {})

    anios_comunes = sorted(list(set(hist_tech.keys()) & set(hist_host.keys()) & set(hist_tot.keys())))
    ultimo_anio = anios_comunes[-1] if anios_comunes else None

    comparativa_anual = {}
    if ultimo_anio:
        sal_tech = hist_tech[ultimo_anio]
        sal_host = hist_host[ultimo_anio]
        sal_tot = hist_tot[ultimo_anio]

        # Brechas de género en el último año
        tech_hombres = datos_anuales["sector_tecnologico"]["hombres"]["historico"].get(ultimo_anio, 0.0)
        tech_mujeres = datos_anuales["sector_tecnologico"]["mujeres"]["historico"].get(ultimo_anio, 0.0)
        host_hombres = datos_anuales["hosteleria"]["hombres"]["historico"].get(ultimo_anio, 0.0)
        host_mujeres = datos_anuales["hosteleria"]["mujeres"]["historico"].get(ultimo_anio, 0.0)

        comparativa_anual = {
            "anio_referencia": ultimo_anio,
            "salario_medio_bruto_anual": {
                "sector_tecnologico_eur": sal_tech,
                "hosteleria_eur": sal_host,
                "total_nacional_eur": sal_tot,
            },
            "multiplo_tech_vs_hosteleria": round(sal_tech / sal_host, 2) if sal_host > 0 else None,
            "diferencia_absoluta_tech_hosteleria_eur": round(sal_tech - sal_host, 2),
            "porcentaje_sobre_media_nacional": {
                "sector_tecnologico": round(((sal_tech / sal_tot) - 1.0) * 100, 2),
                "hosteleria": round(((sal_host / sal_tot) - 1.0) * 100, 2),
            },
            "brecha_genero": {
                "sector_tecnologico": {
                    "hombres_eur": tech_hombres,
                    "mujeres_eur": tech_mujeres,
                    "diferencia_porcentual": round(((tech_hombres - tech_mujeres) / tech_hombres) * 100, 2) if tech_hombres else None,
                },
                "hosteleria": {
                    "hombres_eur": host_hombres,
                    "mujeres_eur": host_mujeres,
                    "diferencia_porcentual": round(((host_hombres - host_mujeres) / host_hombres) * 100, 2) if host_hombres else None,
                },
            },
        }

    # Comparativa trimestral reciente (último dato disponible)
    trim_tech = datos_trimestrales.get("sector_tecnologico", {}).get("datos", [])
    trim_host = datos_trimestrales.get("hosteleria", {}).get("datos", [])
    trim_tot = datos_trimestrales.get("total_nacional", {}).get("datos", [])

    comparativa_trimestral = {}
    if trim_tech and trim_host and trim_tot:
        ult_t_tech = trim_tech[-1]
        ult_t_host = trim_host[-1]
        ult_t_tot = trim_tot[-1]

        val_tech = ult_t_tech["coste_salarial_mes_eur"]
        val_host = ult_t_host["coste_salarial_mes_eur"]
        val_tot = ult_t_tot["coste_salarial_mes_eur"]

        comparativa_trimestral = {
            "periodo_referencia": ult_t_tech["periodo_etiqueta"],
            "coste_salarial_mensual_eur": {
                "sector_tecnologico": val_tech,
                "hosteleria": val_host,
                "total_nacional": val_tot,
            },
            "multiplo_tech_vs_hosteleria": round(val_tech / val_host, 2) if val_host > 0 else None,
            "diferencia_mensual_eur": round(val_tech - val_host, 2),
        }

    # Comparativa por hora
    hora_tech = datos_hora.get("sector_tecnologico", {}).get("datos", [])
    hora_host = datos_hora.get("hosteleria", {}).get("datos", [])
    hora_tot = datos_hora.get("total_nacional", {}).get("datos", [])

    comparativa_hora = {}
    if hora_tech and hora_host and hora_tot:
        ult_h_tech = hora_tech[-1]
        ult_h_host = hora_host[-1]
        ult_h_tot = hora_tot[-1]

        val_h_tech = ult_h_tech["coste_hora_eur"]
        val_h_host = ult_h_host["coste_hora_eur"]
        val_h_tot = ult_h_tot["coste_hora_eur"]

        comparativa_hora = {
            "periodo_referencia": ult_h_tech["periodo_etiqueta"],
            "coste_hora_eur": {
                "sector_tecnologico": val_h_tech,
                "hosteleria": val_h_host,
                "total_nacional": val_h_tot,
            },
            "multiplo_tech_vs_hosteleria": round(val_h_tech / val_h_host, 2) if val_h_host > 0 else None,
            "diferencia_hora_eur": round(val_h_tech - val_h_host, 2),
        }

    return {
        "comparativa_anual": comparativa_anual,
        "comparativa_trimestral": comparativa_trimestral,
        "comparativa_hora": comparativa_hora,
    }


def guardar_datos(datos: Dict[str, Any], ruta_archivo: str) -> None:
    """Guarda los datos extraídos y comparados en formato JSON estructurado.

    Args:
        datos: Estructura de datos completa a guardar.
        ruta_archivo: Ruta local de destino para el archivo JSON.
    """
    directorio = os.path.dirname(ruta_archivo)
    if directorio and not os.path.exists(directorio):
        os.makedirs(directorio, exist_ok=True)

    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=2, ensure_ascii=False)
    print(f"Datos guardados correctamente en: {ruta_archivo}")


def ejecutar_consulta_completa() -> None:
    """Función principal que orquesta la descarga, análisis y visualización de datos salariales."""
    print("=" * 70)
    print("CONEXIÓN A LA API OFICIAL DEL INSTITUTO NACIONAL DE ESTADÍSTICA (INE)")
    print("Análisis comparativo de salarios: Sector tecnológico vs. Hostelería")
    print("=" * 70)

    print("\n1. Descargando series anuales (Encuesta Anual de Estructura Salarial - EAES)...")
    datos_anuales = obtener_salarios_anuales(n_anios=6)

    print("2. Descargando series trimestrales (Encuesta Trimestral de Coste Laboral - ETCL)...")
    datos_trimestrales = obtener_costes_salariales_trimestrales(n_trimestres=12)

    print("3. Descargando coste salarial por hora efectiva (ETCL)...")
    datos_hora = obtener_costes_por_hora(n_trimestres=8)

    print("4. Procesando y calculando métricas comparativas...")
    analisis = procesar_y_comparar_datos(datos_anuales, datos_trimestrales, datos_hora)

    paquete_completo = {
        "fuente_principal": "Instituto Nacional de Estadística (INE)",
        "operaciones": [
            "Encuesta Anual de Estructura Salarial (EAES - Operación 140)",
            "Encuesta Trimestral de Coste Laboral (ETCL - Operación 303)",
        ],
        "metodologia": "Clasificación Nacional de Actividades Económicas (CNAE-2009). Sección J (Información y comunicaciones) y Sección I (Hostelería).",
        "analisis_comparativo": analisis,
        "series_anuales_eaes": datos_anuales,
        "series_trimestrales_etcl": datos_trimestrales,
        "series_coste_hora": datos_hora,
    }

    ruta_salida = os.path.join(os.getcwd(), "datos_salarios_espana.json")
    guardar_datos(paquete_completo, ruta_salida)

    # Visualización resumida en consola
    print("\n" + "=" * 70)
    print("RESUMEN DE RESULTADOS OFICIALES DEL INE")
    print("=" * 70)

    comp_anual = analisis.get("comparativa_anual", {})
    if comp_anual:
        anio = comp_anual.get("anio_referencia")
        sal = comp_anual.get("salario_medio_bruto_anual", {})
        mult = comp_anual.get("multiplo_tech_vs_hosteleria")
        pct = comp_anual.get("porcentaje_sobre_media_nacional", {})

        print(f"\n[A] Salario medio bruto anual (EAES - Año {anio}):")
        print(f"  • Sector tecnológico (Inf. y comunicaciones): {sal.get('sector_tecnologico_eur', 0):,.2f} €/año ({pct.get('sector_tecnologico', 0):+.2f}% sobre media nacional)")
        print(f"  • Hostelería:                                 {sal.get('hosteleria_eur', 0):,.2f} €/año ({pct.get('hosteleria', 0):+.2f}% sobre media nacional)")
        print(f"  • Total nacional:                             {sal.get('total_nacional_eur', 0):,.2f} €/año")
        print(f"  --> Ratio: Un trabajador en tecnología percibe {mult} veces el salario medio de hostelería.")

        bg = comp_anual.get("brecha_genero", {})
        print("\n  Brecha de género en el sector tecnológico:")
        print(f"    - Hombres: {bg.get('sector_tecnologico', {}).get('hombres_eur', 0):,.2f} € | Mujeres: {bg.get('sector_tecnologico', {}).get('mujeres_eur', 0):,.2f} € (Brecha: {bg.get('sector_tecnologico', {}).get('diferencia_porcentual', 0)}%)")
        print("  Brecha de género en hostelería:")
        print(f"    - Hombres: {bg.get('hosteleria', {}).get('hombres_eur', 0):,.2f} € | Mujeres: {bg.get('hosteleria', {}).get('mujeres_eur', 0):,.2f} € (Brecha: {bg.get('hosteleria', {}).get('diferencia_porcentual', 0)}%)")

    comp_trim = analisis.get("comparativa_trimestral", {})
    if comp_trim:
        per = comp_trim.get("periodo_referencia")
        mens = comp_trim.get("coste_salarial_mensual_eur", {})
        mult_m = comp_trim.get("multiplo_tech_vs_hosteleria")
        dif_m = comp_trim.get("diferencia_mensual_eur")

        print(f"\n[B] Coste salarial mensual medio por trabajador (ETCL - {per}):")
        print(f"  • Sector tecnológico: {mens.get('sector_tecnologico', 0):,.2f} €/mes")
        print(f"  • Hostelería:         {mens.get('hosteleria', 0):,.2f} €/mes")
        print(f"  • Media nacional:     {mens.get('total_nacional', 0):,.2f} €/mes")
        print(f"  --> Diferencia mensual: {dif_m:,.2f} €/mes adicionales en tecnología (Ratio {mult_m}x).")

    comp_h = analisis.get("comparativa_hora", {})
    if comp_h:
        per_h = comp_h.get("periodo_referencia")
        horas = comp_h.get("coste_hora_eur", {})
        mult_h = comp_h.get("multiplo_tech_vs_hosteleria")

        print(f"\n[C] Coste salarial por hora efectiva de trabajo (ETCL - {per_h}):")
        print(f"  • Sector tecnológico: {horas.get('sector_tecnologico', 0):,.2f} €/hora")
        print(f"  • Hostelería:         {horas.get('hosteleria', 0):,.2f} €/hora")
        print(f"  • Media nacional:     {horas.get('total_nacional', 0):,.2f} €/hora")
        print(f"  --> Ratio por hora efectiva: {mult_h}x más en tecnología.")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    ejecutar_consulta_completa()
