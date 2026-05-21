# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from scipy import stats

file_path = r"E:\data_analysis\UHI\statistics20260110\FRAC_SUHIFP+ISA.xlsx"
# r"E:\data_analysis\UHI\statistics20260110\014p\ISA_sd.xlsx"
# r'E:\data_analysis\UHI\statistics20260110\city-level_HTIA_chu_ISA.csv'
# r"E:\data_analysis\UHI\statistics\029(BRA+ISA)_chu_ISA.csv" # 20_RMSE_summary.xlsx 19_R_squared_summary.xlsx
df = pd.read_excel(file_path)

# ### 1
# col_name = "ratiosd2024"
# data = df[col_name].dropna()

# ### 2
# col_idx = 3
# data = df.iloc[:, col_idx].dropna()

# ### 3
# # iloc[:, 1::2]
# data = df.iloc[:, 1::2].values.flatten()
# data = pd.Series(data).dropna()

# ### 4
# data = df.iloc[:, 0::2].values.flatten()
# data = pd.Series(data).dropna()

# ### 5
# data = df.iloc[:, [1, 2, 3]].values.flatten()
# data = pd.Series(data).dropna()

cols = [col for col in df.columns if col.startswith('ISA')]
### [col for col in df.columns if col.endswith('sd') or col.endswith('sn')]
data = df[cols].values.flatten()
data = pd.Series(data).dropna()

median = np.median(data)
mean = np.mean(data)
min_val = np.min(data)
max_val = np.max(data)
std = np.std(data, ddof=1)

# 95% CI
conf_int = stats.t.interval(
    0.95,
    len(data)-1,
    loc=mean,
    scale=stats.sem(data)
)

# Statistical results
print(f"median: {median}")
print(f"mean: {mean}")
print(f"std: {std}")
print(f"min: {min_val}")
print(f"max: {max_val}")
print(f"95% CI: {conf_int}")

# Global averages ± 95% CI
lower, upper = conf_int
ci_half = (upper - lower) / 2
print(f"Global averages: {mean:.3f} (± {ci_half:.3f}, 95% CI)")