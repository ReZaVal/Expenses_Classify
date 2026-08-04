"""Medidas de asociacion y perfilado de columnas para el EDA (datos.md ##3).

Para categoricas se usa **Cramer's V**, no Pearson: el target y casi todas las
features son categoricas, y Pearson no significa nada entre categorias.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

# Umbrales de perfilado. Son heuristicas de EDA, no decisiones de modelado.
PCT_NULOS_CASI_VACIA = 90.0
RATIO_IDENTIFICADOR = 0.95


@dataclass(frozen=True)
class PerfilColumna:
    """Diagnostico de una columna antes de considerarla feature."""
    n_filas: int
    pct_nulos: float
    n_unicos: int

    @property
    def casi_vacia(self) -> bool:
        return self.pct_nulos >= PCT_NULOS_CASI_VACIA

    @property
    def constante(self) -> bool:
        return self.n_unicos <= 1

    @property
    def identificador_unico(self) -> bool:
        """Un valor distinto por fila: memoriza en vez de generalizar."""
        no_nulos = self.n_filas * (1 - self.pct_nulos / 100)
        return no_nulos > 0 and self.n_unicos / no_nulos >= RATIO_IDENTIFICADOR

    @property
    def inservible(self) -> bool:
        return self.casi_vacia or self.constante or self.identificador_unico


def perfil_de_columna(serie: pd.Series) -> PerfilColumna:
    return PerfilColumna(
        n_filas=len(serie),
        pct_nulos=float(serie.isna().mean() * 100) if len(serie) else 0.0,
        n_unicos=int(serie.nunique(dropna=True)),
    )


def cramers_v(a: pd.Series, b: pd.Series) -> float:
    """Asociacion entre dos categoricas, en [0, 1]. NaN si no es calculable.

    Con correccion de sesgo (Bergsma): sin ella, las columnas de alta
    cardinalidad salen artificialmente asociadas con todo, que es justo el
    error que haria confundir cardinalidad con senal.
    """
    juntas = pd.DataFrame({"a": a, "b": b}).dropna()
    if juntas.empty or juntas["a"].nunique() < 2 or juntas["b"].nunique() < 2:
        return float("nan")

    tabla = pd.crosstab(juntas["a"], juntas["b"]).to_numpy()
    n = tabla.sum()
    chi2 = _chi2(tabla)
    filas, cols = tabla.shape

    phi2 = max(0.0, chi2 / n - (cols - 1) * (filas - 1) / (n - 1))
    cols_corr = cols - (cols - 1) ** 2 / (n - 1)
    filas_corr = filas - (filas - 1) ** 2 / (n - 1)
    denominador = min(cols_corr - 1, filas_corr - 1)
    if denominador <= 0:
        return float("nan")
    return float(np.sqrt(phi2 / denominador))


def _chi2(tabla: np.ndarray) -> float:
    """Chi-cuadrado de una tabla de contingencia, sin dependencias extra."""
    n = tabla.sum()
    esperado = np.outer(tabla.sum(axis=1), tabla.sum(axis=0)) / n
    with np.errstate(divide="ignore", invalid="ignore"):
        termino = np.where(esperado > 0, (tabla - esperado) ** 2 / esperado, 0.0)
    return float(termino.sum())


def asociacion_con_target(df: pd.DataFrame, target: str,
                          excluir: tuple[str, ...] = ()) -> pd.DataFrame:
    """Cramer's V de cada columna contra el target, de mayor a menor.

    OJO: un valor alto NO significa "buena feature". Puede ser senal legitima o
    leakage; distinguirlo es criterio humano (datos.md ##4), no estadistico.
    """
    filas = []
    for col in df.columns:
        if col == target or col in excluir:
            continue
        perfil = perfil_de_columna(df[col])
        filas.append({
            "columna": col,
            "cramers_v": cramers_v(df[col].astype("object"),
                                   df[target].astype("object")),
            "pct_nulos": round(perfil.pct_nulos, 1),
            "n_unicos": perfil.n_unicos,
            "inservible": perfil.inservible,
        })
    return (pd.DataFrame(filas)
            .sort_values("cramers_v", ascending=False, na_position="last")
            .reset_index(drop=True))
