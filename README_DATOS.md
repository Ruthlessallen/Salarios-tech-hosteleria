# Procedencia de los datos (webapp)

Todos los ficheros en `data/web/` se generan con `pipeline/../build_real_datasets.py`
(copia en el scratchpad de la sesión) a partir de descargas RAW en `data/real/`,
todas ellas fuentes oficiales reales:

## 1. Serie anual nacional por sector y sexo (`01_...csv`)
- **Fuente**: INE, API WSTempus (`https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/<codigo>`)
- **Series**: EAES282/244/263 (Información y comunicaciones), EAES283/245/264 (Hostelería),
  EAES291/253/272 (Total nacional)
- **Cobertura real**: 2008-2024. Los años 2025 y 2026 son una **proyección lineal**
  (regresión sobre los últimos 5 años reales), marcados con `es_estimacion=True`.

## 2. Coste laboral trimestral (`02_...csv`)
- **Fuente**: INE jaxiT3, tablas oficiales **6039** (coste salarial) y **6041** (coste
  por hora efectiva), descarga CSV directa (`ine.es/jaxiT3/files/t/es/csv_bdsc/<id>.csv`)
- **Cobertura real**: 2008T1 a 2026T1, por sección CNAE-09 (I Hostelería, J Información
  y comunicaciones) y tipo de jornada (completa/parcial/ambas). 100% real, sin estimaciones.

## 3. Salario medio/mediano/modal nacional (`03_...csv`)
- **Fuente**: INE jaxiT3, tabla **10882** ("Salario anual medio, mediano, modal, a
  tiempo completo y a tiempo parcial")
- Se calculan los ratios reales mediana/media y moda/media (últimos 3 años), usados
  únicamente para **estimar** mediana/moda por CCAA y sector en la página 1 del mapa,
  ya que el INE/AEAT no publican ese cruce específico.

## 4. Salarios por CCAA y sector (`04_...csv` y `04b_...csv`)
- **Fuente**: Agencia Tributaria (AEAT), estadística "Mercado de Trabajo y Pensiones en
  las Fuentes Tributarias" 2024 (IRPF, Modelo 190), páginas oficiales
  `sede.agenciatributaria.gob.es/.../mercado/2024/...`, una página estática por CCAA,
  parseadas y consolidadas.
- **Limitación real e importante**: la AEAT clasifica por 10 grandes grupos NACE, no por
  las 21 secciones CNAE completas. **"Información y comunicaciones" SÍ está aislada**
  (coincide con la sección J). **"Hostelería" NO está aislada**: queda dentro de la bolsa
  "Otros servicios personales y de ocio" junto con actividades artísticas/recreativas y
  otros servicios (secciones R y S). Es la aproximación real más cercana disponible.
- **País Vasco y Navarra no aparecen**: tienen Hacienda Foral propia (Concierto/Convenio
  económico) y no declaran el IRPF ante la AEAT estatal, por lo que no existen en esta
  estadística oficial (no es un error de scraping).

## Mapa geográfico
- `data/real/spain_ccaa.geojson`: límites de comunidades autónomas de
  `codeforgermany/click_that_hood` (repositorio público de GeoJSON).

## Lo que NO se pudo conseguir como dato oficial real
Se investigó exhaustivamente (INE EAES, ETCL tablas 6061/6062/36855/36857, AEAT) y
**no existe ninguna estadística pública española que cruce Hostelería vs Tecnología
por Comunidad Autónoma o provincia** con el nivel de detalle que tenía el dataset
original del proyecto (que era sintético/inventado, no real).
