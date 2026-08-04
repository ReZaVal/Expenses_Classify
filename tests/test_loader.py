"""Tests del loader (Fase 1). Contratos que vienen de memoria.md D6/D7/D8."""
import pandas as pd
import pytest

from src import config, loader


@pytest.fixture
def cfg(mapeo_falso, excel_falso):
    return config.Config(ruta_excel=excel_falso, ruta_mapeo=mapeo_falso)


# --- config -----------------------------------------------------------------

def test_config_falla_claro_si_falta_el_mapeo(tmp_path, excel_falso):
    cfg = config.Config(ruta_excel=excel_falso,
                        ruta_mapeo=tmp_path / "no_existe.json")
    with pytest.raises(config.FaltaMapeoError, match="mapeo_sensibles.json"):
        cfg.hoja_de("CUENTA_01")


def test_config_falla_claro_si_falta_el_excel(tmp_path, mapeo_falso):
    cfg = config.Config(ruta_excel=tmp_path / "no_existe.xlsx",
                        ruta_mapeo=mapeo_falso)
    with pytest.raises(FileNotFoundError, match="data/raw"):
        loader.cargar_hojas_homogeneas(cfg)


def test_config_traduce_seudonimo_a_hoja_real(cfg):
    assert cfg.hoja_de("CUENTA_01") == "10000001 - Alfa"
    assert cfg.imputacion_de("IMP_01") == "XXXX-0000"


def test_config_no_expone_seudonimos_inexistentes(cfg):
    with pytest.raises(KeyError, match="CUENTA_99"):
        cfg.hoja_de("CUENTA_99")


# --- hojas homogeneas (D6: consolidar para explorar, entrenar por cuenta) ----

def test_consolida_las_cuatro_hojas_homogeneas(cfg):
    df = loader.cargar_hojas_homogeneas(cfg)
    assert set(df["cuenta"].unique()) == {"CUENTA_01", "CUENTA_02",
                                          "CUENTA_03", "CUENTA_04"}
    assert len(df) == 30 + 12 + 20 + 40


def test_corta_la_cola_de_hoja_y_deja_solo_filas_con_id(cfg):
    """D9: lo que va despues de la ultima fila con ID son totales, no gasto."""
    df = loader.cargar_hojas_homogeneas(cfg)
    assert df["ID"].notna().all()
    assert len(df) == 30 + 12 + 20 + 40  # sin las 2 filas de cola por hoja


def test_informa_cuantas_filas_de_cola_se_cortaron(cfg):
    _, informe = loader.cargar_hojas_homogeneas(cfg, con_informe=True)
    assert informe.filas_de_cola == {"CUENTA_01": 2, "CUENTA_02": 2,
                                     "CUENTA_03": 2, "CUENTA_04": 2}


def test_ignora_hojas_resumen_y_sheet1(cfg):
    df = loader.cargar_hojas_homogeneas(cfg)
    assert not df["cuenta"].astype(str).str.contains("Resumen|Sheet1").any()


def test_target_se_nombra_canonicamente_y_no_queda_unnamed(cfg):
    df = loader.cargar_hojas_homogeneas(cfg)
    assert config.COL_TARGET in df.columns
    assert not [c for c in df.columns if str(c).startswith("Unnamed")]


def test_cuenta_es_seudonimo_nunca_el_numero_real(cfg):
    df = loader.cargar_hojas_homogeneas(cfg)
    assert not df["cuenta"].astype(str).str.contains(r"^\d").any()


def test_conserva_filas_atipicas_negativos_y_reclasificaciones(cfg):
    """D7: no se descartan filas por ser contablemente atipicas."""
    df = loader.cargar_hojas_homogeneas(cfg)
    assert (df["US$"] < 0).any(), "se perdieron los montos negativos"
    assert df[config.COL_TARGET].str.contains("Reclasificación").any()


def test_tipado_montos_numericos_y_fechas_datetime(cfg):
    df = loader.cargar_hojas_homogeneas(cfg)
    assert pd.api.types.is_numeric_dtype(df["US$"])
    assert pd.api.types.is_numeric_dtype(df["NSO"])
    assert pd.api.types.is_datetime64_any_dtype(df["Fecha Documento"])


def test_ids_quedan_como_texto_no_numeros(cfg):
    df = loader.cargar_hojas_homogeneas(cfg)
    assert pd.api.types.is_string_dtype(df["ID"])


def test_target_se_normaliza_quitando_espacios_sobrantes(cfg):
    """'Otros costos ' y 'Otros costos' deben colapsar en uno solo."""
    df = loader.cargar_hojas_homogeneas(cfg)
    etiquetas = df[config.COL_TARGET].dropna().unique()
    assert "Otros costos" in etiquetas
    assert "Otros costos " not in etiquetas


def test_reporta_el_colapso_de_etiquetas_por_normalizacion(cfg):
    """El colapso no puede ser silencioso: hay que poder auditarlo."""
    _, informe = loader.cargar_hojas_homogeneas(cfg, con_informe=True)
    assert "Otros costos" in informe.etiquetas_colapsadas


# --- hoja de esquema distinto (D8) ------------------------------------------

def test_cuenta_05_filtra_por_programa_y_excluye_filas_sin_target(cfg):
    """D10: el alcance lo define el programa, no el codigo de imputacion."""
    df = loader.cargar_cuenta_05(cfg)
    assert len(df) == 9, "esperado: 9 con target, 4 sin target, 5 de otro programa"
    assert df[config.COL_TARGET].notna().all()


def test_cuenta_05_excluye_mismo_codigo_pero_otro_programa(cfg):
    """El caso que motivo D10: mismo codigo de imputacion, programa distinto."""
    df = loader.cargar_cuenta_05(cfg)
    assert not df[config.COL_TARGET].str.contains("fuera").any()


def test_cuenta_05_informa_cuantas_filas_deja_fuera(cfg):
    _, informe = loader.cargar_cuenta_05(cfg, con_informe=True)
    assert informe.filas_sin_target == 4
    assert informe.filas_fuera_de_alcance == 5


def test_cuenta_05_no_se_mezcla_con_las_homogeneas(cfg):
    """D6/D8: esquemas distintos, pipelines separados."""
    homogeneas = loader.cargar_hojas_homogeneas(cfg)
    assert "CUENTA_05" not in set(homogeneas["cuenta"].unique())


def test_no_quedan_columnas_de_tipo_ambiguo(cfg):
    """Sin esto el artefacto no serializa: el crudo mezcla texto y numeros."""
    df = loader.cargar_hojas_homogeneas(cfg)
    assert not [c for c in df.columns if df[c].dtype == object]


def test_el_artefacto_se_puede_serializar_y_releer(tmp_path, cfg):
    """Reproducibilidad (datos.md ##6.1): ida y vuelta sin perder filas."""
    df = loader.cargar_hojas_homogeneas(cfg)
    destino = tmp_path / "homogeneas.parquet"
    df.to_parquet(destino, index=False)
    assert len(pd.read_parquet(destino)) == len(df)
