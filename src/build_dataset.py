"""Genera los artefactos de `data/processed/` desde el crudo, y reporta.

Uso:  python -m src.build_dataset

Escribe SOLO en data/processed/ (gitignored). Nunca toca data/raw/ (datos.md ##2).
El informe que imprime es agregado y con seudonimos: no vuelca filas del crudo.
"""
from __future__ import annotations

from src import config, loader


def _reportar(nombre: str, df, informe: loader.InformeCarga) -> None:
    print(f"\n== {nombre} ==")
    print(f"  filas={len(df)}  columnas={len(df.columns)}")
    print(f"  filas por cuenta: {informe.filas_por_cuenta}")
    clases = df.groupby(config.COL_CUENTA)[config.COL_TARGET].nunique().to_dict()
    print(f"  clases distintas en el target: {clases}")
    if informe.filas_sin_target or informe.filas_otra_imputacion:
        print(f"  excluidas -> sin target: {informe.filas_sin_target} | "
              f"fuera del filtro de imputacion: {informe.filas_otra_imputacion}")
    if informe.etiquetas_colapsadas:
        print(f"  etiquetas colapsadas al normalizar: "
              f"{informe.etiquetas_colapsadas}")
    sospechosas = {k: v for k, v in informe.filas_sospechosas_de_total.items() if v}
    if sospechosas:
        print(f"  ¡ATENCION! filas sin ID y sin target (¿totales al pie?): "
              f"{sospechosas} -> NO se eliminaron; decision pendiente.")


def main() -> None:
    cfg = config.Config()
    config.DIR_PROCESADO.mkdir(parents=True, exist_ok=True)

    homogeneas, inf_h = loader.cargar_hojas_homogeneas(cfg, con_informe=True)
    _reportar("Hojas homogeneas (CUENTA_01..04)", homogeneas, inf_h)
    destino_h = config.DIR_PROCESADO / "homogeneas.parquet"
    homogeneas.to_parquet(destino_h, index=False)

    cuenta_05, inf_5 = loader.cargar_cuenta_05(cfg, con_informe=True)
    _reportar("Esquema distinto (CUENTA_05)", cuenta_05, inf_5)
    destino_5 = config.DIR_PROCESADO / "cuenta_05.parquet"
    cuenta_05.to_parquet(destino_5, index=False)

    print(f"\nArtefactos escritos en {config.DIR_PROCESADO} (gitignored):")
    print(f"  - {destino_h.name}\n  - {destino_5.name}")


if __name__ == "__main__":
    main()
