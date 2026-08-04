"""Tests de las medidas de asociacion. Datos 100% sinteticos."""
import pandas as pd
import pytest

from src import asociacion


def test_cramers_v_es_1_cuando_una_columna_determina_la_otra():
    a = pd.Series(list("aabbcc"))
    b = pd.Series([1, 1, 2, 2, 3, 3])
    assert asociacion.cramers_v(a, b) == pytest.approx(1.0, abs=1e-6)


def test_cramers_v_es_bajo_cuando_son_independientes():
    a = pd.Series(list("abab" * 25))
    b = pd.Series(list("aabb" * 25))
    assert asociacion.cramers_v(a, b) < 0.3


def test_cramers_v_ignora_filas_con_nulos():
    a = pd.Series(["a", "b", None, "a"])
    b = pd.Series([1, 2, 3, 1])
    assert asociacion.cramers_v(a, b) == pytest.approx(1.0, abs=1e-6)


def test_cramers_v_devuelve_nan_si_no_queda_nada_que_comparar():
    a = pd.Series([None, None], dtype="object")
    b = pd.Series([1, 2])
    assert pd.isna(asociacion.cramers_v(a, b))


def test_cramers_v_devuelve_nan_si_una_columna_es_constante():
    """Una columna constante no puede asociarse con nada."""
    a = pd.Series(["x"] * 10)
    b = pd.Series(list("aabbccddee"))
    assert pd.isna(asociacion.cramers_v(a, b))


def test_perfil_de_columna_reporta_nulos_y_cardinalidad():
    df = pd.DataFrame({"c": ["a", "a", None, "b"]})
    perfil = asociacion.perfil_de_columna(df["c"])
    assert perfil.pct_nulos == pytest.approx(25.0)
    assert perfil.n_unicos == 2


def test_identifica_columna_casi_vacia_como_inservible():
    """Id_Concepto tiene 97% de nulos: no sirve como feature."""
    serie = pd.Series([None] * 97 + ["x"] * 3)
    assert asociacion.perfil_de_columna(serie).casi_vacia


def test_identifica_columna_constante():
    assert asociacion.perfil_de_columna(pd.Series(["x"] * 50)).constante


def test_identifica_columna_identificadora_unica():
    """Un ID unico por fila no generaliza: memoriza."""
    serie = pd.Series([f"id{i}" for i in range(100)])
    assert asociacion.perfil_de_columna(serie).identificador_unico
