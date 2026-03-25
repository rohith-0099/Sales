"""
Production-oriented Flask backend for retail sales forecasting and analysis.
"""

from __future__ import annotations

import json
import os
import pickle
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from .ai_engine import get_ai_insight
    from .analytics_engine import (
        UploadStore,
        analyze_dataset,
        generate_forecast,
        prepare_uploaded_dataframe,
        read_uploaded_file,
        search_products,
        filter_dataset_by_product,
    )
    from .market_holidays import get_calendar
    from . import ensemble_engine
except ImportError:
    from ai_engine import get_ai_insight
    from analytics_engine import (
        UploadStore,
        analyze_dataset,
        generate_forecast,
        prepare_uploaded_dataframe,
        read_uploaded_file,
        search_products,
        filter_dataset_by_product,
    )
    from market_holidays import get_calendar
    import ensemble_engine


BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
CORS(app)

model = None
encoders = {}
feature_columns = None
model_type = "unloaded"
upload_store = UploadStore(
    ttl_minutes=int(os.getenv("UPLOAD_TTL_MINUTES", "90")),
    max_items=int(os.getenv("MAX_UPLOAD_SESSIONS", "25")),
)

DEFAULT_GEMINI_MODEL_CANDIDATES = [
    "models/gemini-2.0-flash",
    "models/gemini-flash-latest",
    "models/gemini-2.5-flash",
]


def load_model() -> bool:
    global model, encoders, feature_columns, model_type

    integrated_model_path = MODELS_DIR / "integrated_sales_model.pkl"
    original_model_path = MODELS_DIR / "sales_model.pkl"

    try:
        with integrated_model_path.open("rb") as model_file:
            saved_data = pickle.load(model_file)
        model = saved_data["model"]
        encoders = saved_data.get("encoders", {})
        feature_columns = saved_data["feature_columns"]
        model_type = "integrated"
        print("[OK] Integrated model loaded successfully.")
        print(f"   Features: {len(feature_columns)}")
        print(f"   Test R2: {saved_data['performance']['test_r2']:.4f}")
        print(f"   Datasets: {', '.join(saved_data['training_info']['datasets_used'])}")
        return True
    except FileNotFoundError:
        print("[WARNING] Integrated model not found, trying original model.")

    try:
        with original_model_path.open("rb") as model_file:
            saved_data = pickle.load(model_file)
        model = saved_data["model"]
        encoders = saved_data.get("encoders", {})
        feature_columns = saved_data["feature_columns"]
        model_type = "original"
        print("[OK] Original model loaded successfully.")
        return True
    except FileNotFoundError:
        print("[ERROR] No trained model was found in backend/models.")
        return False


def ensure_model_loaded() -> bool:
    if model is not None:
        return True
    return load_model()


def preprocess_input(data: dict) -> pd.DataFrame:
    df = pd.DataFrame([data])

    fat_content_mapping = {
        "low fat": "Low Fat",
        "LF": "Low Fat",
        "reg": "Regular",
        "Low Fat": "Low Fat",
        "Regular": "Regular",
    }
    df["Item_Fat_Content"] = df["Item_Fat_Content"].map(fat_content_mapping)

    categorical_columns = [
        "Item_Identifier",
        "Item_Fat_Content",
        "Item_Type",
        "Outlet_Identifier",
        "Outlet_Size",
        "Outlet_Location_Type",
        "Outlet_Type",
    ]

    for column in categorical_columns:
        if column in encoders:
            try:
                df[column] = encoders[column].transform(df[column])
            except ValueError:
                df[column] = 0

    return df[feature_columns]


def _resolve_item_from_payload(payload: dict) -> dict:
    upload_id = payload.get("upload_id")
    if upload_id:
        item = upload_store.get(upload_id)
        if not item:
            raise LookupError("Upload session not found or expired. Please upload the dataset again.")
        return item

    historical_data = payload.get("historical_data")
    if historical_data is None:
        raise ValueError("Request must include `upload_id` or `historical_data`.")

    prepared = prepare_uploaded_dataframe(pd.DataFrame(historical_data))
    return {
        "data": prepared["data"],
        "metadata": prepared["metadata"],
    }


def _get_json_payload() -> dict:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValueError("Request body must be valid JSON.")
    return payload


def _build_ai_prompt(language: str, product_name: str, context: dict | None, summary: str) -> str:
    context_text = json.dumps(context or {}, ensure_ascii=False, indent=2)
    return f"""
You are a senior retail revenue strategist.
Analyze the uploaded sales dataset and explain the business situation clearly.

Context scope: {product_name}
Required response language: {language}

Structured analytics context:
{context_text}

Fallback summary:
{summary}

Write the response with these exact sections:
## Current Sales Health
## Future Outlook
## Product Focus
## Actions to Improve Sales

Rules:
- Respond only in {language}.
- Use clear markdown headings and flat bullet lists.
- Ground every point in the provided metrics.
- If the data granularity is monthly or yearly, mention that day-level signals may be hidden.
- Under Actions to Improve Sales, provide exactly 3 concrete actions.
"""


def _format_metric(value, suffix: str = "") -> str:
    if value is None:
        return "0"
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return str(value)

    if suffix == "%":
        return f"{numeric_value:+.2f}%"
    if numeric_value.is_integer():
        return f"{int(numeric_value)}{suffix}"
    return f"{numeric_value:.2f}{suffix}"


@app.route("/")
def home():
    return jsonify(
        {
            "message": "Retail sales analytics API is running.",
            "version": "3.0",
            "endpoints": {
                "predict": "/api/predict",
                "batch_predict": "/api/batch-predict",
                "upload_csv": "/api/upload-csv",
                "product_search": "/api/products/search",
                "forecast": "/api/forecast",
                "pattern_analysis": "/api/analyze-patterns",
                "festival_impact": "/api/festival-impact",
                "ai_insights": "/api/ai-insights",
                "model_info": "/api/model-info",
                "health": "/api/health",
            },
        }
    )


@app.route("/api/health", methods=["GET"])
def health_check():
    if not ensure_model_loaded():
        return (
            jsonify(
                {
                    "status": "error",
                    "model_loaded": False,
                    "message": "Prediction model is not loaded.",
                }
            ),
            500,
        )

    return jsonify(
        {
            "status": "healthy",
            "model_loaded": True,
            "model_type": model_type,
            "active_upload_sessions": upload_store.count(),
        }
    )


@app.route("/api/predict", methods=["POST"])
def predict_sales():
    try:
        data = _get_json_payload()

        required_fields = [
            "Item_Identifier",
            "Item_Weight",
            "Item_Fat_Content",
            "Item_Visibility",
            "Item_Type",
            "Item_MRP",
            "Outlet_Identifier",
            "Outlet_Establishment_Year",
            "Outlet_Size",
            "Outlet_Location_Type",
            "Outlet_Type",
        ]

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Missing required fields: {', '.join(missing_fields)}",
                    }
                ),
                400,
            )

        if not ensure_model_loaded():
            return jsonify({"success": False, "error": "Model not loaded"}), 500
        
        prediction = model.predict(preprocess_input(data))[0]
        return jsonify(
            {
                "success": True,
                "predicted_sales": round(float(prediction), 2),
                "input_data": data,
            }
        )
    except Exception as error:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(error),
                    "message": "Prediction failed.",
                }
            ),
            500,
        )


@app.route("/api/batch-predict", methods=["POST"])
def batch_predict():
    try:
        payload = _get_json_payload()
        items = payload.get("items", [])
        if not items:
            return jsonify({"success": False, "error": "No items were provided."}), 400
        if not ensure_model_loaded():
            return jsonify({"success": False, "error": "Model not loaded"}), 500

        predictions = []
        for item in items:
            prediction = model.predict(preprocess_input(item))[0]
            predictions.append(
                {
                    "item": item.get("Item_Identifier", "Unknown"),
                    "predicted_sales": round(float(prediction), 2),
                }
            )

        return jsonify(
            {
                "success": True,
                "predictions": predictions,
                "total_items": len(predictions),
            }
        )
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500


@app.route("/api/upload-csv", methods=["POST"])
def upload_csv():
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file was uploaded."}), 400

        file = request.files["file"]
        if not file or not file.filename:
            return jsonify({"success": False, "error": "Uploaded file is empty."}), 400

        raw_df = read_uploaded_file(file)
        prepared = prepare_uploaded_dataframe(raw_df)
        upload_id = upload_store.save(prepared["data"], prepared["metadata"])
        metadata = prepared["metadata"]

        # IMPROVEMENT 2: Train per-user XGBoost model
        try:
            country_code = request.form.get("country_code", "IN")
            festival_calendar = get_calendar(country_code)
            training_metrics = ensemble_engine.train_user_model(
                prepared["data"], 
                upload_id, 
                calendar=festival_calendar
            )
            metadata["training_metrics"] = training_metrics
        except Exception as e:
            print(f"[XGBoost Training Error] {e}")

        return jsonify(
            {
                "success": True,
                "upload_id": upload_id,
                "file_name": file.filename,
                "stats": metadata["stats"],
                "preview": metadata["preview"],
                "columns": metadata["columns"],
                "granularity": metadata["granularity"],
                "product_column": metadata["product_column"],
                "product_primary_column": metadata["product_primary_column"],
                "product_lookup_columns": metadata["product_lookup_columns"],
                "sample_products": metadata["sample_products"],
                "message": "File uploaded, normalized, and model trained successfully.",
            }
        )
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500


@app.route("/api/products/search", methods=["GET"])
def product_search():
    upload_id = request.args.get("upload_id", "")
    query = request.args.get("q", "")
    limit = int(request.args.get("limit", "10"))

    item = upload_store.get(upload_id)
    if not item:
        return jsonify({"success": False, "error": "Upload session not found or expired."}), 404

    matches = search_products(item, query, limit=max(1, min(limit, 25)))
    return jsonify({"success": True, "matches": matches})


@app.route("/api/forecast", methods=["POST"])
def forecast():
    try:
        payload = _get_json_payload()
        item = _resolve_item_from_payload(payload)
        country_code = payload.get("country_code", "IN")
        festival_calendar = get_calendar(country_code)
        
        # Original Prophet forecast
        result = generate_forecast(
            item,
            festival_calendar,
            selected_product=payload.get("selected_product"),
            forecast_periods=payload.get("forecast_periods"),
        )
        
        # IMPROVEMENT 1: Ensemble Logic (Prophet + XGBoost)
        upload_id = payload.get("upload_id")
        if upload_id:
            try:
                # Prepare prophet DF for ensemble
                # result['forecast'] contains records, we need a DF
                prophet_forecast_df = pd.DataFrame(result['forecast'])
                prophet_forecast_df['ds'] = pd.to_datetime(prophet_forecast_df['date'])
                prophet_forecast_df['yhat'] = prophet_forecast_df['predicted_sales']
                prophet_forecast_df['yhat_lower'] = prophet_forecast_df['lower_bound']
                prophet_forecast_df['yhat_upper'] = prophet_forecast_df['upper_bound']
                
                # Filter item data for the selected product if needed
                filtered_df, _ = filter_dataset_by_product(item, payload.get("selected_product"))
                
                ensemble_forecast, confidence, w_prophet, w_xgb = ensemble_engine.predict_ensemble(
                    prophet_forecast_df,
                    upload_id,
                    filtered_df,
                    calendar=festival_calendar
                )
                
                # Update result with ensemble predictions and metadata
                result['forecast'] = ensemble_forecast
                result['confidence'] = confidence
                result['ensemble_weights'] = {"prophet": w_prophet, "xgb": w_xgb}
                
                # Calculate metrics (placeholders if not already calculated during training)
                if 'training_metrics' in item['metadata']:
                    result['metrics'] = {
                        "rmse": item['metadata']['training_metrics'].get('rmse'),
                        "mae": item['metadata']['training_metrics'].get('mae'),
                        "row_count": item['metadata']['training_metrics'].get('row_count')
                    }
                else:
                    result['metrics'] = {
                        "row_count": len(filtered_df)
                    }
            except Exception as e:
                print(f"[Ensemble Error] {e}")
                result['ensemble_error'] = str(e)

        return jsonify({"success": True, **result})
    except LookupError as error:
        return jsonify({"success": False, "error": str(error)}), 404
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 400
    except Exception as error:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(error),
                    "message": "Forecast generation failed.",
                }
            ),
            500,
        )


@app.route("/api/analyze-patterns", methods=["POST"])
def analyze_patterns():
    try:
        payload = _get_json_payload()
        item = _resolve_item_from_payload(payload)
        country_code = payload.get("country_code", "IN")
        festival_calendar = get_calendar(country_code)
        patterns = analyze_dataset(
            item,
            festival_calendar,
            selected_product=payload.get("selected_product"),
        )
        return jsonify({"success": True, "patterns": patterns})
    except LookupError as error:
        return jsonify({"success": False, "error": str(error)}), 404
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500


@app.route("/api/festival-impact", methods=["GET"])
def festival_impact():
    try:
        upcoming_festivals = []
        today = pd.Timestamp.now().normalize()
        country_code = request.args.get("country_code", "IN")
        festival_calendar = get_calendar(country_code)

        for day_offset in range(60):
            current_date = today + pd.Timedelta(days=day_offset)
            if festival_calendar.is_holiday(current_date):
                holiday_name = festival_calendar.get_holiday_name(current_date)
                upcoming_festivals.append(
                    {
                        "date": current_date.date().isoformat(),
                        "festival": holiday_name,
                        "category": festival_calendar.get_festival_category(holiday_name),
                        "impact_score": round(
                            festival_calendar.get_festival_impact_score(current_date), 2
                        ),
                        "days_from_now": day_offset,
                    }
                )

        return jsonify({"success": True, "upcoming_festivals": upcoming_festivals})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500


@app.route("/api/holidays", methods=["GET"])
def get_holidays():
    """
    Expose festival data via GET /holidays?market=India&start=2026-01-01&end=2026-12-31 endpoint
    """
    try:
        market = request.args.get("market", "IN")
        start_date = request.args.get("start")
        end_date = request.args.get("end")

        if not start_date or not end_date:
            return jsonify({"success": False, "error": "Start and end dates are required."}), 400

        calendar = get_calendar(market)
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        holidays_list = []
        current = start
        while current <= end:
            if calendar.is_holiday(current):
                name = calendar.get_holiday_name(current)
                holidays_list.append({
                    "date": current.strftime('%Y-%m-%d'),
                    "festival": name,
                    "category": calendar.get_festival_category(name)
                })
            current += pd.Timedelta(days=1)

        return jsonify({"success": True, "holidays": holidays_list})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/model-info", methods=["GET"])
def model_info():
    if not ensure_model_loaded():
        return jsonify({"success": False, "message": "Model not loaded."}), 500

    return jsonify(
        {
            "success": True,
            "model_type": model_type,
            "features": feature_columns,
            "num_features": len(feature_columns),
            "encoders_loaded": list(encoders.keys()),
            "festival_support": True,
        }
    )


@app.route("/api/ai-insights", methods=["POST"])
def ai_insights():
    try:
        data = _get_json_payload()
        upload_id = data.get("upload_id")
        item = upload_store.get(upload_id) if upload_id else None
        context = data.get("context") or {}
        analysis_context = context.get("analysis") or {}
        forecast_context = context.get("forecast") or {}
        analysis_summary = analysis_context.get("summary") or {}
        forecast_summary = forecast_context.get("summary") or {}
        
        sales_summary = {
            "scope": data.get("product_name") or "All products",
            "total_sales": data.get("total_sales")
            or analysis_summary.get("total_sales")
            or data.get("summary", "N/A"),
            "trend": data.get("trend")
            or analysis_summary.get("trend_direction")
            or "stable",
            "market": data.get("market") or data.get("country_code", "India"),
            "festival": data.get("festival") or "None",
            "growth_rate": data.get("growth_rate")
            or analysis_summary.get("growth_pct")
            or "N/A",
            "granularity": data.get("granularity")
            or analysis_summary.get("granularity")
            or "Daily",
            "current_run_rate": analysis_summary.get("current_run_rate", "N/A"),
            "latest_sales": analysis_summary.get("latest_sales", "N/A"),
            "forecast_direction": forecast_summary.get("projected_direction", "stable"),
            "forecast_total": forecast_summary.get("cumulative_predicted_sales", "N/A"),
        }
        
        selected_product_stats = analysis_context.get("selected_product_stats")
        top_products = analysis_context.get("top_products") or []
        top_festivals = analysis_context.get("top_festivals") or []

        if sales_summary["festival"] == "None" and top_festivals:
            sales_summary["festival"] = ", ".join(
                [str(festival.get("festival")) for festival in top_festivals[:2] if festival.get("festival")]
            ) or "None"

        if selected_product_stats:
            sales_summary["product_stats"] = [selected_product_stats]
        elif top_products:
            sales_summary["product_stats"] = top_products[:5]
        elif item and "metadata" in item:
            product_summary = item["metadata"].get("product_summary")
            if product_summary is not None and not product_summary.empty:
                total_sales = float(product_summary["total_sales"].sum()) or 0.0
                sales_summary["product_stats"] = []
                for _, row in product_summary.head(5).iterrows():
                    share = (float(row["total_sales"]) / total_sales * 100) if total_sales else 0.0
                    sales_summary["product_stats"].append(
                        {
                            "product": row["product_key"],
                            "total_sales": round(float(row["total_sales"]), 2),
                            "share_of_catalog_sales_pct": round(share, 2),
                        }
                    )

        if item and "metadata" in item:
            sales_summary["granularity"] = item["metadata"].get(
                "granularity",
                sales_summary["granularity"],
            )
        
        language = data.get("language", "English")
        
        # Call the new Groq-powered engine with rich context
        insight = get_ai_insight(sales_summary, language)
        
        return jsonify({
            "success": True, 
            "insights": insight,
            "model": "groq-llama-3.3-70b"
        })
    except Exception as error:
        return jsonify({
            "success": False, 
            "error": str(error),
            "message": "AI insight generation failed."
        }), 500


if __name__ == "__main__":
    if ensure_model_loaded():
        print("[INFO] Starting Flask server on http://127.0.0.1:5000")
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        print("[WARNING] Train a model before starting the API.")
