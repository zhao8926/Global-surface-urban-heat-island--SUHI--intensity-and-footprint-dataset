#-*-coding:utf-8-*-
import arcpy

### 10 -> Tropical zone
### 11 -> Arid zone
### 12 -> Temperate zone
### 13 -> Cold zone

times = ['summer_day', 'summer_night', 'winter_day', 'winter_night']
for time in times:
    # time = times[0]
    print(f"\nProcessing data for period {time}")
    FP_point_shp = f"E:\\SUHI_FP\\stats20260110\\footprint_point_{time}.shp"
    climate_zones = ["Tropical","Arid","Temperate","Cold"]

    field = "czone" ### climate_zone
    if field in [f.name for f in arcpy.ListFields(FP_point_shp)]:
        print(f"{field} already exists")
    else:
        arcpy.AddField_management(FP_point_shp,field,"LONG")
        print(f"{field} field added")

    for i,zone in enumerate(climate_zones):
        zone_shp = f"E:\\SUHI_FP\\SUHII_global\\climate_zone\\{zone}.shp"
        FP_zone = arcpy.SelectLayerByLocation_management(FP_point_shp,"INTERSECT",zone_shp,"","NEW_SELECTION")
        arcpy.CalculateField_management(FP_zone,field,i+10,"PYTHON3")
        print(f"{zone} climate zone is identified")
