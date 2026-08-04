# manager — Director de Expenses_Classify

No explica el cómo (eso está en los docs de dominio): dice en qué orden se hace
el trabajo, qué documento es dueño de cada pieza, y cuál es el criterio para
pasar de fase.

## ⚠️ REGLA PRIORITARIA — Seudonimización (leer SIEMPRE, antes de cualquier commit)
En **todo** lo que se versiona (código y `.md`) van **solo seudónimos**, nunca
data sensible real. Términos sensibles = números de cuenta, nombres de
concepto/programa, nombre de la empresa y códigos internos → usar `CUENTA_0X`,
`CONCEPTO_0XX`, `EMPRESA_0X`, `IMP_0X`. El mapa real ↔ seudónimo vive **solo** en
`glosario_sensibles.md` (gitignored, nunca a GitHub). Antes de commitear:
1. Si introdujiste un término sensible nuevo, agrégalo primero al glosario y usa
   su seudónimo en el doc.
2. Verifica que ningún `.md`/código staged contiene valores reales
   (ver `agente.md §4` y `learn.md L1`). Decisión de fondo: `memoria.md D4`.

## Mapa de documentos
| Documento | Responde a |
|---|---|
| `agente.md` | Protocolo de cómo opera el agente (entrada) |
| `memoria.md` | ¿Qué se decidió y por qué? ¿Qué falta confirmar? |
| `datos.md` | ¿Cómo se leen, limpian, exploran y validan los datos? |
| `modelo.md` | ¿Cómo se entrena, valida y sirve el modelo? (se crea en Fase 2) |
| `learn.md` | ¿Qué errores se detectaron y qué regla dejaron? |
| `manager.md` (este) | ¿En qué orden, y cuándo está "listo" cada paso? |

Regla de oro: si una decisión cambia, se actualiza `memoria.md` primero, y luego
se ajustan los docs de dominio / el código. No dupliques decisiones —
referencia a `memoria.md`. Si el cambio es porque se detectó un error,
regístralo en `learn.md` antes de corregirlo en silencio.

## Contexto activo (lo primero que se lee al arrancar; mantener corto)
- **En qué estoy:** **Fase 1 en curso.** El loader reproducible ya está en
  `src/` con 18 tests en verde; falta el EDA y el contrato de datos.
  Decisiones vigentes: target = columna T (D3); seudonimización
  obligatoria en lo versionado (D4); data real nunca se commitea (D5); **un
  modelo por cuenta contable** (D6); todas las líneas se clasifican, incluidas
  reclasificaciones/negativos/anulaciones (D7); hoja CUENTA_05 con target en col
  AA y sus filas sin valor fuera (D8); solo cuentan las filas con `ID` (D9); el
  alcance de CUENTA_05 lo define el programa, no la imputación (D10).
- **Cambió en la última sesión:** Se integró el `D4` de seudonimización que
  estaba en GitHub con el cierre local de Fase 0 → las decisiones locales se
  renumeraron a **D5–D8**. Se creó `mapeo_sensibles.json` (local, gitignored)
  como versión máquina del glosario, y se construyó el loader (`src/config.py`,
  `src/loader.py`, `src/build_dataset.py`). Sigue abierta solo P4.
- **Próximos pasos:**
  1. EDA por cuenta sobre `data/processed/*.parquet` (dataset ya estable:
     3.521 filas homogéneas + 648 de CUENTA_05).
  2. Auditar leakage y cerrar el contrato de datos en `memoria.md §4`.

## Mapa de extractos por fase (qué leer/tocar sin abrir todo)
Convención de anclas: `memoria.md` → `§n` y `Dn`; docs de dominio → `## n`;
`learn.md` → `Ln`; código → `# §n`.
Regla: "leer" = contrato (no editar); "tocar" = dónde va el cambio. Si un ancla
no existe donde dice esta tabla, es un error de la tabla → corregirla aquí.

### Fase 0 — Harness + reconocimiento de datos
| Tarea | Leer (contrato/decisión) | Tocar |
|---|---|---|
| Montar harness | `agente.md` completo | `*.md` raíz |
| Reconocer Excel | `datos.md ##1` + `memoria.md §2` | `data/raw/` (local, gitignored) |

### Fase 1 — EDA + contrato de datos
| Tarea | Leer (contrato/decisión) | Tocar |
|---|---|---|
| Cargar/consolidar | `datos.md ##1` + `##2` + `memoria.md D6..D8` | `src/` |
| EDA / correlaciones | `datos.md ##2` + `##3` | `notebooks/` o `src/eda.py` |
| Detectar leakage | `datos.md ##4` | `memoria.md §4` (contrato de datos) |

## Fases del proyecto
### Fase 0 — Harness + reconocimiento de datos ✅
Dueño: `agente.md` + `datos.md`.
- [x] Instalar los 4 documentos núcleo + entrada `CLAUDE.md`/`AGENTS.md`.
- [x] Reconocimiento inicial de la estructura del Excel.
- [x] Resolver las preguntas fundacionales con el usuario (`memoria.md §5`):
      P1→D3, P2→D5, P3→D6, P5→D7, P6→D8. **P4 (loop humano-en-el-medio) se
      pospone a la Fase 4 por decisión de orden**, no bloquea nada antes.
Criterio de salida: harness instalado y preguntas fundacionales promovidas a
decisiones `Dn`. ✅ cumplido.

### Fase 1 — EDA + contrato de datos ⬅ ACTIVA
Dueño: `datos.md`.
- [x] Consolidar las hojas de detalle en un dataset limpio y tipado
      (`src/loader.py` + `src/build_dataset.py`, 18 tests con fixtures
      sintéticos; artefactos en `data/processed/`, gitignored).
- [ ] EDA: distribución de clases (desbalance ya visible), cardinalidad de
      features, valores nulos, duplicados, montos negativos/reclasificaciones.
- [ ] Análisis de asociación/correlación entre features y target (evitando
      confundir correlación con leakage).
- [ ] Identificar y aislar columnas con *data leakage* (p.ej. campos que solo
      existen porque ya se clasificó).
Criterio de salida: dataset reproducible + contrato de datos en `memoria.md §4`
+ lista de features candidatas y features prohibidas, todo validado por el
usuario.

### Fase 2 — Baseline + feature engineering
Dueño: `modelo.md` (se crea aquí).
- [ ] Modelo baseline honesto (p.ej. reglas simples / mayoría por cuenta) como
      piso de comparación.
- [ ] Feature engineering sobre texto (Descripción, Proveedor) y categóricas.
- [ ] Primer modelo entrenable con validación robusta.
Criterio de salida: baseline + primer modelo con métricas registradas y
esquema de validación aprobado (anti-overfitting).

### Fase 3 — Validación robusta y control de overfitting
Dueño: `modelo.md`.
- [ ] Validación cruzada apropiada al dominio (¿temporal? ¿por grupo?).
- [ ] Curvas de aprendizaje, análisis de sobreajuste, calibración de confianza.
Criterio de salida: métricas estables train/valid/test sin brecha de
sobreajuste inaceptable, aprobadas por el usuario.

### Fase 4 — Loop humano-en-el-medio (consulta hasta estar entrenado)
Dueño: `modelo.md`.
- [ ] Mecanismo por el que el modelo marca líneas de baja confianza y las
      consulta al humano; las correcciones re-entrenan.
Criterio de salida: loop funcional donde el humano solo revisa lo dudoso y el
modelo mejora con cada tanda.

### Fase 5 — Empaquetado sostenible y escalable
Dueño: `modelo.md`.
- [ ] Pipeline reproducible de punta a punta (datos→features→modelo→inferencia).
- [ ] Documentación de uso para el controller.
Criterio de salida: alguien puede correr la clasificación sobre datos nuevos
sin ayuda del agente.

## Estado actual (actualizar en cada sesión)
| Fase | Estado |
|---|---|
| 0 — Harness + reconocimiento | ✅ completada (D1–D8) |
| — dataset base (D9, D10) | ✅ loader + artefactos reproducibles |
| 1 — EDA + contrato de datos | 🟡 en curso |
| 2 — Baseline + feature eng. | ⬜ no iniciada |
| 3 — Validación robusta | ⬜ no iniciada |
| 4 — Loop humano-en-el-medio | ⬜ no iniciada |
| 5 — Empaquetado | ⬜ no iniciada |
Convención: ⬜ no iniciada · 🟡 en curso · ✅ completada · 🔴 bloqueada (por qué).

## Cómo retomar en una sesión nueva
1. Leer `agente.md`, luego este archivo («Contexto activo» primero).
2. Leer `memoria.md §5` para ver preguntas abiertas.
3. Seguir el doc de dominio de la fase activa (`datos.md` en Fase 1).
4. Al cerrar una decisión o fase: actualizar `memoria.md` primero, luego el
   estado aquí.
