# visualizations/evaluate_results.py
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, r2_score

# Add root to path to load models/data
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data_loader import get_processed_data

def get_aqi_category(pm25):
    """Converts PM2.5 value to Indian AQI Categories"""
    if pm25 <= 30: return "Good"
    if pm25 <= 60: return "Satisfactory"
    if pm25 <= 90: return "Moderate"
    if pm25 <= 120: return "Poor"
    if pm25 <= 250: return "Very Poor"
    return "Severe"

def run_visualizations():
    # 1. Load Data (Using the same path as your main scripts)
    DATA_PATH = '/Users/sanjanaarunkumar/Desktop/miniprojectpmk/imputation/master_pollution_MICE_imputed.csv'
    _, X_test, _, y_test, _, scaler_y = get_processed_data(DATA_PATH)
    
    # 2. Load Your Predictions (Assuming you've run main.py already)
    # For this script, we'll simulate the output from your saved Meta-Learner
    import joblib
    from tensorflow.keras.models import load_model
    from xgboost import XGBRegressor

    MODEL_DIR = '../models/'
    lstm = load_model(os.path.join(MODEL_DIR, 'air_lstm.h5'))
    xgb = XGBRegressor()
    xgb.load_model(os.path.join(MODEL_DIR, 'air_xgb.json'))
    meta = joblib.load(os.path.join(MODEL_DIR, 'meta_learner.pkl'))

    # Generate predictions
    X_test_flat = X_test.reshape(X_test.shape[0], -1)
    p_lstm = lstm.predict(X_test)
    p_xgb = xgb.predict(X_test_flat).reshape(-1, 1)
    
    meta_input = np.hstack([p_lstm, p_xgb])
    pred_scaled = meta.predict(meta_input)
    
    # Final Actual vs Predicted
    y_true = scaler_y.inverse_transform(y_test.reshape(-1, 1)).flatten()
    y_pred = scaler_y.inverse_transform(pred_scaled.reshape(-1, 1)).flatten()

    # --- VISUALIZATION 1: ACTUAL VS PREDICTED (Regression) ---
    plt.figure(figsize=(10, 6))
    plt.scatter(y_true, y_pred, alpha=0.3, color='teal')
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
    plt.xlabel('Actual PM2.5')
    plt.ylabel('Predicted PM2.5')
    plt.title('Hybrid Ensemble: Actual vs Predicted PM2.5')
    plt.savefig('visualizations/actual_vs_predicted.png')
    print("✅ Regression Plot saved.")

    # --- VISUALIZATION 2: CONFUSION MATRIX (Categorical) ---
    categories = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
    true_cat = [get_aqi_category(x) for x in y_true]
    pred_cat = [get_aqi_category(x) for x in y_pred]

    cm = confusion_matrix(true_cat, pred_cat, labels=categories)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', xticklabels=categories, yticklabels=categories, cmap='Blues')
    plt.xlabel('Predicted Category')
    plt.ylabel('Actual Category')
    plt.title('AQI Category Confusion Matrix')
    plt.savefig('visualizations/aqi_confusion_matrix.png')
    
    print("\n📊 CLASSIFICATION REPORT (AQI Severity Prediction):")
    print(classification_report(true_cat, pred_cat, labels=categories))

if __name__ == "__main__":
    run_visualizations()