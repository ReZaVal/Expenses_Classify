# datos.md — Cómo se trabajan los datos en Expenses_Classify

Doc de dominio. Responde "¿cómo se leen, limpian, exploran y validan los datos
aquí?" con **convenciones**, no con decisiones (esas van a `memoria.md`). Dueño
de la Fase 1. Cuando arranque el modelado se creará `modelo.md` como par.

## 1. Fuente y carga
- Fuente única: `data/raw/Clasificacion_de_cuentas_GS_2026.xlsx` (local,
  gitignored por defecto — ver `memoria.md §5 P2`). Ubica el archivo ahí antes
  de correr nada.
- Cargar con `pandas.read_excel(..., sheet_name=...)` u `openpyxl` con
  `data_only=True` (el Excel tiene fórmulas; se quiere el valor calculado).
- Las hojas de detalle tienen el encabezado en la **fila 1**; los datos empiezan
  en la fila 2. Las hojas `Resumen *` y `Sheet1` son tablas dinámicas/resúmenes
  — **no** son fuente de entrenamiento.
- Estructura de directorios: `data/raw/` (crudo, inmutable), `data/processed/`
  (derivados reproducibles), `src/` o `notebooks/` (código), `models/`
  (artefactos). Todos salvo `src/` están gitignored por defecto.

## 2. Consolidación y limpieza (convenciones)
- Consolidar las hojas de detalle homogéneas (CUENTA_01–04) en un solo DataFrame,
  agregando la `Cuenta` como columna. La hoja `CUENTA_05` tiene otro esquema:
  tratarla aparte hasta resolver `memoria.md §5 P6`.
- Tipar explícitamente: fechas a `datetime`, montos (`US$`, `NSO`) a numérico,
  categóricas a `category`, IDs a string (no numérico — no son cantidades).
- **Nunca modificar el crudo.** Toda limpieza produce un artefacto nuevo en
  `data/processed/`, con el código que lo generó versionado en `src/`.
- Documentar cada decisión de limpieza no trivial (filas descartadas, imputación
  de nulos) — si cambia el criterio, es una decisión → `memoria.md`.

## 3. EDA — qué mirar siempre (para "clasificar como un humano")
- **Distribución de clases** del target por cuenta: hay desbalance fuerte
  documentado (`memoria.md §2`). Elegir métricas que no premien predecir la
  mayoría (F1 macro, balanced accuracy, matriz de confusión), no accuracy sola.
- **Cardinalidad** de categóricas (Proveedor, Centro de Costo) y de texto
  (Descripción): decide si van one-hot, target/embedding o texto (TF-IDF).
- **Nulos y vacíos**: hay celdas `''`, `None` y `0` mezclados; homogeneizar.
- **Duplicados y casi-duplicados**: hay filas casi idénticas (mismo proveedor,
  distinta medida) — cuidado al partir train/test para no filtrar copias.
- **Correlación/asociación con el target**: para categóricas usar Cramér's V o
  información mutua, no Pearson. Buscar señal real, distinguirla de leakage (§4).

## 4. Control de *data leakage* (crítico para no auto-engañarse)
Antes de aceptar una feature, preguntar: **"¿este valor existiría ANTES de que el
controller clasifique, o es consecuencia de haber clasificado?"** Si es
consecuencia, es leakage y se prohíbe.
- Sospechosas de leakage (a auditar y confirmar con el usuario): `Concepto` como
  feature de sí mismo, `Descripción_Concepto`, `Id_Concepto`, posiblemente
  `Orden`, `NSO`, `Referencia`. Registrar el veredicto en `memoria.md §4`.
- Las columnas prohibidas se listan explícitamente en `memoria.md §4` y NO se
  usan como feature aunque mejoren la métrica (una métrica inflada por leakage es
  peor que nada: engaña al usuario).

## 5. Partición y validación (anti-overfitting)
- Definir el esquema de validación **antes** de entrenar y documentarlo en
  `memoria.md`. Candidatos según decisión de alcance (`§5 P3`) y naturaleza del
  dato:
  - Si hay señal temporal (columna `Periodo`/`Fecha`): considerar validación
    temporal (entrenar en meses previos, validar en posteriores) para simular
    uso real.
  - Si hay casi-duplicados o grupos (mismo documento/orden): considerar
    `GroupKFold` por grupo para no filtrar copias entre train y test.
- Semilla aleatoria fija y registrada. Reportar train vs. validación vs. test:
  una brecha grande = overfitting → simplificar antes de seguir.
- Nunca tocar el test set hasta el final. Nunca elegir features/hiperparámetros
  mirando el test.

## 6. Checklist de validación de datos/experimentos (correr en el cierre)
1. [ ] El artefacto se regenera desde el crudo con código versionado (repro).
2. [ ] Semilla fija y registrada.
3. [ ] Ninguna feature usada está en la lista de prohibidas por leakage
       (`memoria.md §4`).
4. [ ] Partición train/valid/test documentada y sin fugas entre particiones.
5. [ ] Métricas reportadas incluyen las robustas al desbalance (F1 macro /
       balanced acc / matriz de confusión), no solo accuracy.
6. [ ] Resultados (métricas + config) registrados para poder compararlos luego.
7. [ ] Ninguna data cruda sensible quedó staged para commit sin visto bueno
       (`memoria.md §5 P2`).
