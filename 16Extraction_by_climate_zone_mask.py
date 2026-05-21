# -*- coding: utf-8 -*-
import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling
import os

def extract_by_climate_zones(target_raster_path, climate_zone_path, output_folder):

    zone_mapping = {
        1: "Tropical",
        2: "Arid",
        3: "Temperate",
        4: "Cold",
        5: "Polar"
    }

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with rasterio.open(target_raster_path) as src_target:
        target_data = src_target.read(1)
        target_meta = src_target.profile
        target_transform = src_target.transform
        target_crs = src_target.crs
        target_shape = target_data.shape
        
        nodata_value = src_target.nodata
        if nodata_value is None:
            nodata_value = -9999
            target_meta.update(nodata=nodata_value)

        print(f"Processing target raster: {target_raster_path}")
        print(f"Target size: {target_shape}")

        with rasterio.open(climate_zone_path) as src_climate:
            aligned_climate_data = np.zeros(target_shape, dtype=src_climate.read(1).dtype)

            reproject(
                source=rasterio.band(src_climate, 1),
                destination=aligned_climate_data,
                src_transform=src_climate.transform,
                src_crs=src_climate.crs,
                dst_transform=target_transform,
                dst_crs=target_crs,
                resampling=Resampling.nearest
            )
            
            print("Climate zoning data has been aligned to the target raster grid.")

        for zone_id, zone_name in zone_mapping.items():
            print(f"Fetching partitions: {zone_id} - {zone_name} ...")
            
            mask = (aligned_climate_data == zone_id)
            
            if not np.any(mask):
                continue

            extracted_data = np.where(mask, target_data, nodata_value)
            
            output_filename = f"{os.path.basename(target_raster_path)[:-4]}_{zone_name}.tif"
            output_path = os.path.join(output_folder, output_filename)
            
            output_meta = target_meta.copy()
            output_meta.update(compress='lzw') 

            with rasterio.open(output_path, "w", **output_meta) as dest:
                dest.write(extracted_data, 1)
                
            print(f"  -> Saved: {output_path}")

    print("\nAll processing complete!")


### ITA "E:\\gis_data\\SUHII_Terra_Summer\\global_summer_day_2018.tif"
### DEA "E:\\gis_data\\SUHII_DEA_or_SUE\\seasonal_data\\SUHII_DEA_2018_sd.tif"
### SUE "E:\\gis_data\\SUHII_DEA_or_SUE\\merged_data\\SUHII_SUE_2018_sd.tif"
if __name__ == "__main__":
    my_target_tif = "E:\\gis_data\\SUHII_DEA_or_SUE\\merged_data\\SUHII_SUE_2018_wn.tif"
    my_climate_tif = "E:\\SUHI_FP\\SUHII_global\\climate_zone\\climate_zone.tif"
    save_dir = "E:\\SUHI_FP\\stats20260110\\climate_zone"

    extract_by_climate_zones(my_target_tif, my_climate_tif, save_dir)