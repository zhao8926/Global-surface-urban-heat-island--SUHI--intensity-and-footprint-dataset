#-*-coding:utf-8-*
import rasterio
import os
import geopandas as gpd
import glob
from rasterstats import zonal_stats
import pandas as pd

### Loading data
city_shp = 'E:\\gis_data\\administrative_boundaries_baseline\\research_boundary_final.shp'
gdf = gpd.read_file(city_shp)

times = ['summer_day', 'summer_night', 'winter_day', 'winter_night']
time = times[3]
raster_folder = "E:\\gis_data\\SUHII_Terra_Winter"
### "E:\\gis_data\\SUHII_Terra_Summer"
### "E:\\gis_data\\SUHII_Terra_Winter"
### "E:\\SUHI_FP\\SUHII_global\\Dataset_int16_global"
tif_list = [os.path.join(raster_folder,f"global_{time}_{year}.tif") for year in range(2005,2025)]
tif_nodata = None
with rasterio.open(tif_list[0]) as src:
    tif_nodata = src.nodata
    print("nodata value: ", tif_nodata)

### "E:\\SUHI_FP\\SUHII_global\\Dataset_int16_global\\global_summer_day_2005.tif"
results_df = pd.DataFrame()
results_df["city_id"] = gdf.index

year = 2005
for tif_path in tif_list:
    print(f"Data for {year} is being compiled...")
    stats = zonal_stats(
        gdf, tif_path, stats = ["mean", "std"], nodata = tif_nodata, geojson = False
    )
    stats_df = pd.DataFrame(stats)
    results_df[f"mean_{year}"] = stats_df["mean"]
    results_df[f"std_{year}"] = stats_df["std"]
    gdf[f"mean_{year}"]=stats_df["mean"]
    gdf[f"std_{year}"]=stats_df["std"]
    print(f"{year} {time} has been compiled")
    year = year + 1

mean_all_years = results_df.filter(like="mean_").mean(axis=1)
std_all_years = results_df.filter(like="mean_").std(axis=1)

gdf["UHI_mean"] = mean_all_years
gdf["UHI_std"] = std_all_years

output_shp = f"E:\\SUHI_FP\\stats20260110\\global_cities_with_UHI_{time}.shp"
gdf.to_file(output_shp, encoding="utf-8")
