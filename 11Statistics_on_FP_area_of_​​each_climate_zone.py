#-*-coding:utf-8-*-
import arcpy
import csv

def extract_num_from_string(text):
    return "".join(filter(str.isdigit,text))

times = ['summer_day', 'summer_night', 'winter_day', 'winter_night']
time = times[3]
FP_point_shp = f"E:\\SUHI_FP\\stats20260110\\footprint_point_{time}.shp"
climate_zones = ["Tropical","Arid","Temperate","Cold"]
climate_map = {10:0, 11:1, 12:2, 13:3}

FP_fields = [f"FP_{year}" for year in range(2005,2025)]
# FP_fields.append("czone")
data = {}
for FP_field in FP_fields:
    fields = [FP_field, "czone"]
    year = extract_num_from_string(FP_field)
    values = [0,0,0,0]
    with arcpy.da.SearchCursor(FP_point_shp, fields) as Cursor:
        for row in Cursor:
            if row[1] in climate_map:
                values[climate_map[row[1]]] += row[0]
    data[year] = values
    print(f"Data for year {year} has been compiled")

# save_to_csv_file
csv_path = f"E:\\data_analysis\\UHI\\statistics20260110\\004FP_area_{time}.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Year"] + climate_zones)
    for year, values in data.items():
        writer.writerow([year] + values)

print(f"Result has been saved to: {csv_path}")