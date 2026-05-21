# -*- coding: utf-8 -*-
import arcpy

times = ['summer_day', 'summer_night', 'winter_day', 'winter_night']
time = times[3]
shp = f"E:\\SUHI_FP\\stats20260110\\footprint_{time}.shp"
FID = [f"FP_{year}" for year in range(2005,2025)]
field_name = "judge"
if field_name not in [f.name for f in arcpy.ListFields(shp)]:
    arcpy.AddField_management(shp,field_name,"LONG")
    print(f"{field_name} field added")
else:
    print(f"{field_name} already exists, proceed with subsequent operations")
FID.append(field_name)

with arcpy.da.UpdateCursor(shp,FID) as Cursor:
    for row in Cursor:
        if all(x>0 for x in row[:-1]):
            row[-1] = 1
        else:
            row[-1] = 0
        Cursor.updateRow(row)
print("Cities with heat island effects for 20 years have been identified")

point_shp = f"E:\\SUHI_FP\\stats20260110\\footprint_point_{time}.shp"
point_dayu0 = f"E:\\SUHI_FP\\stats20260110\\footprint_point_{time}_dayu0.shp"
arcpy.management.FeatureToPoint(shp,point_shp)
print("FeatureToPoint")
arcpy.conversion.ExportFeatures(point_shp,point_dayu0,f"{field_name} > 0")
print("ExportFeatures")
point_magnitude = f"E:\\SUHI_FP\\stats20260110\\footprint_point_{time}_magnitude.shp"
ID = []
with arcpy.da.SearchCursor(point_shp,["ID"]+[f"FP_{year}" for year in range(2005,2025)]) as Cursor:
    for row in Cursor:
        oid = row[0]
        fp_values = row[1:]

        # if all(val != 0 for val in fp_values):
        if any(val != 0 for val in fp_values):
            ID.append(oid)
arcpy.conversion.ExportFeatures(point_shp,point_magnitude,f"ID in {tuple(ID)}")
print("ExportFeatures")