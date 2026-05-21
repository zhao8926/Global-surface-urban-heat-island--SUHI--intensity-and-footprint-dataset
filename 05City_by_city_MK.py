# -*- coding: utf-8 -*-
import geopandas as gpd
import numpy as np
import pymannkendall as mk

times = ['summer_day', 'summer_night', 'winter_day', 'winter_night']
time = times[3]
shp_path = f"E:\\SUHI_FP\\stats20260110\\global_SUHII_{time}_dayu0.shp"
gdf = gpd.read_file(shp_path)

years = list(range(2005, 2025))
fid_fields = [f"mean_{year}" for year in years]

for field in ["slope_decade", "mk_pvalue"]:
    if field not in gdf.columns:
        gdf[field] = np.nan

for idx, row in gdf.iterrows():
    vals = [row[f] for f in fid_fields]
    vals = np.array(vals, dtype=float)

    if np.isnan(vals).any():
        continue 

    vals_recent = vals#[10:20]
    res = mk.original_test(vals_recent)

    slope_decade = res.slope * 10
    p_value = res.p

    gdf.at[idx, "slope_decade"] = slope_decade
    gdf.at[idx, "mk_pvalue"] = p_value

gdf.to_file(shp_path, encoding="utf-8")
print("Result has been saved to the original shapefile:", shp_path)
