#-*-coding:utf-8-*-
import rasterio
from pyproj import Geod
import geopandas as gpd
from rasterio.mask import mask
import numpy as np
from shapely.geometry import mapping
from shapely.geometry import box

def read_tif_resolution(tif):
    with rasterio.open(tif) as dataset:
        return dataset.res

def pixel_size_meters_from_degrees(xres_deg, yres_deg, lat_deg, lon_deg=0.0, ellps="WGS84"):
    g = Geod(ellps=ellps)
    _, _, dx_m = g.inv(lon_deg, lat_deg, lon_deg + xres_deg, lat_deg)
    _, _, dy_m = g.inv(lon_deg, lat_deg, lon_deg, lat_deg + yres_deg)
    return abs(dx_m), abs(dy_m)

if __name__ == "__main__":
    shp_path = "E:\\SUHI_FP\\stats20260129\\boundaries_BRA_ISA_area.shp"
    geod = Geod(ellps="WGS84")
    gdf = gpd.read_file(shp_path)
    times = ["summer_day", "summer_night", "winter_day", "winter_night"]
    time = times[3]
    tim_abbre = (time.split('_')[0][0] + time.split('_')[1][0]).lower()
    
    ref_tif_path = r"E:\gis_data\SUHII_Aqua_HTIA_Summer\HTIA_summer_day_2005.tif"

    with rasterio.open(ref_tif_path) as ref_src:
        tif_crs = ref_src.crs
        tif_res = ref_src.res # (xres, yres)
        tif_nodata = ref_src.nodata

        if gdf.crs != tif_crs:
            gdf = gdf.to_crs(tif_crs)

    for year in range(2005,2025):
        season = time.split("_")[0].capitalize()
        tif_year = fr"E:\gis_data\SUHII_Aqua_HTIA_{season}\HTIA_{time}_{year}.tif" ### SUHII_global_{year}_{time}.tif
        src = rasterio.open(tif_year)

        gdf[f"tn{tim_abbre}{year}"] = 0 ### tif num
        gdf[f"BRA{tim_abbre}{year}"] = 0.0 ### FP area

        raster_bounds = box(*src.bounds)
        for idx, row in gdf.iterrows():
            geom = row.geometry
            if not geom.intersects(raster_bounds):
                continue

            intersection_geom = geom.intersection(raster_bounds)
            out_image, out_transform = mask(src, [mapping(intersection_geom)], crop=True)
            data = out_image[0]

            tif_num = np.sum(data != src.nodata)

            pixel_area = gdf.at[idx, "pixel_km2"]
            UHI_area = tif_num * pixel_area

            gdf.at[idx, f"tn{tim_abbre}{year}"] = int(tif_num)
            
            gdf.at[idx, f"BRA{tim_abbre}{year}"] = UHI_area
        print(f"The BRA area of the UHI in {year} has been calculated")

    print("The total result has been calculated")
    out_path = shp_path
    gdf.to_file(out_path, encoding="utf-8")
    print("Saved:", out_path)