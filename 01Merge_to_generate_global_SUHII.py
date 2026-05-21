#-*-coding:utf-8-*
import rasterio
from rasterio.transform import Affine
from rasterio.windows import from_bounds
import numpy as np
import os

def merge_global_standard_extent():
    base_folder = "F:\\gis_data\\SUHII_Aqua"
    output_summer_folder = "F:\\gis_data\\SUHII_Aqua_Summer"
    output_winter_folder = "F:\\gis_data\\SUHII_Aqua_Winter"
    
    os.makedirs(output_summer_folder, exist_ok=True)
    os.makedirs(output_winter_folder, exist_ok=True)

    time_phase = "day" ### day or night
    
    TARGET_NODATA = -32768 
    
    GLOBAL_LEFT = -180.0
    GLOBAL_RIGHT = 180.0
    GLOBAL_TOP = 90.0
    GLOBAL_BOTTOM = -90.0

    for year in range(2005, 2025):
        print(f"Processing: {year}...")

        s_path = os.path.join(base_folder, f"SUHII_global_{year}_summer_{time_phase}_dayu0.tif")
        w_path = os.path.join(base_folder, f"SUHII_global_{year}_winter_{time_phase}_dayu0.tif")

        if not os.path.exists(s_path) or not os.path.exists(w_path):
            print(f"Skip {year}: The file is missing.")
            continue

        out_s_path = os.path.join(output_summer_folder, f"global_summer_{time_phase}_{year}.tif")
        out_w_path = os.path.join(output_winter_folder, f"global_winter_{time_phase}_{year}.tif")

        with rasterio.open(s_path) as src_s, rasterio.open(w_path) as src_w:
            
            res_x = src_s.transform.a
            res_y = src_s.transform.e
            
            global_width = int(round((GLOBAL_RIGHT - GLOBAL_LEFT) / res_x))
            global_height = int(round((GLOBAL_TOP - GLOBAL_BOTTOM) / abs(res_y)))
            
            dst_transform = Affine(res_x, 0.0, GLOBAL_LEFT, 0.0, res_y, GLOBAL_TOP)
            
            out_meta = src_s.meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": global_height,
                "width": global_width,
                "transform": dst_transform,
                "dtype": rasterio.int16,
                "nodata": TARGET_NODATA,
                "compress": "lzw"
            })

            def place_into_global_canvas(src_dataset):
                canvas = np.full((global_height, global_width), TARGET_NODATA, dtype=np.int16)

                win = from_bounds(
                    src_dataset.bounds.left, src_dataset.bounds.bottom,
                    src_dataset.bounds.right, src_dataset.bounds.top,
                    transform=dst_transform
                )
                
                r_start = int(round(win.row_off))
                c_start = int(round(win.col_off))
                
                data = src_dataset.read(1)
                
                if src_dataset.nodata is not None:
                    data[data == src_dataset.nodata] = TARGET_NODATA
                    
                h, w = data.shape
                
                r_end = min(r_start + h, global_height)
                c_end = min(c_start + w, global_width)
                
                h_paste = r_end - r_start
                w_paste = c_end - c_start
                
                if h_paste > 0 and w_paste > 0:
                    canvas[r_start:r_end, c_start:c_end] = data[0:h_paste, 0:w_paste]
                
                return canvas

            s_data_global = place_into_global_canvas(src_s)
            w_data_global = place_into_global_canvas(src_w)

        y_indices = np.arange(global_height)

        latitudes = dst_transform.f + y_indices * dst_transform.e
        north_mask_1d = (latitudes > 0)[:, np.newaxis]

        global_summer = np.where(north_mask_1d, s_data_global, w_data_global)

        global_winter = np.where(north_mask_1d, w_data_global, s_data_global)

        with rasterio.open(out_s_path, "w", **out_meta) as dst:
            dst.write(global_summer, 1)

        with rasterio.open(out_w_path, "w", **out_meta) as dst:
            dst.write(global_winter, 1)

        print(f"{year} processing complete. Output dimensions: {global_width}x{global_height}")

if __name__ == "__main__":
    merge_global_standard_extent()