import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# 1. Load the full MICE-imputed dataset
df = pd.read_csv('/Users/sanjanaarunkumar/Desktop/miniprojectpmk/imputation/master_pollution_MICE_imputed.csv')

# 2. Extract numeric features 
# We include 'hour' and 'month' because their correlation with pollutants 
# reveals peak pollution times (diurnal/seasonal cycles).
numeric_cols = df.select_dtypes(include=[np.number]).columns
corr_matrix = df[numeric_cols].corr(method='pearson') # Uses standard Pearson correlation

# 3. Setup the visualization 
# We increase the DPI and figure size for a professional, sharp look
plt.figure(figsize=(16, 12), dpi=100)

# Create a mask for the upper triangle 
# (This makes it much easier to read by removing the mirror image)
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

# 4. Generate the Heatmap
heatmap = sns.heatmap(
    corr_matrix, 
    mask=mask, 
    annot=True,            # Show the actual correlation numbers
    fmt=".3f",             # Use 3 decimal places for precision
    cmap='RdYlGn_r',       # Red for positive (Bad/High), Green for negative (Good/Low)
    center=0, 
    square=True, 
    linewidths=1.5, 
    cbar_kws={"shrink": .7, "label": "Correlation Coefficient"},
    annot_kws={"size": 10, "weight": "bold"}
)

# 5. Final Formatting
plt.title('Comprehensive Pollutant & Environmental Correlation Matrix', fontsize=22, pad=20)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()

# Save a high-res version for your project report
plt.savefig('correlation_heatmap_highres.png', dpi=300)
plt.show()