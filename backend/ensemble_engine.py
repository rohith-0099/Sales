import os
import json
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)
DEFAULT_PRODUCT_KEY = "__global__"


def _normalize_product_keys(df):
    normalized = df.copy()
    normalized["product_key"] = normalized.get("product_key", DEFAULT_PRODUCT_KEY)
    normalized["product_key"] = (
        normalized["product_key"]
        .fillna(DEFAULT_PRODUCT_KEY)
        .astype("string")
        .replace("", DEFAULT_PRODUCT_KEY)
    )
    return normalized

def engineer_features(df, calendar=None):
    """
    Engineer features for XGBoost:
    - lag_1, lag_7, lag_30 (grouped by product_name)
    - rolling_mean_7, rolling_mean_30
    - day_of_week, month, quarter, is_weekend
    - is_festival
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = _normalize_product_keys(df).sort_values(['product_key', 'date'])

    grouped_sales = df.groupby('product_key')['sales']
    df['lag_1'] = grouped_sales.shift(1)
    df['lag_7'] = grouped_sales.shift(7)
    df['lag_30'] = grouped_sales.shift(30)
    df['rolling_mean_7'] = grouped_sales.shift(1).rolling(window=7).mean().reset_index(level=0, drop=True)
    df['rolling_mean_30'] = grouped_sales.shift(1).rolling(window=30).mean().reset_index(level=0, drop=True)

    # Fill NaNs created by shifting
    df = df.fillna(0)

    # Date features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

    # Festival feature
    if calendar:
        df['is_festival'] = df['date'].apply(lambda x: 1 if calendar.is_holiday(x) else 0)
    else:
        df['is_festival'] = 0

    return df

def train_user_model(df, session_id, calendar=None):
    """
    Trains XGBoost on user's data and saves it.
    """
    processed_df = engineer_features(df, calendar)
    if processed_df.empty:
        raise ValueError("Unable to train the ensemble model because no valid rows were available.")
    
    # Feature columns for training
    feature_cols = [
        'lag_1', 'lag_7', 'lag_30', 
        'rolling_mean_7', 'rolling_mean_30', 
        'day_of_week', 'month', 'quarter', 
        'is_weekend', 'is_festival'
    ]
    
    X = processed_df[feature_cols]
    y = processed_df['sales']
    
    model = XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=6, random_state=42)
    model.fit(X, y)
    
    # Save model
    model_path = MODELS_DIR / f"{session_id}_xgb.json"
    model.save_model(str(model_path))
    
    # Calculate initial metrics on training data for confidence
    preds = model.predict(X)
    metrics = {
        "rmse": float(np.sqrt(mean_squared_error(y, preds))),
        "mae": float(mean_absolute_error(y, preds)),
        "row_count": len(df)
    }
    
    return metrics

def get_ensemble_weights(row_count):
    """
    Weighting logic based on row count.
    """
    if row_count < 100:
        return 0.8, 0.2
    elif 100 <= row_count <= 300:
        return 0.5, 0.5
    else:
        return 0.2, 0.8

def get_confidence_label(w_prophet, w_xgb):
    """
    Dominant weight >= 0.7 -> High, else Medium.
    """
    if max(w_prophet, w_xgb) >= 0.7:
        return "High 🟢"
    return "Medium 🟡"

def predict_ensemble(prophet_forecast_df, session_id, historical_df, calendar=None):
    """
    Generates ensemble predictions for the forecast horizon.
    - prophet_forecast_df: DF from Prophet containing 'ds' and 'yhat'
    - session_id: to load the XGB model
    - historical_df: used to get the tail for lag features
    """
    model_path = MODELS_DIR / f"{session_id}_xgb.json"
    if not model_path.exists():
        # Fallback to pure Prophet if XGB model doesn't exist
        return [{
            "date": row['ds'].strftime('%Y-%m-%d'),
            "predicted_sales": float(row['yhat']),
            "lower_bound": float(row['yhat_lower']),
            "upper_bound": float(row['yhat_upper'])
        } for _, row in prophet_forecast_df.iterrows()], "Medium 🟡", 0, 0

    xgb_model = XGBRegressor()
    xgb_model.load_model(str(model_path))
    
    # Prepare data for XGBoost prediction
    # We need to bridge historical data with future dates to compute lags
    # For simplicity, we'll use the last known values as baseline for future lags if we don't have a full recursive predictor
    # But the requirement asks for lag_1, lag_7, lag_30.
    
    forecast_results = []
    
    # Get last known rows to bootstrap lags
    historical_df = _normalize_product_keys(historical_df)
    last_rows = historical_df.tail(35).copy() # Enough for lag 30
    
    # Ensemble weights
    w_prophet, w_xgb = get_ensemble_weights(len(historical_df))
    confidence = get_confidence_label(w_prophet, w_xgb)

    # Iterate through the forecast dates
    current_context = last_rows[['date', 'sales', 'product_key']].copy()
    
    feature_cols = [
        'lag_1', 'lag_7', 'lag_30', 
        'rolling_mean_7', 'rolling_mean_30', 
        'day_of_week', 'month', 'quarter', 
        'is_weekend', 'is_festival'
    ]

    for _, p_row in prophet_forecast_df.iterrows():
        f_date = p_row['ds']
        
        # Build features for this specific date
        temp_df = pd.DataFrame([{
            'date': f_date,
            'product_key': current_context['product_key'].iloc[0] if not current_context.empty else DEFAULT_PRODUCT_KEY
        }])
        
        # Merge with context to compute lags
        # Actually, it's easier to just pick from the tail of current_context
        def get_lag(n):
            if len(current_context) >= n:
                return current_context['sales'].iloc[-n]
            return current_context['sales'].mean() if not current_context.empty else 0

        temp_df['lag_1'] = get_lag(1)
        temp_df['lag_7'] = get_lag(7)
        temp_df['lag_30'] = get_lag(30)
        temp_df['rolling_mean_7'] = current_context['sales'].tail(7).mean() if not current_context.empty else 0
        temp_df['rolling_mean_30'] = current_context['sales'].tail(30).mean() if not current_context.empty else 0
        
        # Fill NaNs
        temp_df = temp_df.fillna(0)
        
        # Temporal features
        temp_df['day_of_week'] = f_date.dayofweek
        temp_df['month'] = f_date.month
        temp_df['quarter'] = f_date.quarter
        temp_df['is_weekend'] = 1 if f_date.dayofweek in [5, 6] else 0
        
        is_fest = 1 if (calendar and calendar.is_holiday(f_date)) else 0
        fest_name = calendar.get_holiday_name(f_date) if (calendar and is_fest) else None
        temp_df['is_festival'] = is_fest
        
        # XGB Predict
        xgb_val = float(xgb_model.predict(temp_df[feature_cols])[0])
        prophet_val = float(p_row['yhat'])
        
        # Ensemble combine
        ensemble_val = (prophet_val * w_prophet) + (xgb_val * w_xgb)
        ensemble_val = max(0, ensemble_val) # No negative sales
        
        # Update context for next step (recursive-like)
        new_row = pd.DataFrame([{'date': f_date, 'sales': ensemble_val, 'product_key': temp_df['product_key'].iloc[0]}])
        current_context = pd.concat([current_context, new_row]).tail(35)
        
        forecast_results.append({
            "date": f_date.strftime('%Y-%m-%d'),
            "predicted_sales": round(ensemble_val, 2),
            "lower_bound": round(max(0, p_row['yhat_lower']), 2), # Use prophet bounds for simplicity
            "upper_bound": round(max(0, p_row['yhat_upper']), 2),
            "is_festival": bool(is_fest),
            "festival_name": fest_name
        })
        
    return forecast_results, confidence, w_prophet, w_xgb
