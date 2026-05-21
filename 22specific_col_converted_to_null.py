#-*-coding:utf-8-*-
import pandas as pd
import numpy as np
import os

file_path = r"E:\data_analysis\UHI\statistics20260110\012city-level_HTIA_chu_ISA.csv"
output_dir = r"E:\data_analysis\UHI\statistics20260110\014按p分类结果"
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(file_path)

ps = ['sd', 'sn', 'wd', 'wn']

for p in ps:
    new_columns = []
    for y in range(2005, 2025):
        column_name = f"ratio{p}{y}"
        if column_name in df.columns:
            # 替换0为NaN
            df[column_name] = df[column_name].replace(0, np.nan)
            new_columns.append(column_name)
            print(f"{column_name} column null values ​​are converted to NaN")
    df_p = df[new_columns].copy()
    # 保存为Excel文件
    out_file = os.path.join(output_dir, f"ISA_{p}.xlsx")
    df_p.to_excel(out_file, index=False)
    print(f"The data corresponding to {p} has been saved as {out_file}")
