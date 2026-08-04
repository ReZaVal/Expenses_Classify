# learn.md — Bitácora de errores y aprendizaje de Expenses_Classify

Registro de errores detectados (de diseño, código, flujo, o del propio agente
que dirige el proyecto) y de la regla que queda una vez resueltos. Es el
mecanismo por el que el harness "aprende": un error que ya pasó no debería
volver a pasar porque quedó una regla escrita. No reemplaza a `memoria.md` (que
registra decisiones): esto registra errores.

## Protocolo
1. Al detectar un error: entrada nueva en §2 con estado `🔴 Abierto` (no hace
   falta tener la solución).
2. Al resolverlo: completar causa raíz + solución + regla derivada, cambiar a
   `✅ Resuelto`, y propagar la regla al documento que corresponda (`agente.md`
   si es sobre cómo opera el agente, doc de dominio si es convención técnica,
   `memoria.md` si cambia una decisión). Anotar dónde quedó la regla.
3. Antes de repetir un análisis o diseño, revisar el índice de §1.
4. Un error que se repite dos veces a pesar de tener regla escrita → la regla
   está mal ubicada o redactada; arreglar la regla, no solo el síntoma.

## 1. Índice de reglas ya incorporadas
| ID | Resumen del error | Regla derivada | Dónde vive ahora |
|----|-------------------|----------------|-------------------|
| L1 | Riesgo de escribir data sensible (cuentas, conceptos, empresa) en docs versionados | Solo seudónimos en lo versionado; valores reales solo en `glosario_sensibles.md` (gitignored) | `memoria.md D4`, `manager.md` (regla de prioridad), `agente.md §4` |
| L2 | Se seudonimizó sin crear antes el glosario: el mapa real se perdió al cerrar la sesión | El glosario se crea **antes** de aplicar el primer seudónimo, en el mismo cambio | `glosario_sensibles.md §5`, `agente.md §4` |

## 2. Log de errores
### L1 — Data sensible podría filtrarse a GitHub vía los docs del harness
- **Estado:** ✅ Resuelto (regla preventiva incorporada)
- **Detectado en:** sesión de setup, al notar que `memoria.md §2` contenía
  números de cuenta reales y nombres de concepto/programa reales.
- **Síntoma:** los docs vivos del harness (que sí se versionan) incluían
  identificadores sensibles del negocio; el usuario pidió no exponerlos en
  GitHub.
- **Causa raíz:** el harness documenta hallazgos de datos, y sin una regla
  explícita esos hallazgos arrastran valores reales al repositorio público.
- **Solución aplicada:** seudonimización en origen (ver `memoria.md D4`): solo
  seudónimos en lo versionado (`CUENTA_0X`, `CONCEPTO_0XX`, `EMPRESA_0X`,
  `IMP_0X`); el mapa real vive en `glosario_sensibles.md`, gitignored.
- **Regla derivada:** **antes de commitear cualquier `.md`, verificar que no
  contiene términos sensibles reales** (números de cuenta, nombres de
  concepto/programa, empresa, códigos internos); si aparece uno nuevo, agregarlo
  primero al glosario y usar su seudónimo. → propagada a `manager.md` (regla de
  prioridad, se lee al arrancar) y `agente.md §4`.

### L2 — Se aplicó la seudonimización antes de que existiera el glosario
- **Estado:** ✅ Resuelto (glosario reconstruido y regla incorporada)
- **Detectado en:** sesión del 2026-08-03, al integrar el trabajo de GitHub con
  el local: los docs ya usaban `CONCEPTO_001…006` pero `glosario_sensibles.md`
  no existía en el repo local.
- **Síntoma:** los seudónimos eran irreversibles. Nadie —ni el usuario, ni una
  sesión futura— podía saber a qué concepto real correspondía `CONCEPTO_003`.
- **Causa raíz:** el commit `83f9a51` aplicó los seudónimos y dejó el glosario
  "para después"; como el archivo es gitignored, no viajó con el repo y el mapa
  solo existía en el contexto de aquella sesión, que se cerró.
- **Solución aplicada:** se reconstruyó el glosario contra el Excel fuente,
  **verificando cada mapeo con los conteos ya documentados** en `memoria.md §2`
  (264/950, 19/61, 125/270, 716/2240) en vez de asignarlo por parecido de
  nombre. Se añadió `mapeo_sensibles.json` como versión máquina para el código.
- **Regla derivada:** **el glosario se crea antes de aplicar el primer
  seudónimo, en el mismo cambio.** Seudonimizar sin registrar el mapa no es
  proteger un dato: es destruirlo. Corolario: como el glosario nunca sube a
  GitHub, cada sesión debe verificar que existe **antes** de tocar nada
  sensible. → propagada a `glosario_sensibles.md §5` y `agente.md §4`.

## 3. Errores de comportamiento del agente
(Mismo formato que §2, pero para cuando el agente que dirige el proyecto asumió,
infirió o decidió mal — no un bug del producto sino del proceso.)

> (vacío)

## 4. Propuestas de mejora al harness (para evaluar con el usuario)
El usuario pidió proponer mejoras al sistema de harness cuando se detecten. Se
registran aquí como candidatas; NO se aplican al skill sin su visto bueno.

### M1 — El harness no tiene doc de dominio ni checklist específico para data science
- **Observación:** las plantillas del skill contemplan "código" y "flujos" pero
  no un flujo de trabajo de DS (EDA, control de leakage, esquema de validación
  anti-overfitting, tracking de experimentos, human-in-the-loop). Se creó
  `datos.md` (y se creará `modelo.md`) para cubrirlo.
- **Propuesta:** añadir al skill una plantilla opcional de doc de dominio para
  proyectos de datos/ML con un checklist de validación propio (reproducibilidad,
  sin leakage, métricas registradas, semilla fija, partición documentada).
- **Estado:** 🟡 propuesta, pendiente de evaluar con el usuario.
