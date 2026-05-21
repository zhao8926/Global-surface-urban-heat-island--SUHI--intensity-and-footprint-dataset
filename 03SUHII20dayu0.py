#-*-coding:utf-8-*
import arcpy

times = ['summer_day', 'summer_night', 'winter_day', 'winter_night']
time = times[3]
shp = f"E:\\SUHI_FP\\stats20260110\\global_cities_with_UHI_{time}.shp"
FID = [f"mean_{year}" for year in range(2005,2025)]
field_name = "judge"
if field_name not in [f.name for f in arcpy.ListFields(shp)]:
    arcpy.AddField_management(shp,field_name,"LONG")
    print(f"{field_name} has been added")
else:
    print(f"{field_name} existing")
FID.append(field_name)

with arcpy.da.UpdateCursor(shp,FID) as Cursor:
    for row in Cursor:
        if all(x>0 for x in row[:-1]):
            # print("该城市20年都存在热岛")
            row[-1] = 1
        else:
            row[-1] = 0
        Cursor.updateRow(row)
print("Cities that have been identified as having a heat island effect for 20 years")

point_shp = f"E:\\SUHI_FP\\stats20260110\\global_SUHII_{time}.shp"
point_dayu0 = f"E:\\SUHI_FP\\stats20260110\\global_SUHII_{time}_dayu0.shp"
arcpy.management.FeatureToPoint(shp,point_shp)
print("FeatureToPoint")
arcpy.conversion.ExportFeatures(point_shp,point_dayu0,f"{field_name} > 0")
print("ExportFeatures")
point_magnitude = f"E:\\SUHI_FP\\stats20260110\\global_SUHII_{time}_magnitude.shp"
arcpy.conversion.ExportFeatures(point_shp,point_magnitude,f"UHI_mean > 0")
print("ExportFeatures")