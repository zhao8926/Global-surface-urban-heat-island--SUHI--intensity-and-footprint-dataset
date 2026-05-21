import pandas as pd
import numpy as np

uhi_file = r"E:\data_analysis\UHI\statistics20260110\Aqua_city-level_HTIA_area.csv"
### r"E:\data_analysis\UHI\statistics20260110\city-level_HTIA_area.csv"
isa_file = r"E:\data_analysis\UHI\statistics20260110\011city-level_ISA_area.csv"
out_file = r"E:\data_analysis\UHI\statistics20260110\city-level_HTIA_chu_ISA.csv"

uhi_df = pd.read_csv(uhi_file)
isa_df = pd.read_csv(isa_file)

years = [str(y) for y in range(2005,2025)]
periods = ['sd','sn','wd','wn']

ratio_df = pd.DataFrame()

for y in years:
    for p in periods:
        uhi_col = f"BRA{p}{y}"
        isa_col = f"ISA{y}"
        out_col = f"ratio{p}{y}"

        if uhi_col in uhi_df.columns and isa_col in isa_df.columns:
            uhi_values = uhi_df[uhi_col].astype(float)
            isa_values = isa_df[isa_col].astype(float)

            ratio = np.where(
                (isa_values == 0) | (uhi_values == 0) | np.isnan(isa_values) | np.isnan(uhi_values),
                0,
                uhi_values/isa_values
            )

            ratio_df[out_col] = ratio
        else:
            print(f"Warning, {uhi_col} or {isa_col} not found")

avg_ratios = {}
for p in periods:
    cols = [f"ratio{p}{y}" for y in years if f"ratio{p}{y}" in ratio_df.columns]
    if cols:
        data = ratio_df[cols].replace(0,np.nan)
        avg_ratios[f"avg_ratio{p}"] = data.mean(axis=1,skipna=True)
    else:
        print(f"Warning, could not find column for period {p}")

avg_ratio_df = pd.DataFrame(avg_ratios)
final_df = pd.concat([ratio_df,avg_ratio_df],axis=1)

final_df.to_csv(out_file,index=False,encoding='utf-8-sig')

print(f"Calculation complete. Output the data for {final_df.shape[1]} columns. Save the result to:\n{out_file}")