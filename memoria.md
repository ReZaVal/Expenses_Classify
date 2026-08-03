# memoria.md — Decisiones y contexto de Expenses_Classify

Fuente de verdad de las decisiones de diseño. Nunca re-proponer desde cero algo
que ya está aquí sin que el usuario pida revisarlo.

## 1. Contexto del proyecto
**Objetivo:** construir un modelo de data science que clasifique gastos (líneas
de ejecución presupuestal de TGP) **como lo haría un controller humano**, para
apoyar la toma de decisiones. El modelo debe **consultar al humano** las
clasificaciones dudosas hasta estar entrenado (human-in-the-loop), y construirse
con las mejores prácticas: buscar correlaciones reales, **evitar overfitting**,
y ser **sostenible y escalable**.

**Restricciones duras (del usuario):**
- No asumir nada de negocio ni de modelado: todo se consulta (ver `agente.md §3`).
- Aplicar el sistema de harness durante todo el proyecto.
- Proponer mejoras al harness cuando se detecten (no aplicarlas sin evaluar).

**Fuente de datos:** un Excel de "Clasificación de cuentas GS 2026"
(`data/raw/Clasificacion_de_cuentas_GS_2026.xlsx`, mantenido local y gitignored
por defecto — ver §5 P2).

## 2. Análisis / hallazgos del reconocimiento inicial (Fase 0)
El Excel tiene **11 hojas**: hojas de **detalle** por cuenta contable y hojas
**Resumen** asociadas.

**Hojas de detalle (candidatas a dataset de entrenamiento):**
| Hoja | Cuenta | Filas de datos aprox. | Clases en `Concepto` |
|---|---|---|---|
| `65910001 - Relacionamiento` | 65910001 | ~950 | 6 |
| `65910002 - Inv. Social` | 65910002 | ~61 | 7 |
| `65910003 - Gest. Riesgos` | 65910003 | ~270 | 8 |
| `65910004 - Gest. Rec. Ind.` | 65910004 | ~2240 | 7 |
| `63800010_Ser. Imagen Satelital` | 63800010 | ~1090 | estructura DISTINTA |

**Columnas de las 4 primeras hojas de detalle (encabezado en fila 1):**
`ID, Cuenta, Sociedad, División, Periodo, (mes num), Proveedor, Descripción,
Num OT, Referencia, Doc. Compra, Nro. Documento, Fecha Documento, Anulación,
Orden, Centro de Costo, NSO, US$, Concepto, (col vacía), Id_Concepto,
Descripción_Concepto`.

**TARGET (confirmado por el usuario, ver D3):** la variable a predecir es la
**columna T** (letra Excel T = índice 20), sin encabezado en el Excel. Es la
clasificación **granular** que asigna el controller (ej. `Plan de
Relacionamiento - Sierra`, `NUEVA PROV CHIQUI`). La **columna S** (`Concepto`,
índice 19) **NO es el target**: viene de SAP, la ingresan los usuarios, y es un
**feature** legítimo (existe antes de la clasificación del controller).

**Distribución del target (columna T) por hoja de detalle:**
| Hoja | Clases en T | Clase mayoritaria (aprox) |
|---|---|---|
| 65910001 | 21 | `Plan de Relacionamiento - Sierra` (264/950) |
| 65910002 | 10 | `Becas Chiquintirca - Prov` (19/61) |
| 65910003 | 14 | `Logistica espacios de diálogo` (125/270) |
| 65910004 | 20 | `NUEVA PROV CHIQUI` (716/2240) |

**Observaciones clave (hipótesis, a validar en Fase 1 — NO son decisiones):**
- La columna S (`Concepto`, de SAP) es probablemente un **predictor fuerte** de
  T (T suele refinar S con región/detalle: Sierra/Selva/Costa). No es leakage.
- **Desbalance de clases** presente en T (colas largas de clases con 1-4
  ejemplos) → métricas robustas al desbalance (F1 macro, matriz de confusión),
  no accuracy sola. Ojo con clases de 1-2 ejemplos: puede no haber suficiente
  para aprenderlas/validarlas.
- Cada cuenta tiene un **espacio de etiquetas propio** (T distinto por cuenta) →
  afecta el alcance del modelo (§5 P3).
- El target T tiene **problemas de higiene**: espacios finales (`'Otros costos '`),
  mayúsculas/minúsculas inconsistentes, nombres heterogéneos (programas vs.
  refinamientos geográficos) → normalizar antes de entrenar.
- Aparecen filas de **"Reclasificación"** también en el target T, además de
  montos **negativos** y anulaciones → decidir cómo tratarlas (`§5 P5`).
- Las columnas `Id_Concepto` / `Descripción_Concepto` (W/X) en la hoja 1 parecen
  una **lista de referencia** pegada al costado, NO alineada fila-a-fila. **A
  verificar** antes de usarlas (riesgo de leakage/confusión).
- La hoja `63800010` tiene un **esquema totalmente distinto** (columnas tipo
  export SAP: Asiento contable, Cuenta de mayor, Clave contab., etc.) → puede
  requerir tratamiento aparte o quedar fuera del primer alcance.
- Riesgo de **data leakage**: columnas como `Descripción_Concepto`, `NSO`,
  `Orden` o el propio texto de `Descripción` pueden contener la respuesta ya
  clasificada. Se auditará en Fase 1 (`datos.md ##4`).

## 3. Decisiones tomadas
### D1 — Se instala el harness de documentación multi-sesión
- **Decisión:** el proyecto se dirige con el harness (agente/manager/memoria/
  learn + docs de dominio), con entrada `CLAUDE.md`/`AGENTS.md` → `agente.md`.
- **Razón:** proyecto largo, multi-sesión, con decisiones de diseño que no se
  pueden re-litigar y data sensible; encaja con el criterio de instalación del
  skill.
- **Alternativas rechazadas:** un simple `README` (insuficiente para continuidad
  multi-sesión); notebook único sin documentación de decisiones (se pierde el
  porqué entre sesiones).
- **Impacto:** todos los `*.md` de la raíz; flujo de trabajo de todas las fases.

### D2 — Idioma del proyecto: español
- **Decisión:** todo el harness y la comunicación en español.
- **Razón:** es el idioma del usuario y del dominio (contabilidad TGP).
- **Alternativas rechazadas:** inglés (fricción innecesaria para quien mantiene).
- **Impacto:** todos los documentos y comentarios de código de cara al usuario.

### D3 — Variable objetivo: columna T (clasificación granular del controller)
- **Decisión:** el modelo predice el valor de la **columna T** (letra Excel T,
  índice 20, sin encabezado en el archivo) de las hojas de detalle. Es la
  clasificación granular que hoy asigna manualmente el controller.
- **Razón:** el usuario lo confirmó explícitamente. La columna S (`Concepto`)
  viene de SAP ingresada por usuarios → es un **input/feature**, no el target.
- **Alternativas rechazadas:** usar `Concepto` (col S) como target — descartado,
  es dato de entrada de SAP, no la decisión del controller. Usar
  `Descripción_Concepto`/`Id_Concepto` (W/X) — descartado como target.
- **Impacto:** define target y features en `memoria.md §4`, todo `datos.md` y el
  modelado. Nombre canónico a asignar a la columna T (no tiene header) →
  propuesta: `clasificacion_controller` (a confirmar al armar el contrato §4).

## 4. Contrato de datos / estructura (se llena en Fase 1)
> Pendiente hasta cerrar §5 P1 (target) y hacer el EDA. Aquí vivirán: columnas
> oficiales, tipos, qué es feature, qué es target, y qué columnas están
> **prohibidas** por *data leakage*. NO se puede cambiar sin decisión.

## 5. Preguntas abiertas (pendientes de resolver con el usuario)
- [x] **P1 — Variable objetivo.** ✅ RESUELTA → **D3**: el target es la columna
      T (clasificación granular del controller). La columna S (`Concepto`) es un
      feature que viene de SAP.
- [ ] **P2 — Sensibilidad de datos.** El Excel tiene data financiera real de
      TGP. ¿Se versiona en git (repo privado), se mantiene fuera (`.gitignore`,
      default actual), o solo una versión anonimizada? — **Bloquea** decidir qué
      se commitea.
- [ ] **P3 — Alcance del modelo.** ¿Un modelo por cuenta contable (espacios de
      etiquetas separados) o un modelo global multi-cuenta con la cuenta como
      feature? ¿O se decide tras el EDA? — **Bloquea** la arquitectura de
      modelado y la partición de datos.
- [ ] **P4 — Diseño del loop humano-en-el-medio.** ¿Aprendizaje activo (el
      modelo pregunta solo lo de baja confianza y re-entrena), validación por
      lotes, o se diseña más adelante con una propuesta del agente? — **Bloquea**
      la Fase 4.
- [ ] **P5 — Tratamiento de filas especiales.** ¿"Reclasificación",
      "Liquidación de orden", montos negativos y anulaciones son ejemplos de
      entrenamiento válidos, ruido a excluir, o una tarea aparte? — **Bloquea**
      la construcción del dataset limpio en Fase 1.
- [ ] **P6 — Hoja 63800010 (esquema distinto).** ¿Entra en el alcance inicial o
      se trata por separado / se posterga? — Afecta el alcance de Fase 1.
