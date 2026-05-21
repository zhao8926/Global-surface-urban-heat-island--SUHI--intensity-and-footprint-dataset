#-*-coding:utf-8-*-
import os
import glob
import numpy as np
import rasterio
from rasterio.merge import merge

def process_and_mosaic_images(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    tif_files = glob.glob(os.path.join(input_folder, "SUHII_SUE*.tif"))

    file_groups = {}

    print(f"Scanning folder: {input_folder} ...")
    
    for file_path in tif_files:
        filename = os.path.basename(file_path)
        parts = filename.split('_')
        
        if len(parts) == 4:
            # parts[0]: SUHII
            # parts[1]: data_type (DEA/SUE)
            # parts[2]: year
            # parts[3]: position (North/South)
            # parts[4]: time (sd/sn/wd/wn)
            
            time_part = parts[3].split("-")[0]
            parts.remove(parts[-1])
            parts.append(time_part)
            key = "_".join(parts[:4]) 
            
            if key not in file_groups:
                file_groups[key] = []
            file_groups[key].append(file_path)

    print(f"A total of {len(file_groups)} groups of data were found and need to be processed.")

    for group_key, file_list in file_groups.items():
        try:
            print(f"Processing grouping: {group_key} (containing {len(file_list)} files)")
            
            src_files_to_mosaic = []
            
            for fp in file_list:
                src = rasterio.open(fp)
                src_files_to_mosaic.append(src)
            
            mosaic, out_trans = merge(src_files_to_mosaic)
            
            out_meta = src_files_to_mosaic[0].meta.copy()
            
            NEW_NODATA_VALUE = -32768
            
            mosaic_float = mosaic.astype(np.float32)
            
            original_nodata = src_files_to_mosaic[0].nodata
            
            if original_nodata is not None:
                mask = (mosaic_float == original_nodata)
            else:
                mask = np.isnan(mosaic_float)

            mosaic_scaled = mosaic_float * 100
            
            mosaic_scaled[mask] = NEW_NODATA_VALUE
            
            mosaic_int16 = mosaic_scaled.astype(np.int16)

            out_meta.update({
                "driver": "GTiff",
                "height": mosaic_int16.shape[1],
                "width": mosaic_int16.shape[2],
                "transform": out_trans,
                "dtype": "int16",
                "nodata": NEW_NODATA_VALUE,
                "compress": "lzw"
            })

            output_filename = f"{group_key}.tif"
            output_path = os.path.join(output_folder, output_filename)
            
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(mosaic_int16)
                
            print(f" -> Saved: {output_filename}")

            for src in src_files_to_mosaic:
                src.close()

        except Exception as e:
            print(f" [Error] Error processing group {group_key}: {e}")

    print("All processing complete!")

input_dir = r"E:\gis_data\SUHII_DEA_or_SUE\original_data"
output_dir = r"E:\gis_data\SUHII_DEA_or_SUE\merged_data"
os.makedirs(output_dir,exist_ok=True)

if __name__ == "__main__":
    process_and_mosaic_images(input_dir, output_dir)