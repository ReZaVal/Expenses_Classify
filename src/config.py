"""Configuracion y traduccion seudonimo -> valor real.

Contrato de seguridad (memoria.md D4): este archivo SE VERSIONA, asi que aqui
solo pueden aparecer **seudonimos**. Los valores reales (nombres de hoja,
numeros de cuenta, codigos de imputacion) viven unicamente en
`mapeo_sensibles.json`, que esta gitignoreado. Si alguien hardcodea un valor
real en `src/`, rompe D4.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA_EXCEL = RAIZ / "data" / "raw" / "Clasificacion_de_cuentas_GS_2026.xlsx"
RUTA_MAPEO = RAIZ / "mapeo_sensibles.json"
DIR_PROCESADO = RAIZ / "data" / "processed"

# Cuentas de esquema homogeneo (datos.md ##2). CUENTA_05 va aparte por D8.
CUENTAS_HOMOGENEAS = ("CUENTA_01", "CUENTA_02", "CUENTA_03", "CUENTA_04")
CUENTA_ESQUEMA_DISTINTO = "CUENTA_05"
# El alcance de CUENTA_05 lo define el PROGRAMA de financiacion, no el codigo
# de imputacion: son poblaciones distintas (memoria.md D10).
PROGRAMA_EN_ALCANCE = "CONCEPTO_007"
COL_PROGRAMA = "Progr.financiación"
COL_ID = "ID"

# Posicion del target. En las homogeneas es la col. Excel T (0-based 19) y no
# tiene encabezado; en CUENTA_05 es la col. AA (0-based 26). Ver memoria.md D3/D8.
IDX_TARGET_HOMOGENEA = 19
IDX_TARGET_CUENTA_05 = 26

# Nombre canonico del target (memoria.md D3; pendiente de confirmar en §4).
COL_TARGET = "clasificacion_controller"
COL_CUENTA = "cuenta"

COLS_FECHA = ("Fecha Documento",)
COLS_MONTO = ("US$", "NSO")
COLS_ID_TEXTO = ("ID", "Num OT", "Referencia", "Doc. Compra", "Nro. Documento",
                 "Orden", "Centro de Costo")


class FaltaMapeoError(FileNotFoundError):
    """No existe mapeo_sensibles.json: sin el no se pueden ubicar las hojas."""


@dataclass
class Config:
    ruta_excel: Path = RUTA_EXCEL
    ruta_mapeo: Path = RUTA_MAPEO
    _mapeo: dict | None = field(default=None, repr=False)

    @property
    def mapeo(self) -> dict:
        if self._mapeo is None:
            if not Path(self.ruta_mapeo).exists():
                raise FaltaMapeoError(
                    f"Falta mapeo_sensibles.json (buscado en: {self.ruta_mapeo}). "
                    "Es el mapa seudonimo -> valor real (gitignored). "
                    "Reconstruyelo desde "
                    "glosario_sensibles.md; sin el no se sabe que hoja del "
                    "Excel corresponde a cada CUENTA_0X."
                )
            self._mapeo = json.loads(Path(self.ruta_mapeo).read_text("utf-8"))
        return self._mapeo

    def hoja_de(self, alias: str) -> str:
        """Nombre real de la hoja para un seudonimo de cuenta."""
        cuentas = self.mapeo["cuentas"]
        if alias not in cuentas:
            raise KeyError(f"{alias} no esta en mapeo_sensibles.json")
        return cuentas[alias]["hoja"]

    def imputacion_de(self, alias: str) -> str:
        """Codigo real de imputacion para un seudonimo."""
        return self._traducir("imputaciones", alias)

    def concepto_de(self, alias: str) -> str:
        """Valor real de un concepto/programa para un seudonimo."""
        return self._traducir("conceptos", alias)

    def _traducir(self, familia: str, alias: str) -> str:
        valores = self.mapeo.get(familia, {})
        if alias not in valores:
            raise KeyError(f"{alias} no esta en mapeo_sensibles.json ({familia})")
        return valores[alias]

    def verificar_excel(self) -> Path:
        ruta = Path(self.ruta_excel)
        if not ruta.exists():
            raise FileNotFoundError(
                f"No se encuentra el Excel fuente en {ruta}. Copialo a "
                "data/raw/ (esa carpeta esta gitignoreada, datos.md ##1)."
            )
        return ruta
