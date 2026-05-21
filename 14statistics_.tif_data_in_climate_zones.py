import rasterio
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
import numpy as np
import pandas as pd
from tqdm import tqdm

def calculate_stats_memory_safe(climate_path, target_path):
    stats = {}
    valid_zones = [1, 2, 3, 4, 5]
    climate_names = {1: "Tropical", 2: "Arid", 3: "Temperate", 4: "Cold", 5: "Polar"}
    
    for z in valid_zones:
        stats[z] = {
            'sum': 0.0, 'sq_sum': 0.0, 'count': 0, 
            'min': float('inf'), 'max': float('-inf')
        }

    with rasterio.open(target_path) as src_target:
        target_nodata = src_target.nodata
        
        with rasterio.open(climate_path) as src_clim:

            with WarpedVRT(src_clim, 
                           crs=src_target.crs,
                           transform=src_target.transform,
                           width=src_target.width,
                           height=src_target.height,
                           resampling=Resampling.nearest) as vrt_clim:

                windows = list(src_target.block_windows(1))
                
                for ji, window in tqdm(windows, desc="block statistics progress"):
                    data_target = src_target.read(1, window=window)
                    data_clim = vrt_clim.read(1, window=window)

                    mask = np.isin(data_clim, valid_zones)
                    if target_nodata is not None:
                        mask = mask & (data_target != target_nodata) & (data_target > 0)

                    if not np.any(mask):
                        continue

                    valid_clim_pixels = data_clim[mask]
                    valid_target_pixels = data_target[mask]

                    unique_zones_in_block = np.unique(valid_clim_pixels)
                    
                    for zone in unique_zones_in_block:
                        z_mask = (valid_clim_pixels == zone)
                        z_values = valid_target_pixels[z_mask]

                        z_values_f64 = z_values.astype(np.float64)
                        
                        z_sum = np.sum(z_values_f64)
                        z_sq_sum = np.sum(z_values_f64 ** 2)
                        z_count = z_values_f64.size
                        z_min = np.min(z_values_f64)
                        z_max = np.max(z_values_f64)

                        stats[zone]['count'] += z_count
                        stats[zone]['sum'] += z_sum
                        stats[zone]['sq_sum'] += z_sq_sum
                        if z_min < stats[zone]['min']: stats[zone]['min'] = z_min
                        if z_max > stats[zone]['max']: stats[zone]['max'] = z_max

    print("\nSummarizing results...")
    final_results = []
    
    for zone_id in valid_zones:
        s = stats[zone_id]
        if s['count'] > 0:
            mean = s['sum'] / s['count']
            # variance = (Sum(x^2)/N) - Mean^2
            variance = (s['sq_sum'] / s['count']) - (mean ** 2)
            std_dev = np.sqrt(max(0, variance))
            
            final_results.append({
                "Zone_ID": zone_id,
                "Climate_Type": climate_names[zone_id],
                "Count": s['count'],
                "Min": int(s['min']),
                "Max": int(s['max']),
                "Mean": round(mean, 4),
                "Std_Dev": round(std_dev, 4)
            })
        else:
            final_results.append({
                "Zone_ID": zone_id,
                "Climate_Type": climate_names[zone_id],
                "Count": 0, "Min": None, "Max": None, "Mean": None, "Std_Dev": None
            })
            
    return pd.DataFrame(final_results)

if __name__ == "__main__":
    climate_tif = "E:\\SUHI_FP\\SUHII_global\\climate_zone\\climate_zone.tif"
    target_tif = "E:\\gis_data\\SUHII_Terra_Winter\\global_winter_night_2018.tif"
    ### ITA "E:\\gis_data\\SUHII_Terra_Summer\\global_summer_day_2018.tif"
    ### DEA "E:\\gis_data\\SUHII_DEA_or_SUE\\seasonal_data\\SUHII_DEA_2018_sd.tif"
    ### SUE "E:\\gis_data\\SUHII_DEA_or_SUE\\merged_data\\SUHII_SUE_2018_sd.tif"

    try:
        df = calculate_stats_memory_safe(climate_tif, target_tif)
        print("\nStatistical results:")
        print(df)
        
        # save
        df.to_csv(r"E:\data_analysis\UHI\statistics20260110\climate_stats_ITA_2018_wn.csv", index=False)
        print("Results have been saved to CSV.")
        
    except Exception as e:
        print(f"Error occurred: {e}")