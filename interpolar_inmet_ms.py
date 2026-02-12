import numpy as np
import os
import geopandas as gpd
import pandas as pd
from pykrige.ok import OrdinaryKriging
import rasterio
from rasterio.mask import mask
from rasterio.transform import from_bounds
from pathlib import Path
import logging


pasta_interpolados = os.path.join(os.path.dirname(__file__), "dados_horarios_interpolados")
os.makedirs(pasta_interpolados, exist_ok=True)

# ======================================================
# CAMPOS PADRONIZADOS (IMASUL)
# ======================================================

CAMPO_TEMP = "temp_c"
CAMPO_UMID = "umid_pct"
CAMPO_PRESS = "press_hpa"
CAMPO_VENTO = "vento_ms"
CAMPO_CHUVA = "chuva_mm"


# ======================================================
# CAMINHOS
# ======================================================

BASE = Path(os.path.dirname(__file__))
SAIDA = BASE / "saida"
OUT = BASE / "dados_horarios_interpolados"
LIMITE = BASE / "saida"
LOGDIR = BASE / "logs"

OUT.mkdir(exist_ok=True)
LOGDIR.mkdir(exist_ok=True)


# ======================================================
# LOG
# ======================================================

def setup_logger(stamp):
    log = LOGDIR / f"{stamp}_krig.log"
    logging.basicConfig(
        filename=log,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    return logging.getLogger()


# ======================================================
# UTIL
# ======================================================

def ultimo_geojson():
    arquivos = sorted(SAIDA.glob("INMET_MS_*.geojson"))
    return arquivos[-1]


# ======================================================
# KRIGAGEM SIMPLES (SEM DEM)
# ======================================================

def krigagem_simples(gdf, campo, nome_saida, mask_geom, logger):

    # verifica se a variável existe
    if campo not in gdf.columns:
        logger.warning(f"{campo}: variável ausente no GeoJSON — ignorada")
        return

    # remove NaN
    gdf = gdf.dropna(subset=[campo]).copy()

    if len(gdf) < 5:
        logger.warning(f"{campo}: poucas estações válidas ({len(gdf)}) — ignorada")
        return

    logger.info(f"{campo}: {len(gdf)} estações válidas")

    lons = gdf.geometry.x.values
    lats = gdf.geometry.y.values
    vals = gdf[campo].astype(float).values

    # grade simples baseada no limite do MS
    bounds = mask_geom.total_bounds  # xmin, ymin, xmax, ymax

    nx = 300
    ny = 300

    gridx = np.linspace(bounds[0], bounds[2], nx)
    gridy = np.linspace(bounds[1], bounds[3], ny)

    OK = OrdinaryKriging(
        lons,
        lats,
        vals,
        variogram_model="linear",
        variogram_parameters={"slope": 1.0, "nugget": 0.0},
        verbose=False,
        enable_plotting=False,
    )

    z, _ = OK.execute("grid", gridx, gridy)

    z = np.flipud(z)  # corrige orientação

    # salva raster temporário
    temp_tif = OUT / f"{nome_saida}_tmp.tif"
    final_tif = OUT / f"{nome_saida}_krig.tif"

    transform = from_bounds(
        bounds[0], bounds[1], bounds[2], bounds[3], nx, ny
    )

    with rasterio.open(
        temp_tif,
        "w",
        driver="GTiff",
        height=z.shape[0],
        width=z.shape[1],
        count=1,
        dtype=z.dtype,
        crs="WGS84",
        transform=transform,
    ) as dst:
        dst.write(z, 1)

    # recorte MS
    with rasterio.open(temp_tif) as src:
        out_image, out_transform = mask(
            src, mask_geom.geometry, crop=True
        )

        with rasterio.open(
            final_tif,
            "w",
            driver="GTiff",
            height=out_image.shape[1],
            width=out_image.shape[2],
            count=1,
            dtype=out_image.dtype,
            crs="WGS84",
            transform=out_transform,
        ) as dst:
            dst.write(out_image)

    temp_tif.unlink(missing_ok=True)

    logger.info(f"{campo}: raster gerado com sucesso")


# ======================================================
# MAIN
# ======================================================

def main():

    geojson = ultimo_geojson()
    stamp = geojson.stem.replace("INMET_MS_", "")
    logger = setup_logger(stamp)

    logger.info("Iniciando interpolação")

    gdf = gpd.read_file(geojson)
    
     # força conversão numérica robusta para TODOS os campos
    campos_numericos = [CAMPO_TEMP, CAMPO_UMID, CAMPO_PRESS, CAMPO_VENTO, CAMPO_CHUVA]
    
    for campo in campos_numericos:
        if campo in gdf.columns:
            gdf[campo] = (
                gdf[campo]
                .astype(str)
                .str.replace(",", ".", regex=False)
            )
            gdf[campo] = pd.to_numeric(gdf[campo], errors="coerce")



    limite = gpd.read_file(list(LIMITE.glob("INMET_MS_*.geojson"))[0])

    variaveis = {
        "temp_c": "temp",
        "umid_pct": "umid",
        "press_hpa": "press",
        "vento_ms": "vento",
        "chuva_mm": "chuva",
    }

    for campo, suf in variaveis.items():
        krigagem_simples(
            gdf,
            campo,
            f"{stamp}_{suf}",
            limite,
            logger
        )

    logger.info("Interpolação finalizada")


if __name__ == "__main__":
    main()
