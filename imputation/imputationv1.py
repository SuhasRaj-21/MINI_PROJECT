import pandas as pd
import numpy as np
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

# 1. Prepare your data
# Make sure you have extracted 'hour' and 'month' as numeric columns first
df = pd.read_csv('/Users/sanjanaarunkumar/Desktop/miniprojectpmk/master_pollution_model_ready.csv') 

# Convert time and extract features so the Imputer knows "when" it is
#df['timestamp_start'] = pd.to_datetime(df['timestamp_start'])
#df['hour'] = df['timestamp_start'].dt.hour
#df['month'] = df['timestamp_start'].dt.month
#df['day_of_week'] = df['timestamp_start'].dt.dayofweek

# 2. Separate Numeric and Categorical
# We can only perform math on numeric columns
cols_to_impute = ['pm2_5', 'pm10', 'no2', 'no', 'nox', 'so2', 'co', 'o3', 
                  'rh', 'wind_speed', 'wind_direction', 'hour', 'month', 'day_of_week']

# 3. Initialize MICE (IterativeImputer)
# local machine allows us to increase max_iter for better convergence
mice_imputer = IterativeImputer(
    max_iter=20, 
    random_state=42, 
    verbose=2, # This shows you the progress in your terminal
    imputation_order='descending' # Imputes columns with most missing values last
)

# 4. Run Imputation
print("🚀 Starting MICE Imputation... This may take a few minutes.")
df_imputed_numeric = mice_imputer.fit_transform(df[cols_to_impute])

# 5. Reconstruct the Dataframe
df_final = pd.DataFrame(df_imputed_numeric, columns=cols_to_impute)

# Bring back your non-numeric ID columns
df_final['station_id'] = df['station_id'].values
df_final['source_folder'] = df['source_folder'].values
#df_final['timestamp'] = df['timestamp_start'].values

# 6. Save the High-Quality Dataset
df_final.to_csv('master_pollution_MICE_imputed.csv', index=False)
print("✅ Imputation Complete! File saved.")