import os, joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder

def get_processed_data(file_path, time_steps=6):
    df = pd.read_csv(file_path)
    
    le = LabelEncoder()
    df['station_id'] = le.fit_transform(df['station_id'])
    
    df = df.sort_values(by=['station_id', 'month', 'day_of_week', 'hour'])

    df['pm2_5'] = df['pm2_5'].clip(lower=0)
    df['pm2_5_log'] = np.log1p(df['pm2_5'])
    
    # Advanced Features
    df['pm_ratio'] = df['pm2_5'] / (df['pm10'] + 1)
    df['stagnation'] = df['co'] * (1 / (df['wind_speed'] + 0.1))
    df['pm25_rolling_mean_3h'] = df.groupby('station_id')['pm2_5_log'].transform(lambda x: x.rolling(3).mean()).bfill()
    
    df['lag_1'] = df.groupby('station_id')['pm2_5_log'].shift(1).bfill()
    df['lag_24'] = df.groupby('station_id')['pm2_5_log'].shift(24).bfill()
    
    df['hour_sin'] = np.sin(2 * np.pi * df['hour']/24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour']/24)

    features = ['pm2_5_log', 'pm10', 'co', 'wind_speed', 'hour_sin', 'hour_cos', 
                'lag_1', 'lag_24', 'pm_ratio', 'stagnation', 'pm25_rolling_mean_3h']
    
    scaler_x = StandardScaler()
    scaler_y = StandardScaler()
    
    df_scaled_x = scaler_x.fit_transform(df[features]).astype(np.float32)
    df_scaled_y = scaler_y.fit_transform(df[['pm2_5_log']]).astype(np.float32)
    
    X_list, y_list = [], []
    for _, station_df in df.groupby('station_id'):
        if len(station_df) <= time_steps: continue
        pos = df.index.get_indexer(station_df.index)
        s_x, s_y = df_scaled_x[pos], df_scaled_y[pos]
        for i in range(len(s_x) - time_steps):
            X_list.append(s_x[i : i + time_steps])
            y_list.append(s_y[i + time_steps])

    X_seq, y_seq = np.array(X_list), np.array(y_list)

    # Shuffling for generalizability
    indices = np.arange(X_seq.shape[0])
    np.random.seed(42)
    np.random.shuffle(indices)
    X_seq, y_seq = X_seq[indices], y_seq[indices]

    split = int(len(X_seq) * 0.8)
    
    model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(scaler_x, os.path.join(model_dir, 'scaler_x.pkl'))
    joblib.dump(scaler_y, os.path.join(model_dir, 'scaler_y.pkl'))

    return X_seq[:split], X_seq[split:], y_seq[:split], y_seq[split:], scaler_x, scaler_y