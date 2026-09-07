"""Módulo para limpiar, normalizar y estructurar los archivos CSV en bruto del INE.

Corrige los problemas de delimitadores (separador por punto y coma frente a coma estándar),
desglosa campos compuestos (como códigos CNAE y descripciones de actividad), estandariza
formatos numéricos (eliminando puntos de miles y convirtiendo comas decimales a punto)
y asegura que todas las columnas tengan cabeceras explícitas y válidas.
"""

import csv
import os
import re
from typing import List, Optional, Tuple


def limpiar_numero_ine(valor_str: str) -> Optional[float]:
    """Convierte un valor numérico en formato español del INE a float estándar.

    Maneja cadenas con formato '29.540,26', '2.403,8', así como valores nulos o marcas
    estadísticas como '..' o espacios.

    Args:
        valor_str: Cadena de texto con el número a convertir.

    Returns:
        Número flotante equivalente o None si el valor no es numérico.
    """
    if not valor_str:
        return None
    texto = valor_str.strip()
    if texto in ("..", ".", "-", "", "null", "None"):
        return None
    # Eliminar puntos de millar y reemplazar coma decimal por punto
    texto_limpio = texto.replace(".", "").replace(",", ".")
    try:
        return float(texto_limpio)
    except ValueError:
        return None


def separar_codigo_y_descripcion_cnae(texto_cnae: str) -> Tuple[str, str]:
    """Separa el código CNAE de la descripción de la actividad económica.

    Por ejemplo:
    - 'B_S Todas las secciones' -> ('B_S', 'Todas las secciones')
    - 'I Hostelería' -> ('I', 'Hostelería')
    - 'J Información y comunicaciones' -> ('J', 'Información y comunicaciones')
    - 'D Suministro de energía...' -> ('D', 'Suministro de energía...')

    Args:
        texto_cnae: Texto completo que combina código y nombre de la sección CNAE.

    Returns:
        Tupla con (codigo_cnae, descripcion_cnae).
    """
    if not texto_cnae:
        return ("", "")
    texto = texto_cnae.strip()
    coincidencia = re.match(r"^([A-Za-z0-9_]+)\s+(.+)$", texto)
    if coincidencia:
        return (coincidencia.group(1), coincidencia.group(2).strip())
    return ("", texto)


def separar_periodo_trimestral(periodo_str: str) -> Tuple[Optional[int], str, str]:
    """Desglosa una etiqueta de periodo trimestral en año, trimestre y etiqueta homogénea.

    Por ejemplo:
    - '2026T1' -> (2026, 'T1', '2026-T1')
    - '2024-T2' -> (2024, 'T2', '2024-T2')
    - '2023' -> (2023, '', '2023')

    Args:
        periodo_str: Cadena representativa del periodo.

    Returns:
        Tupla con (anio, trimestre, periodo_normalizado).
    """
    if not periodo_str:
        return (None, "", "")
    texto = periodo_str.strip()
    match_trimestre = re.match(r"^(\d{4})[-_\s]?[Tt](\d)$", texto)
    if match_trimestre:
        anio = int(match_trimestre.group(1))
        trimestre = f"T{match_trimestre.group(2)}"
        return (anio, trimestre, f"{anio}-{trimestre}")

    match_anio = re.match(r"^(\d{4})$", texto)
    if match_anio:
        anio = int(match_anio.group(1))
        return (anio, "", str(anio))

    return (None, "", texto)


def leer_archivo_ine_con_codificacion(ruta_archivo: str) -> List[List[str]]:
    """Lee un archivo CSV del INE detectando automáticamente codificación y delimitador.

    Args:
        ruta_archivo: Ruta al archivo CSV en bruto.

    Returns:
        Lista de filas parseadas en formato de cadenas.
    """
    contenido_bytes = b""
    with open(ruta_archivo, "rb") as archivo_bin:
        contenido_bytes = archivo_bin.read()

    # Intentar decodificar con utf-8-sig primero; si falla o hay caracteres rotos, probar cp1252 / latin1
    texto = ""
    for codificacion in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            candidato = contenido_bytes.decode(codificacion)
            # Verificar si contiene caracteres de reemplazo inválidos
            if "\ufffd" not in candidato:
                texto = candidato
                break
        except UnicodeDecodeError:
            continue

    if not texto:
        texto = contenido_bytes.decode("latin1", errors="replace")

    lineas = texto.splitlines()
    if not lineas:
        return []

    primera_linea = lineas[0]
    delimitador = ";" if ";" in primera_linea else ("," if "," in primera_linea else "\t")

    filas = []
    lector = csv.reader(lineas, delimiter=delimitador)
    for fila in lector:
        if fila and any(campo.strip() for campo in fila):
            filas.append([campo.strip() for campo in fila])

    return filas


def limpiar_tabla_28185_eaes(ruta_origen: str, ruta_destino: str) -> None:
    """Limpia y normaliza la tabla 28185 (Estructura Salarial Anual por sección y sexo).

    Args:
        ruta_origen: Ruta al archivo CSV en bruto original.
        ruta_destino: Ruta donde guardar el CSV limpio.
    """
    filas_crudas = leer_archivo_ine_con_codificacion(ruta_origen)
    if not filas_crudas:
        print(f"Aviso: No se pudo leer {ruta_origen}")
        return

    # Cabecera esperada: Secciones de la CNAE 2009; Sexo; Periodo; Total
    filas_limpias = []
    for fila in filas_crudas[1:]:
        if len(fila) < 4:
            continue
        cnae_raw, sexo, periodo_raw, total_raw = fila[0], fila[1], fila[2], fila[3]
        codigo_cnae, descripcion_cnae = separar_codigo_y_descripcion_cnae(cnae_raw)
        anio, _, periodo_norm = separar_periodo_trimestral(periodo_raw)
        salario_anual = limpiar_numero_ine(total_raw)

        filas_limpias.append({
            "codigo_cnae": codigo_cnae,
            "descripcion_cnae": descripcion_cnae,
            "sexo": sexo,
            "anio": anio,
            "periodo": periodo_norm,
            "salario_medio_anual_bruto_eur": salario_anual if salario_anual is not None else "",
        })

    os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
    with open(ruta_destino, "w", newline="", encoding="utf-8-sig") as f_out:
        campos = [
            "codigo_cnae",
            "descripcion_cnae",
            "sexo",
            "anio",
            "periodo",
            "salario_medio_anual_bruto_eur",
        ]
        escritor = csv.DictWriter(f_out, fieldnames=campos, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        escritor.writeheader()
        escritor.writerows(filas_limpias)

    print(f"Limpieza completada para tabla 28185 ({len(filas_limpias)} registros) en: {ruta_destino}")


def limpiar_tabla_trimestral_etcl(ruta_origen: str, ruta_destino: str, es_coste_hora: bool = False) -> None:
    """Limpia y normaliza las tablas de coste laboral trimestral (6039 mensual y 6041 por hora).

    Args:
        ruta_origen: Ruta al archivo CSV en bruto original.
        ruta_destino: Ruta donde guardar el CSV limpio.
        es_coste_hora: Indica si la métrica corresponde a coste por hora efectiva.
    """
    filas_crudas = leer_archivo_ine_con_codificacion(ruta_origen)
    if not filas_crudas:
        print(f"Aviso: No se pudo leer {ruta_origen}")
        return

    # Cabecera esperada: Tipo de jornada; Secciones de la CNAE-09; Componentes del coste; Periodo; Total
    nombre_col_importe = "coste_hora_efectiva_eur" if es_coste_hora else "coste_salarial_mensual_eur"
    filas_limpias = []

    for fila in filas_crudas[1:]:
        if len(fila) < 5:
            continue
        jornada, cnae_raw, componente, periodo_raw, total_raw = fila[0], fila[1], fila[2], fila[3], fila[4]
        codigo_cnae, descripcion_cnae = separar_codigo_y_descripcion_cnae(cnae_raw)
        anio, trimestre, periodo_norm = separar_periodo_trimestral(periodo_raw)
        importe = limpiar_numero_ine(total_raw)

        filas_limpias.append({
            "tipo_jornada": jornada,
            "codigo_cnae": codigo_cnae,
            "descripcion_cnae": descripcion_cnae,
            "componente_coste": componente,
            "anio": anio,
            "trimestre": trimestre,
            "periodo": periodo_norm,
            nombre_col_importe: importe if importe is not None else "",
        })

    os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
    with open(ruta_destino, "w", newline="", encoding="utf-8-sig") as f_out:
        campos = [
            "tipo_jornada",
            "codigo_cnae",
            "descripcion_cnae",
            "componente_coste",
            "anio",
            "trimestre",
            "periodo",
            nombre_col_importe,
        ]
        escritor = csv.DictWriter(f_out, fieldnames=campos, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        escritor.writeheader()
        escritor.writerows(filas_limpias)

    print(f"Limpieza completada para tabla {'6041' if es_coste_hora else '6039'} ({len(filas_limpias)} registros) en: {ruta_destino}")


def limpiar_csv_especifico(ruta_origen: str, ruta_destino: str) -> None:
    """Convierte un archivo CSV de series procesadas a estándar RFC 4180 (coma, comillas y números limpios).

    Args:
        ruta_origen: Archivo CSV original con delimitador por punto y coma.
        ruta_destino: Archivo CSV destino normalizado.
    """
    filas_crudas = leer_archivo_ine_con_codificacion(ruta_origen)
    if not filas_crudas:
        return

    cabecera_original = filas_crudas[0]
    filas_datos = filas_crudas[1:]

    # Normalizar nombres de columnas a formato limpio sin caracteres conflictivos
    cabecera_limpia = [col.strip().lower() for col in cabecera_original]

    os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
    with open(ruta_destino, "w", newline="", encoding="utf-8-sig") as f_out:
        escritor = csv.writer(f_out, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        escritor.writerow(cabecera_limpia)

        for fila in filas_datos:
            fila_limpia = []
            for valor in fila:
                val_limpio = valor.strip()
                # Intentar convertir números si tienen coma decimal
                if re.match(r"^-?\d+(\.\d+)?,\d+$", val_limpio):
                    num = limpiar_numero_ine(val_limpio)
                    fila_limpia.append(str(num) if num is not None else "")
                else:
                    fila_limpia.append(val_limpio)
            escritor.writerow(fila_limpia)

    print(f"Archivo estandarizado ({len(filas_datos)} registros) en: {ruta_destino}")


def ejecutar_limpieza_completa(carpeta_origen: str = "data/raw", carpetas_destino: Optional[List[str]] = None) -> None:
    """Orquesta la limpieza completa y exporta todos los archivos a las carpetas destino indicadas.

    Args:
        carpeta_origen: Carpeta con los archivos CSV en bruto originales.
        carpetas_destino: Lista de rutas de destino donde replicar los archivos limpios.
    """
    if carpetas_destino is None:
        carpetas_destino = [
            os.path.join("data", "raw v2"),
            "raw v2",
        ]

    for carpeta in carpetas_destino:
        os.makedirs(carpeta, exist_ok=True)
        print(f"\n=======================================================")
        print(f"GENERANDO ARCHIVOS LIMPIOS EN: {os.path.abspath(carpeta)}")
        print(f"=======================================================")

        # 1. Limpieza de tablas oficiales completas
        t28185_orig = os.path.join(carpeta_origen, "ine_tabla_28185_estructura_salarial_anual.csv")
        t28185_dest = os.path.join(carpeta, "ine_tabla_28185_estructura_salarial_anual.csv")
        if os.path.exists(t28185_orig):
            limpiar_tabla_28185_eaes(t28185_orig, t28185_dest)

        t6039_orig = os.path.join(carpeta_origen, "ine_tabla_6039_coste_salarial_trimestral.csv")
        t6039_dest = os.path.join(carpeta, "ine_tabla_6039_coste_salarial_trimestral.csv")
        if os.path.exists(t6039_orig):
            limpiar_tabla_trimestral_etcl(t6039_orig, t6039_dest, es_coste_hora=False)

        t6041_orig = os.path.join(carpeta_origen, "ine_tabla_6041_coste_hora_efectiva.csv")
        t6041_dest = os.path.join(carpeta, "ine_tabla_6041_coste_hora_efectiva.csv")
        if os.path.exists(t6041_orig):
            limpiar_tabla_trimestral_etcl(t6041_orig, t6041_dest, es_coste_hora=True)

        # 2. Limpieza de series específicas de tecnología frente a hostelería
        archivos_especificos = [
            "salarios_anuales_eaes.csv",
            "costes_salariales_trimestrales_etcl.csv",
            "costes_por_hora_etcl.csv",
            "comparativa_resumen_tech_vs_hosteleria.csv",
        ]

        for nombre in archivos_especificos:
            orig = os.path.join(carpeta_origen, nombre)
            dest = os.path.join(carpeta, nombre)
            if os.path.exists(orig):
                limpiar_csv_especifico(orig, dest)

    print("\nProceso de limpieza y generación de 'raw v2' finalizado correctamente.")


if __name__ == "__main__":
    ejecutar_limpieza_completa()
