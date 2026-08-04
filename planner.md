# planner.md — Plan de tareas, sesiones y cronograma de Expenses_Classify

Descompone las fases de `manager.md` en **tareas atómicas ejecutables en una
sesión**, les pone dependencias, estimación y fecha referencial, y define cómo se
abre y se cierra cada sesión.

**División de responsabilidades (no duplicar contenido):**
- `manager.md` → **qué orden** y **cuándo una fase está lista** (criterio de salida).
- `planner.md` (este) → **en cuántas tareas** se parte esa fase, **quién depende de
  quién**, **cuántas sesiones** cuesta y **cuándo** se estima hacerlo.
- `memoria.md` → **qué se decidió**. Si una tarea cierra una decisión, la decisión
  vive allá; aquí solo queda la referencia `Dn`.

Regla: si el plan cambia (una tarea se parte, se agrega o se descarta), se
actualiza **este archivo** y, si mueve una fase, la tabla «Estado actual» de
`manager.md`. Un cambio de plan **no** es una decisión de negocio: no va a
`memoria.md` salvo que cambie el alcance del proyecto.

---

## 1. Parámetros del plan (definidos por el usuario, 2026-08-04)
| Parámetro | Valor | Consecuencia sobre el plan |
|---|---|---|
| Ritmo | **2-3 sesiones/semana** (se planifica con 2,5) | Cronograma en semanas, no en días corridos |
| Duración de sesión | **1-2 horas** | Ninguna tarea puede exceder ~2 h → tareas pequeñas y numerosas |
| Deadline de negocio | **Ninguno duro** | Las fechas son **referenciales**; manda la calidad, no el calendario |
| Fecha de arranque del plan | 2026-08-04 | Semana 1 = 2026-08-04 |

**Unidad de estimación: la sesión (1-2 h).** No se estima en horas: el trabajo de
data science tiene varianza alta y una estimación en horas se incumple siempre.
Una tarea que no cabe en una sesión está mal partida → hay que partirla.

## 2. Resumen del proyecto en números
| Fase | Tareas | Sesiones est. | Semanas est. | Ventana referencial |
|---|---|---|---|---|
| 0 — Harness + reconocimiento | 3 | 3 | — | ✅ cerrada |
| 1 — EDA + contrato de datos | 7 | 8 | 3,2 | 2026-08-04 → 2026-08-28 |
| 2 — Baseline + feature engineering | 7 | 9 | 3,6 | 2026-08-31 → 2026-09-25 |
| 3 — Validación robusta | 5 | 6 | 2,4 | 2026-09-28 → 2026-10-09 |
| 4 — Loop humano-en-el-medio | 5 | 7 | 2,8 | 2026-10-12 → 2026-10-30 |
| 5 — Empaquetado | 4 | 5 | 2,0 | 2026-11-02 → 2026-11-13 |
| **Total pendiente** | **28** | **35** | **~15** | **cierre est. 2026-11-13** |

**Cierre estimado del proyecto: mediados de noviembre de 2026** (~3,5 meses).
Este número es una proyección aritmética (35 sesiones ÷ 2,5 por semana), no una
promesa: se **recalcula al cerrar cada fase** con las sesiones realmente gastadas.

### Convención de identificadores
- `TX.Y` = tarea Y de la fase X (ej. `T1.3`). El ID **no se recicla**: si una tarea
  se descarta, queda tachada con el motivo.
- `S-NN` = sesión de trabajo real, numerada correlativa (§6).
- Estado de tarea: ⬜ pendiente · 🟡 en curso · ✅ hecha · 🔴 bloqueada · ⛔ descartada.

## 3. Cómo se abre una sesión (protocolo)
Cada sesión trabaja **una tarea** (o dos, si son triviales y de la misma fase).
No se abre una sesión "a ver qué hago": se abre contra un ID de tarea.

**Apertura (5 min, el agente lo hace solo):**
1. Leer `agente.md` → `manager.md` («Contexto activo») → este archivo.
2. Verificar que existe `glosario_sensibles.md` **antes** de tocar nada sensible
   (`learn.md L2`). Si no existe, eso es lo primero.
3. Tomar la **primera tarea ⬜ cuyas dependencias estén todas ✅**. Si hay varias,
   la de menor ID.
4. Anunciar al usuario: *«Sesión S-NN, tarea TX.Y — [nombre]. Leo [anclas], toco
   [archivos], termino cuando [criterio de salida]»*. Esperar visto bueno si la
   tarea está marcada 🔒 (requiere decisión del usuario).
5. Registrar la fila de la sesión en §6 con estado 🟡.

**Cierre (checklist de `agente.md §6`):**
1. Criterio de salida de la tarea cumplido → marcar ✅ en §4 y en §6.
2. ¿Decisión nueva? → `memoria.md §3` como `Dn` + quitarla de `§5`.
3. ¿Fase avanzada? → «Estado actual» y «Contexto activo» de `manager.md`.
4. ¿Código tocado? → checklist de `datos.md ##6` (repro, semilla, sin leakage,
   métricas registradas).
5. Commit con mensaje que referencie la fase y la tarea:
   `feat(fase1): T1.3 normaliza el target (cierra D11)`.
6. ¿Error detectado? → `learn.md`, aunque no esté resuelto.
7. Dejar escrito en §6 **cuál es la siguiente tarea**, para que la sesión que
   viene arranque en frío sin re-derivar nada.

**🔒 = tarea que no puede cerrarse sin decisión del usuario.** El agente prepara
el análisis y la recomendación; el controller decide (`agente.md §3`).

## 4. Backlog de tareas por fase

### Fase 0 — Harness + reconocimiento ✅ (cerrada, referencia histórica)
| ID | Tarea | Estado | Cerró |
|---|---|---|---|
| T0.1 | Instalar los 4 documentos núcleo + entrada `CLAUDE.md` | ✅ | D1, D2 |
| T0.2 | Reconocimiento de la estructura del Excel | ✅ | `memoria.md §2` |
| T0.3 | Resolver preguntas fundacionales con el usuario | ✅ | D3–D8 |

### Fase 1 — EDA + contrato de datos 🟡 ACTIVA
Dueño: `datos.md`. Criterio de salida de la fase (`manager.md`): dataset
reproducible + contrato de datos en `memoria.md §4` + lista de features
candidatas y prohibidas, validado por el usuario.

| ID | Tarea | Dep. | Ses. | Leer | Tocar | Criterio de salida |
|---|---|---|---|---|---|---|
| ✅ T1.0 | Loader reproducible + dataset tipado | — | 2 | — | `src/loader.py`, `src/build_dataset.py` | 18 tests verdes, artefactos en `data/processed/` (hecho, D9/D10) |
| ✅ T1.1 | Herramienta de asociación (Cramér's V + perfilado) | T1.0 | 1 | `datos.md ##3` | `src/asociacion.py` | Módulo con tests (hecho, commit `a1da976`) |
| ⬜ T1.2 | EDA descriptivo — hojas homogéneas (CUENTA_01–04) | T1.0 | 1 | `datos.md ##3` | `src/eda.py` | Tabla agregada por cuenta: distribución del target, cardinalidad, nulos, duplicados, % de montos negativos. **Sin filas reales** (D5) |
| ⬜ T1.3 | EDA descriptivo — CUENTA_05 (esquema SAP) | T1.0 | 1 | `datos.md ##2`, `memoria.md D8`,`D10` | `src/eda.py` | Mismo perfilado sobre las 648 filas con target; diferencias de esquema documentadas |
| 🔒 ⬜ T1.4 | Higiene y normalización del target | T1.2, T1.3 | 1 | `memoria.md §2` | `src/`, `memoria.md §3` | Criterio escrito para espacios finales, mayúsculas y nombres heterogéneos; **cuántas clases colapsan** medido y aprobado → decisión `Dn` |
| ⬜ T1.5 | Asociación feature↔target por cuenta | T1.4 | 1 | `datos.md ##3` | `src/eda.py` | Ranking de Cramér's V por cuenta; validada o refutada la hipótesis de que la columna S predice T (`memoria.md §2`) |
| ⬜ T1.6 | Auditoría de columnas W/X + criterio "sin valor" en col. AA | T1.3 | 1 | `datos.md ##4`, `memoria.md D8` | `src/`, `memoria.md §4` | Respondido si `Id_Concepto`/`Descripción_Concepto` están alineadas fila-a-fila o son lista pegada al costado; definido "sin valor" (nulo vs. `''` vs. espacios) |
| 🔒 ⬜ T1.7 | Auditoría de leakage y lista de prohibidas | T1.5, T1.6 | 1 | `datos.md ##4` | `memoria.md §4` | Veredicto por columna sospechosa (`NSO`, `Orden`, `Referencia`, `Descripción`, W/X) con la pregunta de `datos.md ##4`; lista de prohibidas aprobada |
| 🔒 ⬜ T1.8 | Redactar el contrato de datos (`memoria.md §4`) | T1.7 | 1 | todo lo anterior | `memoria.md §4`, `manager.md` | §4 completo: columnas, tipos, target (nombre canónico), features candidatas, prohibidas. **Cierra la Fase 1** |

**Riesgo de la fase:** si T1.7 declara prohibida a la columna S (`Concepto`), la
señal disponible cae mucho y la Fase 2 cambia de forma. Es el hallazgo más
importante del proyecto: se resuelve con el usuario, no por métrica.

### Fase 2 — Baseline + feature engineering ⬜
Dueño: `modelo.md` (se crea aquí). Criterio de salida: baseline + primer modelo
con métricas registradas y esquema de validación aprobado.

| ID | Tarea | Dep. | Ses. | Criterio de salida |
|---|---|---|---|---|
| ⬜ T2.1 | Crear `modelo.md` (doc de dominio par de `datos.md`) | T1.8 | 1 | Convenciones de entrenamiento, tracking de experimentos y checklist propio, sin duplicar decisiones |
| 🔒 ⬜ T2.2 | Definir el esquema de validación | T1.8 | 1 | Elegido entre validación temporal (por `Periodo`) y `GroupKFold` con evidencia del EDA; semilla fija; documentado como `Dn` (`datos.md ##5`) |
| ⬜ T2.3 | Baseline honesto por cuenta | T2.2 | 1 | Piso de comparación (clase mayoritaria + regla S→T) con F1 macro y matriz de confusión **por cuenta**. Es el número contra el que se juzga todo lo demás |
| ⬜ T2.4 | Feature engineering — categóricas | T2.3 | 1 | Codificación decidida por cardinalidad (one-hot / target encoding), sin usar prohibidas |
| ⬜ T2.5 | Feature engineering — texto (`Descripción`, `Proveedor`) | T2.3 | 2 | Representación de texto (TF-IDF u otra) construida **dentro** del fold, no antes (evita fuga) |
| ⬜ T2.6 | Primer modelo entrenable por cuenta | T2.4, T2.5 | 2 | N artefactos en `models/`, métricas por cuenta registradas, comparadas contra T2.3 |
| 🔒 ⬜ T2.7 | Revisión de resultados con el usuario | T2.6 | 1 | El controller valida si las predicciones "se parecen a lo que él haría". **Cierra la Fase 2** |

**Nota de alcance (D6):** `CUENTA_02` tiene ~61 filas y 10 clases. En T2.6 se
documenta su limitación en vez de reportar una métrica que no significa nada.

### Fase 3 — Validación robusta y control de overfitting ⬜
Dueño: `modelo.md`. Criterio de salida: métricas estables train/valid/test sin
brecha inaceptable, aprobadas por el usuario.

| ID | Tarea | Dep. | Ses. | Criterio de salida |
|---|---|---|---|---|
| ⬜ T3.1 | Validación cruzada definitiva por cuenta | T2.7 | 1 | CV corrida bajo el esquema de T2.2; métricas con dispersión entre folds, no un número suelto |
| ⬜ T3.2 | Curvas de aprendizaje y diagnóstico de sobreajuste | T3.1 | 1 | Brecha train/valid cuantificada por cuenta; si es inaceptable, simplificar antes de seguir (`datos.md ##5`) |
| ⬜ T3.3 | Calibración de la confianza | T3.2 | 2 | La probabilidad que emite el modelo es confiable como umbral. **Es la precondición técnica de la Fase 4**: sin calibración, el loop consulta lo que no debe |
| ⬜ T3.4 | Análisis de errores por cuenta y en filas atípicas | T3.2 | 1 | Desempeño medido por separado en reclasificaciones, negativos y anulaciones (`memoria.md D7`); fallas sistemáticas reportadas como hallazgo |
| 🔒 ⬜ T3.5 | Informe de métricas y aprobación | T3.3, T3.4 | 1 | Métricas honestas presentadas al usuario (incluido lo que no funciona). **Cierra la Fase 3** |

### Fase 4 — Loop humano-en-el-medio ⬜
Dueño: `modelo.md`. **Bloqueada por `memoria.md §5 P4`** (única pregunta viva).

| ID | Tarea | Dep. | Ses. | Criterio de salida |
|---|---|---|---|---|
| 🔒 ⬜ T4.1 | Resolver P4 — diseño del loop | T3.5 | 1 | Elegido entre aprendizaje activo, validación por lotes o híbrido, con trade-offs. Promueve P4 → `Dn` y **desbloquea la fase** |
| ⬜ T4.2 | Umbral de confianza y cola de revisión | T4.1, T3.3 | 2 | Umbral calibrado con el coste real del error; el modelo separa "clasifico solo" de "pregunto" |
| ⬜ T4.3 | Interfaz de revisión para el controller | T4.2 | 1 | El usuario puede revisar y corregir una tanda sin leer código |
| ⬜ T4.4 | Re-entrenamiento con las correcciones | T4.3 | 2 | Las correcciones vuelven al dataset y mejoran el modelo, **sin contaminar el test set** |
| 🔒 ⬜ T4.5 | Prueba del loop end-to-end con una tanda real | T4.4 | 1 | El controller revisa solo lo dudoso y la métrica mejora tanda a tanda. **Cierra la Fase 4** |

### Fase 5 — Empaquetado sostenible y escalable ⬜
Dueño: `modelo.md`. Criterio de salida: alguien corre la clasificación sobre
datos nuevos sin ayuda del agente.

| ID | Tarea | Dep. | Ses. | Criterio de salida |
|---|---|---|---|---|
| ⬜ T5.1 | Pipeline reproducible de punta a punta | T4.5 | 2 | `datos → features → modelo → inferencia` en un comando, desde el crudo |
| ⬜ T5.2 | Inferencia sobre un archivo nuevo | T5.1 | 1 | Entra un Excel del periodo siguiente, sale clasificado + su cola de dudosos |
| ⬜ T5.3 | Documentación de uso para el controller | T5.2 | 1 | Manual sin jerga de DS: qué correr, qué mirar, qué hacer si algo falla |
| ⬜ T5.4 | Prueba en frío | T5.3 | 1 | **El usuario lo corre solo, sin el agente.** Si se traba, el fallo es de T5.3, no suyo. **Cierra el proyecto** |

## 5. Cronograma referencial
Semana 1 = del 2026-08-04. Base: 2,5 sesiones/semana. Las fechas se
**recalculan al cerrar cada fase**; una fecha vencida no es un fracaso, es una
estimación a corregir aquí.

| Semanas | Ventana | Fase | Tareas previstas | Hito |
|---|---|---|---|---|
| 1-2 | 2026-08-04 → 08-14 | 1 | T1.2, T1.3, T1.4, T1.5 | EDA descrito y target normalizado |
| 3-4 | 2026-08-17 → 08-28 | 1 | T1.6, T1.7, T1.8 | 🏁 **Contrato de datos cerrado (§4)** |
| 5-6 | 2026-08-31 → 09-11 | 2 | T2.1, T2.2, T2.3 | Baseline honesto medido |
| 7-8 | 2026-09-14 → 09-25 | 2 | T2.4, T2.5, T2.6, T2.7 | 🏁 **Primer modelo por cuenta validado** |
| 9-10 | 2026-09-28 → 10-09 | 3 | T3.1 … T3.5 | 🏁 **Métricas estables y calibradas** |
| 11-13 | 2026-10-12 → 10-30 | 4 | T4.1 … T4.5 | 🏁 **Loop humano-en-el-medio funcionando** |
| 14-15 | 2026-11-02 → 11-13 | 5 | T5.1 … T5.4 | 🏁 **Entregado y corrido por el usuario** |

**Ruta crítica:** `T1.8 → T2.2 → T2.6 → T3.3 → T4.2 → T5.1`. Todo retraso ahí
desplaza el cierre; el resto tiene holgura.

**Los tres puntos donde el plan se puede romper (y qué hacer):**
1. **T1.7 prohíbe la columna S por leakage** → la Fase 2 se rediseña sobre texto;
   sumar ~2 sesiones a T2.5. Es el riesgo más probable.
2. **T3.2 muestra sobreajuste severo** → volver a T2.4/T2.5 a simplificar features.
   Presupuestar 2-3 sesiones de vuelta atrás antes de tocar la Fase 4.
3. **`CUENTA_02` no alcanza para entrenar** (61 filas / 10 clases) → se documenta
   como limitación (D6 ya lo anticipa) y esa cuenta queda en revisión 100% humana.
   No se infla el plan intentando salvarla.

## 6. Bitácora de sesiones
Una fila por sesión real. Se llena **al cerrar** cada sesión. La columna
«Siguiente» es lo que permite arrancar en frío la sesión que viene.

| Sesión | Fecha | Tarea | Estado | Qué quedó | Siguiente |
|---|---|---|---|---|---|
| S-01 | 2026-08-03 | T1.0 | ✅ | Loader + dataset (D9, D10), 18 tests | T1.1 |
| S-02 | 2026-08-03 | T1.1 | ✅ | `src/asociacion.py` (Cramér's V + perfilado) | T1.2 |
| S-03 | 2026-08-04 | — | ✅ | Se creó este `planner.md` (plan y cronograma) | **T1.2 — EDA descriptivo de las hojas homogéneas** |

## 7. Cómo se mantiene vivo este plan
- **Al cerrar cada tarea:** marcar ✅ en §4 y añadir la fila en §6. 30 segundos.
- **Al cerrar cada fase:** recalcular §2 y §5 con las sesiones realmente gastadas
  y actualizar «Estado actual» en `manager.md`.
- **Si una tarea toma más de 2 sesiones:** está mal partida → partirla en §4 con
  IDs nuevos y anotar por qué. Que una tarea se desborde es información útil, no
  un error a esconder.
- **Si aparece trabajo no previsto:** entra como tarea nueva al final de su fase,
  nunca "de paso" dentro de otra tarea. El plan debe reflejar lo que pasó.
