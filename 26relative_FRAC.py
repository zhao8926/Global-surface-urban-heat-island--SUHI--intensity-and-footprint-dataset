import pandas as pd
import numpy as np
from scipy import stats

# 读取Excel
tims = ["sd","sn","wd","wn"]
tim = tims[3]
file_path = r"E:\data_analysis\UHI\statistics20260110\Aqua_FRAC_SUHIFP+ISA.xlsx"
output_file = fr"E:\data_analysis\UHI\statistics20260110\RelativeFRAC_statistics_{tim}.xlsx"
df = pd.read_excel(file_path)

years = range(2005, 2025)

results = []

for year in years:
    frac_col = f"FRAC{year}{tim}"
    isa_col = f"ISA{year}"
    
    # 检查两个列是否同时存在
    if frac_col not in df.columns or isa_col not in df.columns:
        continue

    frac_data = df[frac_col]
    isa_data = df[isa_col]

    valid_mask = frac_data.notna() & isa_data.notna()
    
    frac_valid = frac_data[valid_mask]
    isa_valid = isa_data[valid_mask]

    valid_mask2 = isa_valid != 0
    frac_valid = frac_valid[valid_mask2]
    isa_valid = isa_valid[valid_mask2]

    ratio = (frac_valid - isa_valid) / isa_valid

    data = ratio.to_numpy()
    
    if len(data) == 0:
        print(f"{year} has no valid data")
        continue

    median = np.median(data)
    mean = np.mean(data)
    min_val = np.min(data)
    max_val = np.max(data)
    std = np.std(data)
    
    # 95% CI
    lower, upper = stats.t.interval(
        0.95,
        len(data) - 1,
        loc=mean,
        scale=stats.sem(data)
    )
    
    ci_half = (upper - lower) / 2
    
    mean_std_str = f"{mean*100:.3f} ± {std*100:.3f}"
    mean_ci_str = f"{mean*100:.3f} ± {ci_half*100:.3f}"
    
    results.append({
        "Year": year,
        "(FRAC-ISA)/ISA Median": median,
        "(FRAC-ISA)/ISA Mean": mean,
        "(FRAC-ISA)/ISA Std": std,
        "Min": min_val,
        "Max": max_val,
        "95CI Lower": lower,
        "95CI Upper": upper,
        "95CI Half Width": ci_half,
        "Mean ± Std": mean_std_str,
        "Mean ± 95%CI": mean_ci_str
    })

results_df = pd.DataFrame(results)
results_df.to_excel(output_file, index=False)

print(f"Statistical results have been saved to: {output_file}")
