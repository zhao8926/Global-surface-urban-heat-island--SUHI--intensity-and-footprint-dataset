#-*-coding:utf-8-*-
import geopandas as gpd
times = ['summer_day', 'summer_night', 'winter_day', 'winter_night']
time = times[3]
shp_path = f"E:\\SUHI_FP\\stats20260110\\global_SUHII_{time}_dayu0.shp"
gdf = gpd.read_file(shp_path)

climate_mapping = {"Tropical":10,"Arid":11,"Temperate":12,"Cold":13}
filtered_gdf = gdf[gdf['climate_po'] == climate_mapping['Cold']]

if len(filtered_gdf) > 0:
    target_data = filtered_gdf['slope_deca']

    mean_val = target_data.mean()
    std_val = target_data.std()
    print(f"{climate_mapping['Cold']} number of records filtered out: {len(filtered_gdf)}")
    print(f"Mean: {mean_val:.4f}")
    print(f"Std:  {std_val:.4f}")

else:
    print("No data was found for climate_po as '10'. Please check the field value type (is it a string or a number?)")