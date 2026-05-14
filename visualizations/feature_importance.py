import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
import numpy as np

# 1. Load the dataset
df = pd.read_csv('/Users/sanjanaarunkumar/Desktop/miniprojectpmk/imputation/master_pollution_MICE_imputed.csv')

# 2. Create the 'Next Day' Target
# We sort by station_id to ensure we don't mix data between locations
df = df.sort_values(by=['station_id']) 
df['target_next_day'] = df.groupby('station_id')['pm2_5'].shift(-1)

# Drop rows where we don't have a 'tomorrow'
df_clean = df.dropna(subset=['target_next_day'])

# 3. CRITICAL FIX: Select ONLY numeric columns
# This automatically removes '24-hr', 'station_id', and any other text/dates
numeric_df = df_clean.select_dtypes(include=[np.number])

# Define X (features) and y (target)
# We remove 'target_next_day' from X so the model doesn't "cheat"
X = numeric_df.drop(columns=['target_next_day'])
y = numeric_df['target_next_day']

# Extra safety: Drop 'station_id' if it's still in X (it's just a label)
if 'station_id' in X.columns:
    X = X.drop(columns=['station_id'])

# 4. Train Random Forest
print(f"🚀 Training on {X.shape[1]} numeric features...")
print(f"Dropped non-numeric columns like: {df_clean.select_dtypes(exclude=[np.number]).columns.tolist()}")

rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X, y)

# 5. Plotting Feature Importance
feature_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': rf.feature_importances_
}).sort_values(by='Importance', ascending=False)

plt.figure(figsize=(12, 8))
sns.barplot(x='Importance', y='Feature', data=feature_importance, palette='viridis')
plt.title('Predictive Power: Which features determine tomorrow\'s PM2.5?', fontsize=16)
plt.tight_layout()

plt.savefig('feature_importance_fixed.png', dpi=300)
plt.show()