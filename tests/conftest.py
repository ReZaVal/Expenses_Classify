"""Fixtures sinteticos: los tests NUNCA tocan el Excel real ni el mapeo local.

Todo lo que se ve aqui son datos inventados con la MISMA FORMA que el crudo
(24 columnas, target sin encabezado en el indice 19, etc.). Asi los tests
corren en un clon fresco sin data sensible.
"""
import json

import pandas as pd
import pytest

# Nombres de hoja falsos, con la misma forma "<cuenta> - <programa>".
HOJAS_FALSAS = {
    "CUENTA_01": {"cuenta": "10000001", "hoja": "10000001 - Alfa"},
    "CUENTA_02": {"cuenta": "10000002", "hoja": "10000002 - Beta"},
    "CUENTA_03": {"cuenta": "10000003", "hoja": "10000003 - Gamma"},
    "CUENTA_04": {"cuenta": "10000004", "hoja": "10000004 - Delta"},
    "CUENTA_05": {"cuenta": "20000005", "hoja": "20000005_Epsilon"},
}
IMP_FALSA = "XXXX-0000"

COLS_DETALLE = [
    "ID", "Cuenta", "Sociedad", "División", "Periodo", "mes num", "Proveedor",
    "Descripción", "Num OT", "Referencia", "Doc. Compra", "Nro. Documento",
    "Fecha Documento", "Anulación", "Orden", "Centro de Costo", "NSO", "US$",
    "Concepto", "Unnamed: 19", "extra_1", "Id_Concepto",
    "Descripción_Concepto", "extra_2",
]


def _hoja_detalle(n_filas: int, etiquetas: list[str]) -> pd.DataFrame:
    """DataFrame con la forma de una hoja homogenea (target en indice 19)."""
    filas = []
    for i in range(n_filas):
        fila = [None] * len(COLS_DETALLE)
        fila[0] = f"ID{i:04d}"
        fila[4] = "2026-01"
        fila[6] = f"Proveedor {i % 5}"
        fila[7] = f"descripcion libre {i}"
        fila[12] = "2026-01-15"
        fila[16] = 100.0 + i
        fila[17] = -50.0 if i % 10 == 0 else 25.0 + i  # montos negativos: D7
        fila[18] = f"ConceptoSAP{i % 3}"
        fila[19] = etiquetas[i % len(etiquetas)]
        filas.append(fila)
    return pd.DataFrame(filas, columns=COLS_DETALLE)


def _hoja_cuenta_05(n_con_target: int, n_sin_target: int,
                    n_otra_imputacion: int) -> pd.DataFrame:
    """Hoja de esquema distinto: 27 columnas, target en indice 26 (col AA)."""
    cols = [f"col_{i}" for i in range(27)]
    cols[3] = "Imputación"
    cols[26] = "Unnamed: 26"
    filas = []
    for i in range(n_con_target):
        f = [None] * 27
        f[0], f[3], f[26] = f"A{i}", IMP_FALSA, f"Etiqueta_{i % 3}"
        filas.append(f)
    for i in range(n_sin_target):
        f = [None] * 27
        f[0], f[3], f[26] = f"B{i}", IMP_FALSA, None
        filas.append(f)
    for i in range(n_otra_imputacion):
        f = [None] * 27
        f[0], f[3], f[26] = f"C{i}", "OTRA-9999", f"Etiqueta_fuera_{i}"
        filas.append(f)
    return pd.DataFrame(filas, columns=cols)


@pytest.fixture
def mapeo_falso(tmp_path):
    """mapeo_sensibles.json sintetico."""
    ruta = tmp_path / "mapeo_sensibles.json"
    ruta.write_text(json.dumps({
        "empresa": {"EMPRESA_01": "ACME"},
        "cuentas": HOJAS_FALSAS,
        "imputaciones": {"IMP_01": IMP_FALSA},
    }), encoding="utf-8")
    return ruta


@pytest.fixture
def excel_falso(tmp_path):
    """Excel con la misma estructura que el crudo, con datos inventados."""
    ruta = tmp_path / "excel_falso.xlsx"
    etiquetas = {
        "CUENTA_01": ["Alfa - Norte", "Alfa - Sur", "Alfa - Este"],
        "CUENTA_02": ["Beta uno", "Beta dos"],
        "CUENTA_03": ["Gamma uno", "Reclasificación - Gamma"],
        # 'Otros costos ' con espacio final: caso de higiene documentado
        "CUENTA_04": ["Delta uno", "Otros costos ", "Otros costos"],
    }
    filas = {"CUENTA_01": 30, "CUENTA_02": 12, "CUENTA_03": 20, "CUENTA_04": 40}
    with pd.ExcelWriter(ruta, engine="openpyxl") as w:
        for alias, n in filas.items():
            _hoja_detalle(n, etiquetas[alias]).to_excel(
                w, sheet_name=HOJAS_FALSAS[alias]["hoja"], index=False)
        _hoja_cuenta_05(9, 4, 5).to_excel(
            w, sheet_name=HOJAS_FALSAS["CUENTA_05"]["hoja"], index=False)
        # Ruido que debe ignorarse (datos.md ##1)
        pd.DataFrame({"x": [1, 2]}).to_excel(w, sheet_name="Resumen 10000001",
                                             index=False)
        pd.DataFrame({"y": [1]}).to_excel(w, sheet_name="Sheet1", index=False)
    return ruta
