import os, joblib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    r2_score, mean_absolute_error, mean_squared_error, 
    confusion_matrix, classification_report
)
from tensorflow.keras.models import load_model
from xgboost import XGBRegressor
from data_loader import get_processed_data

def get_aqi_category(value):
    if value <= 30: return 0  # Good
    if value <= 60: return 1  # Satisfactory
    if value <= 90: return 2  # Moderate
    if value <= 120: return 3 # Poor
    if value <= 250: return 4 # Very Poor
    return 5                 # Severe

def run_evaluation():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_DIR = os.path.join(BASE_DIR, 'models')
    DATA_PATH = '/Users/sanjanaarunkumar/Desktop/miniprojectpmk/imputation/master_pollution_MICE_imputed.csv'

    _, X_test, _, y_test, _, scaler_y = get_processed_data(DATA_PATH, time_steps=6)
    lstm = load_model(os.path.join(MODEL_DIR, 'air_lstm.h5'))
    xgb = XGBRegressor(); xgb.load_model(os.path.join(MODEL_DIR, 'air_xgb.json'))
    meta_learner = joblib.load(os.path.join(MODEL_DIR, 'meta_learner.pkl'))

    X_test_flat = X_test.reshape(X_test.shape[0], -1)
    meta_X_test = np.hstack([lstm.predict(X_test), xgb.predict(X_test_flat).reshape(-1, 1)])
    preds_scaled = meta_learner.predict(meta_X_test)
    
    y_true = np.expm1(scaler_y.inverse_transform(y_test.reshape(-1, 1))).flatten()
    y_pred = np.expm1(scaler_y.inverse_transform(preds_scaled.reshape(-1, 1))).flatten()

    print("\n📈 REGRESSION METRICS")
    print(f"R2 Score: {r2_score(y_true, y_pred):.4f}")
    print(f"MAE:      {mean_absolute_error(y_true, y_pred):.2f}")

    y_true_cat = [get_aqi_category(v) for v in y_true]
    y_pred_cat = [get_aqi_category(v) for v in y_pred]
    names = ['Good', 'Satisfactory', 'Moderate', 'Poor', 'Very Poor', 'Severe']
    
    print("\n🎯 CLASSIFICATION REPORT")
    print(classification_report(y_true_cat, y_pred_cat, target_names=names[:len(np.unique(y_true_cat))]))

    plt.figure(figsize=(10, 8))
    cm = confusion_matrix(y_true_cat, y_pred_cat)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=names[:cm.shape[0]], yticklabels=names[:cm.shape[0]])
    plt.savefig(os.path.join(BASE_DIR, 'confusion_matrix.png'))
    print("✅ Plot saved.")

if __name__ == "__main__":
    run_evaluation()