#-*-coding:utf-8-*-
import pandas as pd
import numpy as np

xlsx = r'E:\data_analysis\UHI\statistics20260110\FRAC_SUHIFP+ISA.xlsx'
tims = ['sd','sn','wd','wn']
tim = tims[3]
out_xlsx = fr'E:\data_analysis\UHI\statistics20260110\FRAC_statistics_{tim}.xlsx'
df = pd.read_excel(xlsx)

target_cols = df.filter(regex=fr'^FRAC\d+{tim}$').columns

stats_df = df[target_cols].agg(['mean', 'std', 'min', 'max']).transpose()

stats_df['Year'] = stats_df.index.str.extract(fr'FRAC(\d+){tim}', expand=False)

cols = ['Year'] + [c for c in stats_df.columns if c != 'Year']
final_result = stats_df[cols].reset_index(drop=True)

print("--- Final results ---")
print(final_result)

final_result.to_excel(out_xlsx,index=False)