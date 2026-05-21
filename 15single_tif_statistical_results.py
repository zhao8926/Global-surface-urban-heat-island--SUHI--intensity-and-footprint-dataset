# -*- coding: utf-8 -*-
import rasterio
import numpy as np

def get_stats_small_raster(tif_path):
    with rasterio.open(tif_path) as src:
        data = src.read(1)
        nodata = src.nodata
        
        valid_mask = data > 0

        if nodata is not None:
            valid_mask = valid_mask & (data !=nodata)

        masked_data = data[valid_mask]

        mean_val = np.mean(masked_data)
        std_val = np.std(masked_data)
        
        print(f"mean_val: {mean_val}")
        print(f"std_val: {std_val}")
        return mean_val, std_val

tif = "E:\\gis_data\\SUHII_DEA_or_SUE\\merged_data\\SUHII_SUE_2018_wn.tif"
get_stats_small_raster(tif)

### ITA "E:\\gis_data\\SUHII_Terra_Summer\\global_summer_day_2018.tif"
### DEA "E:\\gis_data\\SUHII_DEA_or_SUE\\seasonal_data\\SUHII_DEA_2018_sd.tif"
### SUE "E:\\gis_data\\SUHII_DEA_or_SUE\\merged_data\\SUHII_SUE_2018_sd.tif"