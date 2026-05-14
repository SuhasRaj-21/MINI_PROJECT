import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp

# 1. Load both (The one with NaNs and the MICE-saved one)
df_raw = pd.read_csv('/Users/sanjanaarunkumar/Desktop/miniprojectpmk/master_pollution_no_imputation.csv')
df_imp = pd.read_csv('/Users/sanjanaarunkumar/Desktop/miniprojectpmk/imputation/master_pollution_MICE_imputed.csv')

pollutant = 'pm2_5' # Let's check PM2.5 first

# 2. Metric 1: Mean/Std Deviation Comparison
print(f"--- {pollutant} Statistics ---")
print(f"Original Mean: {df_raw[pollutant].mean():.2f}")
print(f"Imputed Mean:  {df_imp[pollutant].mean():.2f}")

# 3. Metric 2: KS Test
# We drop NaNs from raw for the comparison
stat, p_val = ks_2samp(df_raw[pollutant].dropna(), df_imp[pollutant])
print(f"KS Statistic: {stat:.4f}, P-Value: {p_val:.4f}")

# 4. Metric 3: Distribution Visualization
plt.figure(figsize=(10, 5))
sns.kdeplot(df_raw[pollutant], label='Original (with Gaps)', color='blue', linestyle='--')
sns.kdeplot(df_imp[pollutant], label='MICE Imputed', color='orange')
plt.title(f"Distribution Comparison: {pollutant}")
plt.legend()
plt.show()