#-*-coding:utf-8-*-
import rasterio
import numpy as np
from scipy.ndimage import label
from rasterio.features import shapes
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.ops import unary_union
from pyproj import Geod
import fiona
from rasterio.mask import mask
import warnings
warnings.filterwarnings("ignore")

geod = Geod(ellps="WGS84")

def compute_regions_area_perimeter_geod(input_data, transform=None, threshold=0, structure=None, nodata_val=None):

    results = []

    if isinstance(input_data, str):
        with rasterio.open(input_data) as src:
            arr = src.read(1)
            transform = src.transform
            crs = src.crs
            if crs is None or not crs.is_geographic:
                raise ValueError("Raster must be latitude and longitude (EPSG:4326)")
            if nodata_val is None:
                nodata_val = src.nodata
    else:
        arr = input_data
        if transform is None:
            raise ValueError("Array input must provide a transform")

    if nodata_val is not None:
        arr = np.where(arr == nodata_val, 0, arr)

    if structure is None:
        structure = np.ones((3,3), dtype=int)

    mask_arr = arr > threshold
    labeled, n = label(mask_arr, structure=structure)

    for label_id in range(1, labeled.max() + 1):
        single_mask = (labeled == label_id).astype("uint8")
        geom_gen = shapes(single_mask, mask=single_mask, transform=transform)
        polys = [shape(geom_dict) for geom_dict, val in geom_gen]

        pixel_count = int((labeled == label_id).sum())
        if len(polys) == 0:
            continue
        geom = polys[0] if len(polys) == 1 else unary_union(polys)

        area_m2, _ = geod.geometry_area_perimeter(geom)
        area_m2 = abs(area_m2)

        def geom_total_perimeter(g):
            total_perim = 0
            if isinstance(g, Polygon):
                x, y = g.exterior.xy
                total_perim += geod.line_length(x, y)
                for interior in g.interiors:
                    x, y = interior.xy
                    total_perim += geod.line_length(x, y)
            elif isinstance(g, MultiPolygon):
                for p in g.geoms:
                    total_perim += geom_total_perimeter(p)
            return total_perim

        perimeter_m = geom_total_perimeter(geom)

        results.append({
            "label": label_id,
            "area_m2": area_m2,
            "perimeter_m": perimeter_m,
            "pixel_count": pixel_count,
            "geometry": geom
        })

    return results

def compute_weighted_frac(res):
    areas = np.array([r["area_m2"] for r in res])
    perimeters = np.array([r["perimeter_m"] for r in res])
    fracs = np.array([(2 * np.log(0.25 * p)) / np.log(a) for a, p in zip(areas, perimeters)])
    frac_weighted = np.sum((areas / np.sum(areas)) * fracs)
    return fracs, frac_weighted

tims = ['summer_day','summer_night','winter_day','winter_night']
years = range(2005, 2015)

shp_file = "E:\\SUHI_FP\\stats20260129\\boundaries_FRAC_UHI2005_2014.shp"

with fiona.open(shp_file, "r") as src:
    features = list(src)
    schema = src.schema.copy()
    crs = src.crs

for year in years:
    print(f"\n===== processing {year} =====")

    for tim in tims:
        tim_abbre = (tim.split('_')[0][0] + tim.split('_')[1][0]).lower()
        field = f"FRAC{year}{tim_abbre}"

        if field not in schema["properties"]:
            schema["properties"][field] = "float:24.8"

        season = tim.split("_")[0].capitalize()
        tif_file = f"E:\\gis_data\\SUHII_Aqua_{season}\\global_{tim.lower()}_{year}.tif"
        
        ### "E:\\gis_data\\SUHII_Aqua_Summer\\global_summer_day_2005.tif"

        print(f" -> Processing time period {tim} ...")
        with rasterio.open(tif_file) as src_raster:
            for feature in features:
                geom = [feature["geometry"]]
                try:
                    out_image, out_transform = mask(src_raster, geom, crop=True, all_touched=True)
                    arr = out_image[0]
                    
                    if src_raster.nodata is not None:
                        arr = np.where(arr == src_raster.nodata, np.nan, arr)

                    if np.all(np.isnan(arr)) or np.nanmax(arr) <= 0:
                        frac_weighted = 0.0
                    else:
                        res_partition = compute_regions_area_perimeter_geod(arr, transform=out_transform)
                        if len(res_partition) == 0:
                            frac_weighted = 0.0
                        else:
                            _, frac_weighted = compute_weighted_frac(res_partition)

                except ValueError:
                    frac_weighted = 0.0

                feature["properties"][field] = frac_weighted

    with fiona.open(shp_file, "w", driver="ESRI Shapefile", crs=crs, schema=schema) as dst:
        for feature in features:
            dst.write(feature)

    print(f"The FRAC of year {year} has been written to shapefile.")
