#-*-coding:utf-8-*-
import arcpy
import os
import numpy as np

times = ['summer_day', 'summer_night', 'winter_day', 'winter_night']
time = times[3]
SUHII_data = f"E:\\SUHI_FP\\stats20260110\\global_SUHII_{time}_magnitude.shp"

value = []
with arcpy.da.SearchCursor(SUHII_data,["UHI_mean"]) as Cursor:
    for row in Cursor:
        value.append(row[0])
mean = np.mean(value)
std = np.std(value,ddof=0)
print(f"global {time} has a mean of {mean/100} and a standard deviation of {std/100}")


zone_folder = "E:\\SUHI_FP\\SUHII_global\\climate_zone"
zones = ['Tropical','Arid','Temperate','Cold']
for zone in zones:
    zone_shp = os.path.join(zone_folder,f"{zone}.shp")
    SUHII_zone = arcpy.SelectLayerByLocation_management(SUHII_data,"INTERSECT",zone_shp)
    value = []
    with arcpy.da.SearchCursor(SUHII_zone,["UHI_mean"]) as Cursor:
        for row in Cursor:
            value.append(row[0])
    mean = np.mean(value)
    std = np.std(value,ddof=0)
    print(f"The mean of {zone} {time} is {mean/100}, and the standard deviation is {std/100}")

    