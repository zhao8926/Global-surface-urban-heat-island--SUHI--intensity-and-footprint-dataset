#-*-coding:utf-8
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
    shp_path = "E:\\SUHI_FP\\stats20260110\\boundaries_B_ISA_area.shp"
    geod = Geod(ellps="WGS84")
    gdf = gpd.read_file(shp_path)

    for year in range(2005,2025):
        tif_year = f"E:\\gis_data\\ISA\\ISA{year}.tif"
        src = rasterio.open(tif_year)

        gdf[f"tnISA{year}"] = 0
        gdf[f"ISA{year}"] = 0.0

        raster_bounds = box(*src.bounds)
        for idx, row in gdf.iterrows():
            geom = row.geometry
            if not geom.intersects(raster_bounds):
                continue

            intersection_geom = geom.intersection(raster_bounds)
            out_image, out_transform = mask(src, [mapping(intersection_geom)], crop=True)
            data = out_image[0]

            tif_num = np.sum(data == 1)

            pixel_area = gdf.at[idx, "pixel_km2"]
            UHI_area = tif_num * pixel_area

            gdf.at[idx, f"tnISA{year}"] = int(tif_num)
            
            gdf.at[idx, f"ISA{year}"] = UHI_area
        print(f"The area of ​​impermeable layers in {year} has been statistically analyzed")

    print("The total result has been calculated")
    out_path = shp_path
    gdf.to_file(out_path, encoding="utf-8")
    print("The total result has been saved:", out_path)