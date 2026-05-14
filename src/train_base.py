import os
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers.legacy import Adam 
from xgboost import XGBRegressor
from data_loader import get_processed_data

def train_specialists():
    DATA_PATH = '/Users/sanjanaarunkumar/Desktop/miniprojectpmk/imputation/master_pollution_MICE_imputed.csv'
    X_train, X_test, y_train, y_test, _, _ = get_processed_data(DATA_PATH, time_steps=6)

    model = Sequential([
        Input(shape=(X_train.shape[1], X_train.shape[2])),
        LSTM(128, return_sequences=True), 
        Dropout(0.3),
        LSTM(64), 
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dense(1)
    ])
    
    model.compile(optimizer=Adam(learning_rate=0.0005), loss='mse')
    early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)

    print("🚀 Training High-Capacity Stacked LSTM...")
    model.fit(X_train, y_train, epochs=100, batch_size=64, 
              validation_data=(X_test, y_test), callbacks=[early_stop])

    print("🌲 Training Precision XGBoost...")
    X_train_flat = X_train.reshape(X_train.shape[0], -1)
    xgb = XGBRegressor(n_estimators=1500, max_depth=8, learning_rate=0.02, gamma=0.1, subsample=0.8, colsample_bytree=0.8, n_jobs=-1)
    xgb.fit(X_train_flat, y_train)

    model_dir = 'models'
    model.save(os.path.join(model_dir, 'air_lstm.h5'))
    xgb.save_model(os.path.join(model_dir, 'air_xgb.json'))
    print("✅ Base models optimized.")