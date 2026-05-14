import pandas as pd

df = pd.read_csv('/Users/sanjanaarunkumar/Desktop/miniprojectpmk/imputation/master_pollution_MICE_imputed.csv')

print(df[['hour', 'month', 'day_of_week']].nunique())