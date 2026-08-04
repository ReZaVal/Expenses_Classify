"""Carga reproducible del Excel fuente (Fase 1).

Reglas que implementa, todas con decision detras:
- D6: se consolidan las 4 hojas homogeneas para explorar, pero la cuenta queda
  como columna porque el entrenamiento es por cuenta.
- D7: NO se descartan filas por ser contablemente atipicas (negativos,
  reclasificaciones, anulaciones). La unica exclusion permitida es "sin target".
- D8: CUENTA_05 va por su cuenta, sin las filas sin target.
- D9: en las hojas homogeneas, una fila es gasto si tiene ID. Lo que viene
  despues de la ultima fila con ID es cola (totales, tablas de cuadre).
- D10: el alcance de CUENTA_05 lo define el PROGRAMA (CONCEPTO_007), no el
  codigo de imputacion: hay filas con el mismo codigo y otro programa.
- D4: aqui no aparece ningun nombre real; todo pasa por config.Config.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from src import config


@dataclass
class InformeCarga:
    """Lo que la carga dejo fuera o modifico. Nada debe ser silencioso."""
    filas_por_cuenta: dict[str, int] = field(default_factory=dict)
    etiquetas_colapsadas: dict[str, list[str]] = field(default_factory=dict)
    filas_sin_target: int = 0
    filas_fuera_de_alcance: int = 0
    filas_de_cola: dict[str, int] = field(default_factory=dict)


def _normalizar_target(serie: pd.Series) -> tuple[pd.Series, dict]:
    """Quita espacios sobrantes del target y reporta que etiquetas colapsan.

    Colapsar 'Otros costos ' con 'Otros costos' es deseable, pero tiene que
    quedar auditable: si dos etiquetas distintas se funden, hay que verlo.
    """
    original = serie.dropna().astype(str)
    limpia = serie.astype(str).str.strip().where(serie.notna())
    colapsos = {}
    for valor_limpio, grupo in original.groupby(original.str.strip()):
        variantes = sorted(grupo.unique())
        if len(variantes) > 1:
            colapsos[valor_limpio] = variantes
    return limpia, colapsos


def _tipar(df: pd.DataFrame) -> pd.DataFrame:
    """Tipado explicito (datos.md ##2). Devuelve una copia, no muta."""
    out = df.copy()
    for col in config.COLS_MONTO:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    for col in config.COLS_FECHA:
        if col in out.columns:
            # dayfirst: el Excel viene en formato dd/mm/aaaa
            out[col] = pd.to_datetime(out[col], errors="coerce", dayfirst=True)
    for col in config.COLS_ID_TEXTO:
        if col in out.columns:
            out[col] = out[col].astype("string")
    # El crudo mezcla texto, numeros y vacios en la misma columna (datos.md ##3).
    # Se homogeneiza a texto: sin esto el tipo queda ambiguo y falla al serializar.
    for col in out.columns[out.dtypes == object]:
        out[col] = out[col].astype("string")
    return out


def _cortar_cola(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Corta la cola de hoja: todo lo que no tiene ID (D9).

    En las 4 hojas homogeneas las filas sin ID estan SIEMPRE despues de la
    ultima fila con ID: son la celda de total al pie, filas en blanco y (en una
    hoja) un bloque de cuadre por centro de costo. No son registros de gasto.
    Ojo: no sirve filtrar por "sin target", porque una de esas filas de cuadre
    tiene un numero suelto justo en la columna del target.
    """
    con_id = df[config.COL_ID].notna()
    return df.loc[con_id].copy(), int((~con_id).sum())


def cargar_hojas_homogeneas(cfg: config.Config | None = None,
                            con_informe: bool = False):
    """Consolida las 4 hojas de esquema homogeneo en un DataFrame tipado."""
    cfg = cfg or config.Config()
    ruta = cfg.verificar_excel()
    informe = InformeCarga()
    piezas = []

    for alias in config.CUENTAS_HOMOGENEAS:
        hoja = cfg.hoja_de(alias)
        df = pd.read_excel(ruta, sheet_name=hoja, header=0)
        df = df.rename(columns={
            df.columns[config.IDX_TARGET_HOMOGENEA]: config.COL_TARGET})
        df[config.COL_TARGET], colapsos = _normalizar_target(
            df[config.COL_TARGET])
        df.insert(0, config.COL_CUENTA, alias)
        df = _tipar(df)

        df, n_cola = _cortar_cola(df)
        informe.filas_por_cuenta[alias] = len(df)
        informe.filas_de_cola[alias] = n_cola
        for etiqueta, variantes in colapsos.items():
            informe.etiquetas_colapsadas.setdefault(etiqueta, []).extend(variantes)
        piezas.append(df)

    consolidado = pd.concat(piezas, ignore_index=True)
    consolidado = consolidado.loc[
        :, [c for c in consolidado.columns if not str(c).startswith("Unnamed")]]
    return (consolidado, informe) if con_informe else consolidado


def cargar_cuenta_05(cfg: config.Config | None = None,
                     con_informe: bool = False):
    """Carga la hoja de esquema distinto: alcance por programa (D10), sin filas sin target (D8)."""
    cfg = cfg or config.Config()
    ruta = cfg.verificar_excel()
    informe = InformeCarga()

    hoja = cfg.hoja_de(config.CUENTA_ESQUEMA_DISTINTO)
    df = pd.read_excel(ruta, sheet_name=hoja, header=0)
    df = df.rename(columns={
        df.columns[config.IDX_TARGET_CUENTA_05]: config.COL_TARGET})
    df[config.COL_TARGET], colapsos = _normalizar_target(df[config.COL_TARGET])
    informe.etiquetas_colapsadas = {k: sorted(v) for k, v in colapsos.items()}

    programa = cfg.concepto_de(config.PROGRAMA_EN_ALCANCE)
    en_alcance = df[config.COL_PROGRAMA].astype(str).str.strip() == programa
    informe.filas_fuera_de_alcance = int((~en_alcance).sum())
    df = df.loc[en_alcance]

    con_target = df[config.COL_TARGET].notna()
    informe.filas_sin_target = int((~con_target).sum())
    df = df.loc[con_target].copy()

    df.insert(0, config.COL_CUENTA, config.CUENTA_ESQUEMA_DISTINTO)
    df = _tipar(df)
    informe.filas_por_cuenta[config.CUENTA_ESQUEMA_DISTINTO] = len(df)
    df = df.loc[:, [c for c in df.columns if not str(c).startswith("Unnamed")]]
    return (df.reset_index(drop=True), informe) if con_informe else df.reset_index(drop=True)
