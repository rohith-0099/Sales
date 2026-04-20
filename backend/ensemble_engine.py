import logging

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

from logger import get_logger


logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

DEFAULT_PRODUCT_KEY = "__global__"
AGGREGATE_SCOPE = "aggregate"
PRODUCT_SCOPE = "product"


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


def _model_path(session_id, scope):
    return MODELS_DIR / f"{session_id}_{scope}_xgb.json"


def _build_scope_series(df, scope):
    scoped_df = df.copy()
    scoped_df["date"] = pd.to_datetime(scoped_df["date"])
    scoped_df = _normalize_product_keys(scoped_df)

    if scope == PRODUCT_SCOPE and scoped_df["product_key"].notna().any():
        return (
            scoped_df.groupby(["product_key", "date"], as_index=False)["sales"]
            .sum()
            .sort_values(["product_key", "date"])
            .reset_index(drop=True)
        )

    aggregate_df = (
        scoped_df.groupby("date", as_index=False)["sales"]
        .sum()
        .sort_values("date")
        .reset_index(drop=True)
    )
    aggregate_df["product_key"] = DEFAULT_PRODUCT_KEY
    return aggregate_df[["product_key", "date", "sales"]]


def engineer_features(df, calendar=None):
    """
    Engineer features for XGBoost:
    - lag_1, lag_7, lag_30 grouped within each product series
    - rolling_mean_7, rolling_mean_30 grouped within each product series
    - day_of_week, month, quarter, is_weekend
    - is_festival
    """
    featured_df = df.copy()
    featured_df["date"] = pd.to_datetime(featured_df["date"])
    featured_df = _normalize_product_keys(featured_df).sort_values(["product_key", "date"])

    grouped_sales = featured_df.groupby("product_key")["sales"]
    featured_df["lag_1"] = grouped_sales.shift(1)
    featured_df["lag_7"] = grouped_sales.shift(7)
    featured_df["lag_30"] = grouped_sales.shift(30)
    featured_df["rolling_mean_7"] = grouped_sales.transform(
        lambda series: series.shift(1).rolling(window=7, min_periods=1).mean()
    )
    featured_df["rolling_mean_30"] = grouped_sales.transform(
        lambda series: series.shift(1).rolling(window=30, min_periods=1).mean()
    )

    featured_df = featured_df.fillna(0)
    featured_df["day_of_week"] = featured_df["date"].dt.dayofweek
    featured_df["month"] = featured_df["date"].dt.month
    featured_df["quarter"] = featured_df["date"].dt.quarter
    featured_df["is_weekend"] = featured_df["day_of_week"].isin([5, 6]).astype(int)

    if calendar:
        featured_df["is_festival"] = featured_df["date"].apply(
            lambda value: 1 if calendar.is_holiday(value) else 0
        )
    else:
        featured_df["is_festival"] = 0

    return featured_df


def _train_scope_model(series_df, session_id, scope, calendar=None):
    if len(series_df) < 2:
        return None

    processed_df = engineer_features(series_df, calendar)
    if processed_df.empty:
        return None

    feature_cols = [
        "lag_1",
        "lag_7",
        "lag_30",
        "rolling_mean_7",
        "rolling_mean_30",
        "day_of_week",
        "month",
        "quarter",
        "is_weekend",
        "is_festival",
    ]

    X = processed_df[feature_cols]
    y = processed_df["sales"]

    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        random_state=42,
        objective="reg:squarederror",
    )
    model.fit(X, y)
    model.save_model(str(_model_path(session_id, scope)))

    preds = model.predict(X)
    return {
        "scope": scope,
        "rmse": float(np.sqrt(mean_squared_error(y, preds))),
        "mae": float(mean_absolute_error(y, preds)),
        "row_count": int(len(series_df)),
        "series_count": int(series_df["product_key"].nunique()),
    }


def train_user_model(df, session_id, calendar=None):
    """
    Train scope-aware XGBoost models for the uploaded dataset.

    Two models may be created:
    - aggregate: one time series built from all sales summed by date
    - product: per-product time series built from sales summed by product and date
    """
    try:
        logger.info(f"Starting model training for upload session: {session_id}")
        
        normalized_df = _normalize_product_keys(df)
        has_real_product_scope = "product_key" in df.columns and df["product_key"].notna().any()
        aggregate_series = _build_scope_series(normalized_df, AGGREGATE_SCOPE)
        product_series = _build_scope_series(normalized_df, PRODUCT_SCOPE)

        logger.debug(f"Aggregate series size: {len(aggregate_series)}, Product scope enabled: {has_real_product_scope}")

        metrics = {
            AGGREGATE_SCOPE: _train_scope_model(
                aggregate_series,
                session_id,
                AGGREGATE_SCOPE,
                calendar=calendar,
            ),
            PRODUCT_SCOPE: _train_scope_model(
                product_series,
                session_id,
                PRODUCT_SCOPE,
                calendar=calendar,
            ) if has_real_product_scope else None,
        }

        if not metrics[AGGREGATE_SCOPE] and not metrics[PRODUCT_SCOPE]:
            error_msg = "Unable to train the ensemble model because no valid aggregated series were available."
            logger.error(f"Model training failed for {session_id}: {error_msg}")
            raise ValueError(error_msg)

        logger.info(f"Model training completed successfully for session: {session_id}")
        return metrics
    except Exception as e:
        logger.error(f"Model training error for session {session_id}: {str(e)}")
        raise


def get_ensemble_weights(row_count):
    """
    Weighting logic based on available historical points in the scoped series.
    """
    if row_count < 100:
        return 0.8, 0.2
    if row_count <= 300:
        return 0.5, 0.5
    return 0.2, 0.8


def get_confidence_label(w_prophet, w_xgb):
    """
    Dominant weight >= 0.7 -> High, else Medium.
    """
    if max(w_prophet, w_xgb) >= 0.7:
        return "High"
    return "Medium"


def _prophet_only_fallback(prophet_forecast_df):
    return [
        {
            "date": row["ds"].strftime("%Y-%m-%d"),
            "predicted_sales": round(float(row["yhat"]), 2),
            "lower_bound": round(float(row["yhat_lower"]), 2),
            "upper_bound": round(float(row["yhat_upper"]), 2),
            "is_festival": False,
            "festival_name": None,
        }
        for _, row in prophet_forecast_df.iterrows()
    ]


def predict_ensemble(prophet_forecast_df, session_id, historical_df, calendar=None, scope=AGGREGATE_SCOPE):
    """
    Generate scope-consistent ensemble predictions for the forecast horizon.

    Scope determines both:
    - which session XGBoost model is loaded
    - how the historical data is aggregated before lag features are created
    """
    model_path = _model_path(session_id, scope)
    if not model_path.exists():
        return _prophet_only_fallback(prophet_forecast_df), "Medium", 0, 0

    scope_series = _build_scope_series(historical_df, scope)
    if scope_series.empty:
        return _prophet_only_fallback(prophet_forecast_df), "Medium", 0, 0

    xgb_model = XGBRegressor()
    xgb_model.load_model(str(model_path))

    w_prophet, w_xgb = get_ensemble_weights(len(scope_series))
    confidence = get_confidence_label(w_prophet, w_xgb)
    current_context = scope_series.tail(35)[["date", "sales", "product_key"]].copy()

    feature_cols = [
        "lag_1",
        "lag_7",
        "lag_30",
        "rolling_mean_7",
        "rolling_mean_30",
        "day_of_week",
        "month",
        "quarter",
        "is_weekend",
        "is_festival",
    ]

    forecast_results = []

    for _, prophet_row in prophet_forecast_df.iterrows():
        forecast_date = prophet_row["ds"]
        product_key = (
            current_context["product_key"].iloc[0]
            if not current_context.empty
            else DEFAULT_PRODUCT_KEY
        )

        def get_lag(lag_size):
            if len(current_context) >= lag_size:
                return current_context["sales"].iloc[-lag_size]
            return current_context["sales"].mean() if not current_context.empty else 0.0

        temp_df = pd.DataFrame(
            [
                {
                    "date": forecast_date,
                    "product_key": product_key,
                    "lag_1": get_lag(1),
                    "lag_7": get_lag(7),
                    "lag_30": get_lag(30),
                    "rolling_mean_7": current_context["sales"].tail(7).mean() if not current_context.empty else 0.0,
                    "rolling_mean_30": current_context["sales"].tail(30).mean() if not current_context.empty else 0.0,
                    "day_of_week": forecast_date.dayofweek,
                    "month": forecast_date.month,
                    "quarter": forecast_date.quarter,
                    "is_weekend": 1 if forecast_date.dayofweek in [5, 6] else 0,
                    "is_festival": 1 if (calendar and calendar.is_holiday(forecast_date)) else 0,
                }
            ]
        ).fillna(0)

        xgb_value = float(xgb_model.predict(temp_df[feature_cols])[0])
        prophet_value = float(prophet_row["yhat"])
        blended_value = max(0.0, (prophet_value * w_prophet) + (xgb_value * w_xgb))

        new_row = pd.DataFrame(
            [{"date": forecast_date, "sales": blended_value, "product_key": product_key}]
        )
        current_context = pd.concat([current_context, new_row], ignore_index=True).tail(35)

        festival_name = calendar.get_holiday_name(forecast_date) if (calendar and temp_df["is_festival"].iloc[0]) else None

        forecast_results.append(
            {
                "date": forecast_date.strftime("%Y-%m-%d"),
                "predicted_sales": round(blended_value, 2),
                "lower_bound": round(max(0.0, float(prophet_row["yhat_lower"])), 2),
                "upper_bound": round(max(0.0, float(prophet_row["yhat_upper"])), 2),
                "is_festival": bool(temp_df["is_festival"].iloc[0]),
                "festival_name": festival_name,
            }
        )

    return forecast_results, confidence, w_prophet, w_xgb
