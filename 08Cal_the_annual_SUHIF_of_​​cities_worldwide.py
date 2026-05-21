# -*- coding: utf-8 -*-
import rasterio
from pyproj import Geod
import geopandas as gpd
from rasterio.mask import mask
import numpy as np
from shapely.geometry import mapping, box
import os

def pixel_size_meters_from_degrees(xres_deg, yres_deg, lat_deg, lon_deg=0.0, ellps="WGS84"):

    g = Geod(ellps=ellps)

    _, _, dx_m = g.inv(lon_deg, lat_deg, lon_deg + xres_deg, lat_deg)

    _, _, dy_m = g.inv(lon_deg, lat_deg, lon_deg, lat_deg + yres_deg)
    return abs(dx_m), abs(dy_m)

if __name__ == "__main__":
    times = ["summer_day", "summer_night", "winter_day", "winter_night"]
    time = times[3]
    
    shp_path = r"E:\SUHI_FP\stats20260110\research_boundary_final.shp"
    out_path = fr"E:\SUHI_FP\stats20260110\footprint_{time}.shp"
    SUHII_data_path = r"E:\gis_data\SUHII_Terra_Winter"
    ### r"E:\gis_data\SUHII_Terra_Summer"
    
    print(f"Reading vector: {shp_path}")
    gdf = gpd.read_file(shp_path)

    ref_year = 2005
    ref_tif_path = os.path.join(SUHII_data_path, f"global_{time}_{ref_year}.tif")
    
    if not os.path.exists(ref_tif_path):
        raise FileNotFoundError(f"Reference year file does not exist: {ref_tif_path}")

    with rasterio.open(ref_tif_path) as ref_src:
        tif_crs = ref_src.crs
        tif_res = ref_src.res # (xres, yres)
        tif_nodata = ref_src.nodata
        
        if gdf.crs != tif_crs:
            print(f"Hint: SHP coordinate system is inconsistent with TIF, reprojection is in progress...")
            gdf = gdf.to_crs(tif_crs)

    print("Pre-calculating the cell area (pa) of all geometries...")
    gdf["pa"] = 0.0
    
    for idx, row in gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
            
        centroid = geom.centroid
        lat = centroid.y
        
        proj_res_xy = pixel_size_meters_from_degrees(tif_res[0], tif_res[1], lat)
        
        # Calculate the area and convert it to km^2 (consistent with your original logic: / 1e6)
        pixel_area_km2 = (proj_res_xy[0] * proj_res_xy[1]) / 1e6
        gdf.at[idx, "pa"] = pixel_area_km2

    print("Pixel area (pa) calculation complete, starting year statistics...\n")

    for year in range(2005, 2025):
        tif_year_path = os.path.join(SUHII_data_path, f"global_{time}_{year}.tif")
        
        if not os.path.exists(tif_year_path):
            print(f"Skip {year} (file not found)")
            continue
            
        tn_col = f"tn_{year}" # tif num
        fp_col = f"FP_{year}" # FootPrint area
        gdf[tn_col] = 0
        gdf[fp_col] = 0.0
        
        with rasterio.open(tif_year_path) as src:
            raster_bounds = box(*src.bounds)
            
            for idx, row in gdf.iterrows():
                geom = row.geometry
                
                if not geom.intersects(raster_bounds):
                    continue
                
                try:
                    intersection_geom = geom.intersection(raster_bounds)
                    out_image, out_transform = mask(src, [mapping(intersection_geom)], crop=True)
                    data = out_image[0]
                    
                    tif_num = np.sum(data != src.nodata)
                    
                    if tif_num > 0:
                        pixel_area = gdf.at[idx, "pa"]
                        UHI_area = tif_num * pixel_area
                        
                        gdf.at[idx, tn_col] = int(tif_num)
                        gdf.at[idx, fp_col] = UHI_area
                        
                except Exception as e:
                    pass
        
        print(f"The area of ​​the urban heat island footprint in {year} has been statistically analyzed")

    print("The total result has been calculated")
    gdf.to_file(out_path, encoding="utf-8")
    print("The total result has been saved:", out_path)