# memoria.md — Decisiones y contexto de Expenses_Classify

Fuente de verdad de las decisiones de diseño. Nunca re-proponer desde cero algo
que ya está aquí sin que el usuario pida revisarlo.

## 1. Contexto del proyecto
**Objetivo:** construir un modelo de data science que clasifique gastos (líneas
de ejecución presupuestal de EMPRESA_01) **como lo haría un controller humano**, para
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
| `CUENTA_01` | CUENTA_01 | ~950 | 6 |
| `CUENTA_02` | CUENTA_02 | ~61 | 7 |
| `CUENTA_03` | CUENTA_03 | ~270 | 8 |
| `CUENTA_04` | CUENTA_04 | ~2240 | 7 |
| `CUENTA_05` | CUENTA_05 | ~1090 | estructura DISTINTA |

**Columnas de las 4 primeras hojas de detalle (encabezado en fila 1):**
`ID, Cuenta, Sociedad, División, Periodo, (mes num), Proveedor, Descripción,
Num OT, Referencia, Doc. Compra, Nro. Documento, Fecha Documento, Anulación,
Orden, Centro de Costo, NSO, US$, Concepto, (col vacía), Id_Concepto,
Descripción_Concepto`.

**TARGET (confirmado por el usuario, ver D3):** la variable a predecir es la
**columna T** (letra Excel T = índice 20), sin encabezado en el Excel. Es la
clasificación **granular** que asigna el controller (ej. `CONCEPTO_001`,
`CONCEPTO_004`). La **columna S** (`Concepto`,
índice 19) **NO es el target**: viene de SAP, la ingresan los usuarios, y es un
**feature** legítimo (existe antes de la clasificación del controller).

**Distribución del target (columna T) por hoja de detalle:**
| Hoja | Clases en T | Clase mayoritaria (aprox) |
|---|---|---|
| CUENTA_01 | 21 | `CONCEPTO_001` (264/950) |
| CUENTA_02 | 10 | `CONCEPTO_002` (19/61) |
| CUENTA_03 | 14 | `CONCEPTO_003` (125/270) |
| CUENTA_04 | 20 | `CONCEPTO_004` (716/2240) |

**Observaciones clave (hipótesis, a validar en Fase 1 — NO son decisiones):**
- La columna S (`Concepto`, de SAP) es probablemente un **predictor fuerte** de
  T (T suele refinar S con región/detalle: Sierra/Selva/Costa). No es leakage.
- **Desbalance de clases** presente en T (colas largas de clases con 1-4
  ejemplos) → métricas robustas al desbalance (F1 macro, matriz de confusión),
  no accuracy sola. Ojo con clases de 1-2 ejemplos: puede no haber suficiente
  para aprenderlas/validarlas.
- Cada cuenta tiene un **espacio de etiquetas propio** (T distinto por cuenta) →
  afecta el alcance del modelo (§5 P3).
- El target T tiene **problemas de higiene**: espacios finales (`'CONCEPTO_006 '`),
  mayúsculas/minúsculas inconsistentes, nombres heterogéneos (programas vs.
  refinamientos geográficos) → normalizar antes de entrenar.
- Aparecen filas de **"Reclasificación"** también en el target T, además de
  montos **negativos** y anulaciones → decidir cómo tratarlas (`§5 P5`).
- Las columnas `Id_Concepto` / `Descripción_Concepto` (W/X) en la hoja 1 parecen
  una **lista de referencia** pegada al costado, NO alineada fila-a-fila. **A
  verificar** antes de usarlas (riesgo de leakage/confusión).
- La hoja `CUENTA_05` tiene un **esquema totalmente distinto** (columnas tipo
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
- **Razón:** es el idioma del usuario y del dominio (contabilidad EMPRESA_01).
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

### D4 — Seudonimización en origen de términos sensibles en los docs
- **Decisión:** los documentos versionados (`memoria.md`, `datos.md`,
  `manager.md`, etc.) llevan **solo seudónimos** para números de cuenta y
  nombres de concepto/programa, el **nombre de la empresa** y códigos internos
  (`CUENTA_0X`, `CONCEPTO_0XX`, `EMPRESA_0X`, `IMP_0X`). El mapa real ↔ seudónimo
  vive únicamente en `glosario_sensibles.md`, **gitignoreado** (nunca sube a
  GitHub). No se usan filtros git de cifrado.
- **Razón:** proteger data sensible (cuentas, conceptos) sin romper el harness:
  los docs siguen legibles y el clon fresco de cada sesión no necesita llave
  para leerlos (solo para des-seudonimizar, si hace falta, con el glosario
  local). Alcance acordado con el usuario: cuentas, conceptos/programas, nombre
  de la empresa y códigos internos.
- **Alternativas rechazadas:** (a) cifrado letra↔dígito con filtros
  clean/smudge — rompe la lectura del harness en sesiones futuras (la llave es
  local y el entorno clona en frío) y vuelve ilegibles los diffs; (b) renombrar
  archivos local≠remoto — git no lo soporta y rompe referencias cruzadas.
- **Impacto:** `glosario_sensibles.md` (local), `.gitignore`, y todos los docs
  con términos sensibles. Regla operativa en `learn.md L1`.

### D5 — La data financiera real NUNCA se commitea
- **Decisión:** el Excel fuente y cualquier derivado con data financiera real de
  EMPRESA_01 **no se versionan en git bajo ninguna circunstancia** (ni en repo privado,
  ni anonimizados "por si acaso"). Viven solo en local: `data/raw/`,
  `data/processed/`, `models/` permanecen en `.gitignore`.
- **Razón:** el usuario lo definió como restricción dura. Es información
  financiera real de la empresa.
- **Alternativas rechazadas:** versionar en repo privado (un repo privado puede
  volverse público o compartirse por error); versión anonimizada commiteada
  (la anonimización es reversible por cruce y agrega superficie de riesgo).
- **Impacto:** `.gitignore` es parte del contrato, no una conveniencia. Todo
  artefacto que se commitea (código, docs, métricas agregadas) debe estar libre
  de filas de datos. Antes de cada commit: verificar que no haya data staged
  (`datos.md ##6.7`). Los ejemplos que se peguen en docs deben ser sintéticos o
  agregados, no filas reales.

### D6 — Alcance: un modelo por cuenta contable
- **Decisión:** se entrena **un modelo independiente por cuenta contable**
  (CUENTA_01, CUENTA_02, CUENTA_03, CUENTA_04 y CUENTA_05), no un modelo global
  multi-cuenta.
- **Razón:** cada cuenta tiene su propio espacio de etiquetas en la columna T
  (ver §2) y su propia semántica de negocio; mezclarlas obligaría al modelo a
  aprender primero a qué cuenta pertenece cada línea, cuando la cuenta ya se
  conoce en tiempo de inferencia.
- **Alternativas rechazadas:** modelo global con `Cuenta` como feature
  (comparte señal entre cuentas pero diluye espacios de etiquetas disjuntos);
  posponer la decisión al EDA (el usuario la cerró ahora).
- **Impacto:** la partición train/valid/test se hace **dentro de cada cuenta**;
  las métricas se reportan por cuenta (no promediadas a ciegas); habrá N
  artefactos de modelo en `models/`. La cuenta CUENTA_02 (~61 filas, 10 clases)
  queda con muy pocos datos → se documentará su limitación en Fase 2 en vez de
  fingir una métrica. Pendiente: si el EDA muestra que algunas cuentas comparten
  etiquetas, se podrá proponer compartir representación de texto — sería una
  decisión nueva, no un cambio silencioso.

### D7 — Todas las líneas se clasifican (no hay filas "de descarte")
- **Decisión:** las filas de "Reclasificación", "Liquidación de orden", montos
  negativos y anulaciones son **ejemplos de entrenamiento válidos**. Todo
  concepto debe quedar clasificado; no se excluyen filas del dataset por ser
  atípicas contablemente.
- **Razón:** el usuario lo definió: en la operación real el controller clasifica
  todas las líneas, así que el modelo debe hacer lo mismo. Excluirlas crearía un
  modelo que falla justo en los casos que el humano igual tiene que resolver.
- **Alternativas rechazadas:** filtrarlas como ruido (dejaría un hueco en
  producción); tratarlas como tarea aparte (duplica el sistema sin necesidad
  demostrada).
- **Impacto:** el dataset limpio conserva estas filas. El signo del monto
  (`US$` negativo) y la naturaleza del documento son **features**, no criterios
  de filtrado. Al medir, revisar por separado el desempeño en estas filas: si el
  modelo falla sistemáticamente ahí, es hallazgo a reportar, no motivo para
  excluirlas.

### D8 — Hoja CUENTA_05: target = columna AA; las filas sin valor quedan fuera
- **Decisión:** la hoja `CUENTA_05` entra al alcance,
  filtrada a `Imputación = IMP_01` (757 de 1094 filas). Su target es la
  **columna final sin encabezado (col 27 / AA)**, análoga a la columna T de las
  otras hojas. Las **107 filas sin valor en AA se dejan en blanco**: no se usan
  para entrenar y el modelo **tampoco las predice** (quedan fuera del alcance de
  inferencia).
- **Razón:** el usuario lo confirmó. Las filas en blanco no representan una
  clasificación del controller, así que no son ni ejemplo de entrenamiento ni
  caso a resolver.
- **Alternativas rechazadas:** dejar la hoja fuera del proyecto; tratar las 107
  filas en blanco como una clase más o pedir que el modelo las clasifique.
- **Impacto:** esta cuenta tiene un esquema de features **completamente
  distinto** (export SAP) → su pipeline de features es propio, coherente con D6
  (un modelo por cuenta). Convive con D7 sin contradicción: D7 dice que no se
  descartan filas por ser contablemente atípicas; aquí se excluyen filas **sin
  target**, que es otra cosa. Definir en Fase 1 el criterio exacto de "sin
  valor" (nulo vs. cadena vacía vs. espacios).

## 4. Contrato de datos / estructura (se llena en Fase 1)
> Pendiente hasta cerrar §5 P1 (target) y hacer el EDA. Aquí vivirán: columnas
> oficiales, tipos, qué es feature, qué es target, y qué columnas están
> **prohibidas** por *data leakage*. NO se puede cambiar sin decisión.

## 5. Preguntas abiertas (pendientes de resolver con el usuario)
- [x] **P1 — Variable objetivo.** ✅ RESUELTA → **D3**: el target es la columna
      T (clasificación granular del controller). La columna S (`Concepto`) es un
      feature que viene de SAP.
- [x] **P2 — Sensibilidad de datos.** ✅ RESUELTA → **D5**: la data financiera
      real **nunca** se commitea; vive solo en local (`.gitignore`).
- [x] **P3 — Alcance del modelo.** ✅ RESUELTA → **D6**: un modelo independiente
      por cuenta contable.
- [ ] **P4 — Diseño del loop humano-en-el-medio.** ¿Aprendizaje activo (el
      modelo pregunta solo lo de baja confianza y re-entrena), validación por
      lotes, o se diseña más adelante con una propuesta del agente? — **Bloquea**
      la Fase 4.
- [x] **P5 — Tratamiento de filas especiales.** ✅ RESUELTA → **D7**: son
      ejemplos válidos; todos los conceptos deben clasificarse.
- [x] **P6 — Hoja CUENTA_05 (esquema distinto).** ✅ RESUELTA → **D8**: filtrar a
      `Imputación = IMP_01`, target = columna AA, y las 107 filas sin valor
      quedan fuera (no se entrenan ni se predicen).

> Única pregunta viva: **P4**. No bloquea la Fase 1.
