# Proyecto de análisis salarial en España: sector tecnológico frente a hostelería

Este proyecto se conecta de forma directa a la interfaz de programación de aplicaciones (API) oficial del **Instituto Nacional de Estadística (INE)** para extraer, estructurar y contrastar datos salariales en España, analizando las diferencias entre el **sector tecnológico** (*información y comunicaciones*, sección J de la CNAE-09) y el **sector de hostelería** (sección I de la CNAE-09), tomando como punto de referencia el conjunto del mercado laboral español.

Adicionalmente, se complementa con la información procedente de otras **fuentes oficiales del Estado español** (Agencia Tributaria, Ministerio de Trabajo y Economía Social, y Seguridad Social) y de ámbito europeo (**Eurostat**).

---

## 1. Fuentes oficiales consultadas

Todas las cifras analizadas provienen exclusivamente de organismos públicos oficiales:

1. **Instituto Nacional de Estadística (INE)**:
   - **Encuesta anual de estructura salarial (EAES - Operación 140)**: ganancia bruta media anual por trabajador, desglosada por sectores de actividad económica (CNAE-2009) y sexo.
   - **Encuesta trimestral de coste laboral (ETCL - Operación 303)**: coste salarial total promedio mensual por empleado y coste salarial por hora efectiva trabajada.
2. **Agencia Estatal de Administración Tributaria (AEAT)**:
   - **Estadística de mercado de trabajo y pensiones en las fuentes tributarias**: salarios declarados por las empresas mediante el modelo 190 (retenciones sobre rendimientos del trabajo).
3. **Ministerio de Trabajo y Economía Social**:
   - **Estadística de convenios colectivos de trabajo**: salarios base, pluses y revisiones salariales pactadas por convenio, contrastando el *Convenio colectivo estatal de empresas de consultoría, tecnologías de la información y estudios de mercado* con los convenios estatales y provinciales de hostelería (*Acuerdo laboral de ámbito estatal para el sector de hostelería - ALEH*).
4. **Ministerio de Inclusión, Seguridad Social y Migraciones**:
   - **Bases de cotización y afiliación a la Seguridad Social**: distribución de la masa laboral según los grupos de cotización (grupos de titulados universitarios e ingenieros vs. grupos de personal no cualificado y de servicios).
5. **Eurostat (Oficina Estadística de la Unión Europea)**:
   - **Encuesta sobre la estructura de los ingresos (*Structure of Earnings Survey - SES*)**: comparativa europea del sector J (*Information and communication*) frente al sector I (*Accommodation and food service activities*).

---

## 2. Resultados clave y comparativa oficial

### A. Salario medio bruto anual (INE - Encuesta anual de estructura salarial)

| Sector / Colectivo | Salario anual (2024) | Salario anual (2023) | Salario anual (2022) | Desviación sobre media nacional |
| :--- | :---: | :---: | :---: | :---: |
| **Sector tecnológico** (*Inf. y comunicaciones*) | **42.741,94 €** | 39.674,43 € | 37.438,55 € | **+44,69 %** |
| **Total nacional** (*Media en España*) | **29.540,26 €** | 28.049,94 € | 26.948,87 € | 0,00 % |
| **Hostelería** | **17.653,42 €** | 16.985,78 € | 16.274,71 € | **-40,24 %** |

- **Ratio tech / hostelería**: el salario medio anual en tecnología multiplica por **2,42 veces** el salario medio de la hostelería (diferencia de **25.088,52 € anuales**).

#### Desglose por género en 2024:
- **Sector tecnológico**:
  - Hombres: 45.054,30 €
  - Mujeres: 38.807,08 €
  - Brecha salarial de género: 13,87 %
- **Hostelería**:
  - Hombres: 19.526,77 €
  - Mujeres: 16.222,08 €
  - Brecha salarial de género: 16,92 %
- **Total nacional**:
  - Hombres: 32.057,55 €
  - Mujeres: 26.904,90 €
  - Brecha salarial de género: 16,07 %

---

### B. Coste salarial mensual por trabajador (INE - Encuesta trimestral de coste laboral)

Datos del primer trimestre de 2026 (última publicación de la ETCL):

| Sector | Coste salarial medio mensual | Diferencia absoluta respecto a hostelería | Ratio |
| :--- | :---: | :---: | :---: |
| **Sector tecnológico** | **3.961,96 € / mes** | +2.604,64 € / mes | **2,92x** |
| **Total nacional** | **2.403,80 € / mes** | +1.046,48 € / mes | 1,77x |
| **Hostelería** | **1.357,32 € / mes** | Referencia base | 1,00x |

---

### C. Coste salarial por hora efectiva trabajada (INE - ETCL)

Al calcular el coste por hora efectiva, se aísla el impacto de la parcialidad horaria:

| Sector | Coste por hora efectiva (2026-T1) | Coste por hora efectiva (2025-T4) | Ratio frente a hostelería |
| :--- | :---: | :---: | :---: |
| **Sector tecnológico** | **26,66 € / hora** | 27,16 € / hora | **2,32x** |
| **Total nacional** | **18,24 € / hora** | 19,84 € / hora | 1,59x |
| **Hostelería** | **11,49 € / hora** | 12,68 € / hora | 1,00x |

---

## 3. Factores determinantes según las fuentes oficiales

Los informes técnicos del INE, la AEAT y el Ministerio de Trabajo señalan cuatro factores estructurales que explican esta disparidad:

1. **Intensidad de la jornada laboral y estacionalidad**:
   - En la hostelería, más del 25 % de los contratos son a tiempo parcial o fijos discontinuos vinculados a campañas turísticas, lo que reduce la remuneración bruta anual por perceptor.
   - En el sector tecnológico, la jornada a tiempo completo representa más del 95 % de las contrataciones.
2. **Nivel formativo y grupo de cotización**:
   - En tecnología, más del 70 % de los ocupados cotiza en los grupos 1 y 2 de la Seguridad Social (ingenieros, licenciados y graduados universitarios).
   - En hostelería predomina la cotización en los grupos 6, 7 y 8 (oficiales de tercera, peones y dependientes), con alta proximidad al salario mínimo interprofesional (SMI).
3. **Productividad y valor añadido bruto (VAB)**:
   - Según la Contabilidad Nacional del INE, el valor añadido por empleado en información y comunicaciones es significativamente superior, lo que permite una mayor capacidad de absorción de costes salariales elevados.
4. **Negociación colectiva y complementos absorbibles**:
   - Mientras que el convenio de hostelería provincial marca en muchas categorías salarios equivalentes o muy cercanos al SMI legal, en el sector TIC el salario real de mercado supera habitualmente las tablas mínimas de convenio debido a la demanda de perfiles especializados.

---

## 4. Estructura del código y archivos del proyecto

El proyecto se organiza en torno a los siguientes archivos y carpetas:

- **[`consultar_salarios_ine.py`](file:///c:/Users/Ruth/Desktop/PROGRAMACION/PROYECTOS/PROYECTOS-PERSONALES/Proyecto%20salarios/consultar_salarios_ine.py)**: Módulo de conexión a la API WSTempus del INE. Contiene las funciones:
  - `descargar_tabla_csv_ine(id_tabla, ruta_destino)`: Descarga directa de tablas completas del portal oficial del INE.
  - `exportar_csv_salarios_anuales(datos_anuales, ruta_salida)`: Exporta a CSV las series anuales por sector y género.
  - `exportar_csv_costes_trimestrales(datos_trimestrales, ruta_salida)`: Exporta a CSV los costes mensuales de la ETCL.
  - `exportar_csv_costes_hora(datos_hora, ruta_salida)`: Exporta a CSV los costes por hora efectiva trabajada.
  - `exportar_csv_resumen_comparativo(analisis, ruta_salida)`: Exporta a CSV la tabla de indicadores comparativos.
  - `ejecutar_descargas_y_exportaciones(carpeta_salida)`: Orquestador general de la descarga y almacenamiento en `data/raw`.

- **[`limpiar_datos_raw.py`](file:///c:/Users/Ruth/Desktop/PROGRAMACION/PROYECTOS/PROYECTOS-PERSONALES/Proyecto%20salarios/limpiar_datos_raw.py)**: Módulo de limpieza y normalización a estándar RFC 4180. Contiene las funciones:
  - `limpiar_numero_ine(valor_str)`: Convierte valores con coma decimal y puntos de miles a float estándar.
  - `separar_codigo_y_descripcion_cnae(texto_cnae)`: Desglosa código CNAE y nombre descriptivo.
  - `separar_periodo_trimestral(periodo_str)`: Separa año, trimestre y etiqueta homogénea.
  - `leer_archivo_ine_con_codificacion(ruta_archivo)`: Detecta y lee con la codificación adecuada.
  - `limpiar_tabla_28185_eaes(ruta_origen, ruta_destino)`: Limpia la tabla anual completa del INE.
  - `limpiar_tabla_trimestral_etcl(ruta_origen, ruta_destino, es_coste_hora)`: Limpia las tablas trimestrales de la ETCL.
  - `limpiar_csv_especifico(ruta_origen, ruta_destino)`: Normaliza las series comparativas filtradas.
  - `ejecutar_limpieza_completa(carpeta_origen, carpetas_destino)`: Orquestador general de la limpieza.

- **[`pipeline/notebooks/`](file:///c:/Users/Ruth/Desktop/PROGRAMACION/PROYECTOS/PROYECTOS-PERSONALES/Proyecto%20salarios/pipeline/notebooks)**: Directorio de notebooks interactivos de análisis exploratorio de datos:
  - **[`01_investigacion_cnae_trimestral.ipynb`](file:///c:/Users/Ruth/Desktop/PROGRAMACION/PROYECTOS/PROYECTOS-PERSONALES/Proyecto%20salarios/pipeline/notebooks/01_investigacion_cnae_trimestral.ipynb)**: Cuaderno de investigación sobre la ETCL por código de actividad CNAE-09. Analiza el catálogo de ramas de actividad (B a S), genera el ranking salarial 2026-T1, visualiza la evolución histórica (2018-2026), desglosa los componentes salariales (ordinario, extraordinario y atrasos) y examina el coste salarial por hora efectiva.

- **[`datos_salarios_espana.json`](file:///c:/Users/Ruth/Desktop/PROGRAMACION/PROYECTOS/PROYECTOS-PERSONALES/Proyecto%20salarios/datos_salarios_espana.json)**: Archivo JSON consolidado con todos los datos y metadatos del INE.

- **[`data/raw/`](file:///c:/Users/Ruth/Desktop/PROGRAMACION/PROYECTOS/PROYECTOS-PERSONALES/Proyecto%20salarios/data/raw)**: Directorio con las descargas en bruto originales del INE (delimitador `;` y formato español).

- **[`data/raw v2/`](file:///c:/Users/Ruth/Desktop/PROGRAMACION/PROYECTOS/PROYECTOS-PERSONALES/Proyecto%20salarios/data/raw%20v2)** (y accesible también en **[`raw v2/`](file:///c:/Users/Ruth/Desktop/PROGRAMACION/PROYECTOS/PROYECTOS-PERSONALES/Proyecto%20salarios/raw%20v2)**): Directorio con los archivos CSV completamente limpios, normalizados y estructurados:
  - Todas las columnas tienen nombres explícitos y únicos (sin columnas vacías ni `Unnamed`).
  - Códigos CNAE separados de las descripciones textuales.
  - Delimitador estándar por comas (`,`) con entrecomillado adecuado de textos con coma.
  - Valores numéricos estandarizados a punto flotante (`29540.26` en lugar de `29.540,26`).
  - Codificación UTF-8 con BOM (`utf-8-sig`) compatible de forma nativa con Python (Pandas), Excel, Power BI y SQL.
  - Archivos incluidos:
    - `ine_tabla_28185_estructura_salarial_anual.csv` (Tabla anual completa limpia)
    - `ine_tabla_6039_coste_salarial_trimestral.csv` (Tabla mensual completa limpia)
    - `ine_tabla_6041_coste_hora_efectiva.csv` (Tabla hora efectiva limpia)
    - `salarios_anuales_eaes.csv` (Serie anual específica tech vs hostelería)
    - `costes_salariales_trimestrales_etcl.csv` (Serie mensual específica tech vs hostelería)
    - `costes_por_hora_etcl.csv` (Serie por hora específica tech vs hostelería)
    - `comparativa_resumen_tech_vs_hosteleria.csv` (Métricas y ratios comparativos limpios)

---

## 5. Instrucciones de ejecución

1. **Consultar la API del INE y generar el archivo JSON consolidado**:
   ```bash
   python consultar_salarios_ine.py
   ```

2. **Descargar los archivos CSV en bruto en `data/raw`**:
   ```bash
   python descargar_csv_ine.py
   ```

3. **Limpiar, normalizar y generar los archivos CSV en `data/raw v2` (y `raw v2`)**:
   ```bash
   python limpiar_datos_raw.py
   ```

4. **Regenerar o ejecutar el notebook de investigación CNAE trimestral**:
   ```bash
   python pipeline/crear_notebook_cnae.py
   ```
   O abrir directamente con Jupyter Lab / Notebook / VS Code:
   `pipeline/notebooks/01_investigacion_cnae_trimestral.ipynb`



