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
| — | (sin errores registrados aún) | — | — |

## 2. Log de errores
> (vacío — se agrega la primera entrada cuando aparezca un error de datos,
> código o diseño)

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
