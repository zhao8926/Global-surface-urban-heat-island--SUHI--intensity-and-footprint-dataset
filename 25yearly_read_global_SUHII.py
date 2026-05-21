#-*-coding:utf-8-*-
import os
import rasterio
from tqdm import tqdm
import numpy as np
import scipy.stats as stats
import pandas as pd

seasons = [["summer_day","sd"], ["summer_night", "sn"], ["winter_day", "wd"], ["winter_night", "wn"]]
season =  seasons[3] ###  ###  ### 
ID = season[0].split("_")[0].capitalize()
data = "Aqua" ### Terra or Aqua
folder = fr"E:\gis_data\SUHII_{data}_{ID}"
### example SUHII : "global_summer_day_2005.tif"
output_file = fr"E:\data_analysis\UHI\statistics20260110\global_cities_SUHII_statistics_{season[1]}.xlsx"

def stats_tif(tif_path):
    try:
        with rasterio.open(tif_path) as src:
            masked_data = src.read(1, masked=True)
            valid_data = masked_data[masked_data > 0].compressed()

            valid_data = valid_data * 0.01

            if valid_data.size == 0:
                return None

            tqdm.write(f"processing: {os.path.basename(tif_path)} | num of valid pixels: {valid_data.size}")

            median_val = np.median(valid_data)
            mean_val = np.mean(valid_data)
            min_val = np.min(valid_data)
            max_val = np.max(valid_data)
            std_val = np.std(valid_data)

            sem = stats.sem(valid_data)
            lower, upper = stats.t.interval(
                confidence=0.95, 
                df=len(valid_data) - 1, 
                loc=mean_val, 
                scale=sem
            )
            
            ci_half = (upper - lower) / 2

            mean_std_str = f"{mean_val:.3f} ± {std_val:.3f}"
            mean_ci_str = f"{mean_val:.3f} ± {ci_half:.3f}"

            stats_dict = {
                "Median": median_val,
                "Mean": mean_val,
                "Std": std_val,
                "Min": min_val,
                "Max": max_val,
                "95CI Lower": lower,
                "95CI Upper": upper,
                "95CI Half Width": ci_half,
                "Mean ± Std": mean_std_str,
                "Mean ± 95%CI": mean_ci_str
            }
            
            return stats_dict

    except FileNotFoundError:
        print(f"Error: file {tif_path} not found")
        return None
    except Exception as e:
        print(f"An unknown error occurred while processing {tif_path}: {e}")
        return None
    
results = []

print("Starting batch processing...")

for year in tqdm(range(2005, 2025)):
    file_name = f"global_{season[0]}_{year}.tif"
    SUHII_PATH = os.path.join(folder, file_name)
    
    if os.path.exists(SUHII_PATH):
        year_stats = stats_tif(SUHII_PATH)
        
        year_stats["Year"] = year
        results.append(year_stats)
    else:
        print(f"Skip: File does not exist {file_name}")

if results:
    results_df = pd.DataFrame(results)
    
    cols = ["Year"] + [col for col in results_df.columns if col != "Year"]
    results_df = results_df[cols]

    try:
        results_df.to_excel(output_file, index=False)
        print("-" * 30)
        print(f"Statistics complete! Results saved to: {output_file}")
        print(f"A total of {len(results_df)} years of data were processed.")
    except PermissionError:
        print(f"Save failed: Please close the open {output_file} file and try again.")
else:
    print("No valid data was generated, and the file was not saved.")


