import os, joblib
import numpy as np
from tensorflow.keras.models import load_model
from xgboost import XGBRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import r2_score
from data_loader import get_processed_data

def run_blending_ensemble():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_DIR = os.path.join(BASE_DIR, 'models')
    DATA_PATH = '/Users/sanjanaarunkumar/Desktop/miniprojectpmk/imputation/master_pollution_MICE_imputed.csv'

    X_train, X_test, y_train, y_test, _, scaler_y = get_processed_data(DATA_PATH, time_steps=6)
    lstm = load_model(os.path.join(MODEL_DIR, 'air_lstm.h5'))
    xgb = XGBRegressor(); xgb.load_model(os.path.join(MODEL_DIR, 'air_xgb.json'))

    print("🧬 Blending Predictions...")
    X_train_flat, X_test_flat = X_train.reshape(X_train.shape[0], -1), X_test.reshape(X_test.shape[0], -1)

    meta_X_train = np.hstack([lstm.predict(X_train), xgb.predict(X_train_flat).reshape(-1, 1)])
    meta_X_test = np.hstack([lstm.predict(X_test), xgb.predict(X_test_flat).reshape(-1, 1)])

    meta_learner = GradientBoostingRegressor(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42)
    meta_learner.fit(meta_X_train, y_train.ravel())

    # CRITICAL: Save the meta-learner for the evaluator
    joblib.dump(meta_learner, os.path.join(MODEL_DIR, 'meta_learner.pkl'))
    
    preds_scaled = meta_learner.predict(meta_X_test)
    actual_y = np.expm1(scaler_y.inverse_transform(y_test.reshape(-1, 1)))
    final_preds = np.expm1(scaler_y.inverse_transform(preds_scaled.reshape(-1, 1)))

    print(f"🏆 Final Ensemble R2: {r2_score(actual_y, final_preds):.4f}")