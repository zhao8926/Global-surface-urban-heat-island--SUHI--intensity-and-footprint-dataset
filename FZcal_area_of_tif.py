import rasterio
import numpy as np
import pandas as pd

def compute_area_by_latband_corrected(raster_path, mask_values=None):
    R = 6371007.181 

    with rasterio.open(raster_path) as src:
        data = src.read(1)
        nodata = src.nodata
        h, w = src.height, src.width
        trans = src.transform

        if not (abs(trans.b) < 1e-12 and abs(trans.d) < 1e-12):
            raise RuntimeError("The raster contains rotation parameters; area calculation requires resampling.")

        pixel_width_deg = trans.a
        pixel_height_deg = abs(trans.e)

        lat_top = trans.f

        row_indices = np.arange(h + 1)
        lat_edges = lat_top - row_indices * pixel_height_deg

        lat_edges = np.clip(lat_edges, -90, 90)

        lat_edges_rad = np.deg2rad(lat_edges)
        lon_width_rad = np.deg2rad(pixel_width_deg)

        # Area = R^2 * (lon2 - lon1) * (sin(lat1) - sin(lat2))
        sin_lat = np.sin(lat_edges_rad)

        diff_sin = sin_lat[:-1] - sin_lat[1:]
        
        area_per_pixel_row = (R**2) * lon_width_rad * diff_sin

        # (h,) -> (h, 1) -> (h, w)
        area_matrix = np.broadcast_to(area_per_pixel_row[:, np.newaxis], (h, w))

        if nodata is not None:
            if np.isnan(nodata):
                nodata_mask = ~np.isnan(data)
            else:
                nodata_mask = data != nodata
        else:
            nodata_mask = np.ones_like(data, dtype=bool)

        if mask_values is None:
            valid_mask = nodata_mask
        elif callable(mask_values):
            valid_mask = nodata_mask & mask_values(data)
        else:
            valid_mask = nodata_mask & np.array(mask_values, dtype=bool)

        total_area_m2 = np.sum(area_matrix, where=valid_mask)

        return area_per_pixel_row, area_matrix, total_area_m2

### ITA "E:\\gis_data\\SUHII_Terra_Summer\\global_summer_day_2018.tif"
### DEA "E:\\gis_data\\SUHII_DEA_or_SUE\\seasonal_data\\SUHII_DEA_2018_sd.tif"
### SUE "E:\\gis_data\\SUHII_DEA_or_SUE\\merged_data\\SUHII_SUE_2018_sd.tif"
### city "E:\\SUHI_FP\\stats20260110\\city\\SUE_2018_sd_Sanya.tif"

tif_path = "E:\\SUHI_FP\\stats20260110\\city\\DEA_2018_sd_Rio_de_Janeiro.tif"
_,_,area = compute_area_by_latband_corrected(tif_path)
print(f"{tif_path} area：{area/1e6}km2")