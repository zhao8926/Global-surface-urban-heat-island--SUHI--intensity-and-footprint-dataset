#-*-coding:utf-8-*-
import arcpy
import os

times = ['summer_day', 'summer_night', 'winter_day', 'winter_night']
time = times[3]
SUHII_trend = f"E:\\SUHI_FP\\stats20260110\\global_SUHII_{time}_dayu0.shp"
climate_position = "climate_po"
if climate_position in [f.name for f in arcpy.ListFields(SUHII_trend)]:
    print(f"The {climate_position} field already exists")
else:
    arcpy.AddField_management(SUHII_trend,climate_position,"LONG")
    print(f"The {climate_position} field has been added")

climate_zone_folder = "E:\\SUHI_FP\\SUHII_global\\climate_zone"
zones = ["Tropical","Arid","Temperate","Cold"]
climate_zones = [os.path.join(climate_zone_folder,f"{zone}.shp")
                 for zone in zones]
for i,zone in enumerate(climate_zones):
    trend = arcpy.SelectLayerByLocation_management(SUHII_trend,"INTERSECT",zone,"","NEW_SELECTION")
    arcpy.CalculateField_management(trend,climate_position,i+10,"PYTHON3")
    print(f"The trend point corresponding to {zone} has been marked")