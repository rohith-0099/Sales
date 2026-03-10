"""
Production-oriented Flask backend for retail sales forecasting and analysis.
"""

from __future__ import annotations

import json
import os
import pickle
from functools import lru_cache
from pathlib import Path

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from analytics_engine import (
    UploadStore,
    analyze_dataset,
    generate_forecast,
    prepare_uploaded_dataframe,
    read_uploaded_file,
    search_products,
)
from indian_holidays import IndianFestivalCalendar


BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
CORS(app)

model = None
encoders = {}
feature_columns = None
model_type = "unloaded"
festival_calendar = IndianFestivalCalendar()
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


@lru_cache(maxsize=1)
def _list_supported_gemini_models() -> tuple[str, ...]:
    supported_models = []
    for model in genai.list_models():
        methods = getattr(model, "supported_generation_methods", []) or []
        if "generateContent" in methods:
            supported_models.append(model.name)
    return tuple(supported_models)


def _resolve_gemini_model_name() -> str:
    configured_name = os.getenv("GEMINI_MODEL", "").strip()
    candidates = []

    if configured_name:
        candidates.append(configured_name)
        if not configured_name.startswith("models/"):
            candidates.append(f"models/{configured_name}")

    candidates.extend(DEFAULT_GEMINI_MODEL_CANDIDATES)
    available_models = set(_list_supported_gemini_models())

    for candidate in candidates:
        if candidate in available_models:
            return candidate

    raise RuntimeError(
        "No supported Gemini text model was found for this API key. "
        "Set GEMINI_MODEL in backend/.env to one of the models returned by list_models()."
    )


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


def _build_fallback_ai_insights(
    language: str,
    product_name: str,
    context: dict | None,
    failure_reason: str,
) -> str:
    dataset = (context or {}).get("dataset", {})
    analysis = (context or {}).get("analysis", {})
    forecast = (context or {}).get("forecast", {})
    summary = analysis.get("summary", {})
    festival_impact = analysis.get("festival_impact", {})
    selected_product = analysis.get("selected_product_stats")
    top_products = analysis.get("top_products") or []
    forecast_summary = forecast.get("summary", {})
    forecast_periods = forecast.get("periods")
    forecast_unit = forecast.get("unit", "periods")

    product_focus_lines = []
    if selected_product:
        product_focus_lines.append(
            f"- {selected_product['product']} is ranked #{selected_product['rank']} and contributes "
            f"{_format_metric(selected_product['share_of_catalog_sales_pct'], '%')} of catalog sales."
        )
    elif top_products:
        lead_product = top_products[0]
        product_focus_lines.append(
            f"- {lead_product['product']} is the strongest product in the current upload with total sales of "
            f"{_format_metric(lead_product['total_sales'])}."
        )
        if len(top_products) > 1:
            second_product = top_products[1]
            product_focus_lines.append(
                f"- {second_product['product']} is the next strongest product and should be monitored as a secondary growth bet."
            )
    else:
        product_focus_lines.append("- Product-level ranking is not available for this dataset.")

    actions = []
    if festival_impact.get("uplift_percentage", 0) > 5:
        actions.append(
            "- Increase inventory and marketing spend ahead of strong festival periods because holiday sales are outperforming normal days."
        )
    else:
        actions.append(
            "- Use targeted promotions during weaker periods because festival uplift is limited in the current data."
        )

    if summary.get("trend_direction") == "downward":
        actions.append(
            "- Investigate pricing, assortment, and stock availability immediately because the recent run rate is below the previous baseline."
        )
    else:
        actions.append(
            "- Double down on channels and products driving the current momentum while the trend remains stable or improving."
        )

    if selected_product:
        actions.append(
            f"- Create a focused campaign for {selected_product['product']} and track whether its share of sales rises above "
            f"{_format_metric(selected_product['share_of_catalog_sales_pct'], '%')}."
        )
    elif top_products:
        actions.append(
            f"- Build bundles, upsell flows, or visibility boosts around {top_products[0]['product']} to lift overall basket value."
        )
    else:
        actions.append(
            "- Add product identifiers to future uploads so the system can recommend product-level actions instead of only aggregate actions."
        )

    fallback_note = (
        f"Gemini API is currently unavailable for this request ({failure_reason}). "
        f"A local rule-based summary is shown instead."
    )
    if language != "English":
        fallback_note += f" Requested language was {language}, but the fallback summary is returned in English."

    lines = [
        f"_Note: {fallback_note}_",
        "",
        "## Current Sales Health",
        f"- Scope: {product_name or dataset.get('selected_scope', 'All products')}",
        f"- Granularity: {dataset.get('granularity', 'unknown')}",
        f"- Current run rate: {_format_metric(summary.get('current_run_rate'))}",
        f"- Latest sales: {_format_metric(summary.get('latest_sales'))}",
        f"- Trend direction: {summary.get('trend_direction', 'unknown')} at {_format_metric(summary.get('growth_pct'), '%')}",
        f"- Festival uplift: {_format_metric(festival_impact.get('uplift_percentage'), '%')}",
        "",
        "## Future Outlook",
        f"- Forecast horizon: {_format_metric(forecast_periods)} {forecast_unit}",
        f"- Forecast direction: {forecast_summary.get('projected_direction', 'unknown')}",
        f"- Expected cumulative sales: {_format_metric(forecast_summary.get('cumulative_predicted_sales'))}",
        f"- Average predicted sales: {_format_metric(forecast_summary.get('average_predicted_sales'))}",
        f"- Peak forecast point: {forecast_summary.get('peak_forecast_date', 'n/a')} at {_format_metric(forecast_summary.get('peak_forecast_sales'))}",
        "",
        "## Product Focus",
        *product_focus_lines,
        "",
        "## Actions to Improve Sales",
        *actions[:3],
    ]

    return "\n".join(lines)


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
    if model is None:
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
        data = request.get_json()

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
        payload = request.get_json()
        items = payload.get("items", [])
        if not items:
            return jsonify({"success": False, "error": "No items were provided."}), 400

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
                "message": "File uploaded and normalized successfully.",
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
        payload = request.get_json()
        item = _resolve_item_from_payload(payload)
        result = generate_forecast(
            item,
            festival_calendar,
            selected_product=payload.get("selected_product"),
            forecast_periods=payload.get("forecast_periods"),
        )
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
        payload = request.get_json()
        item = _resolve_item_from_payload(payload)
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


@app.route("/api/model-info", methods=["GET"])
def model_info():
    if model is None:
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
    payload = {}
    context = None
    try:
        payload = request.get_json()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Gemini API key is not configured. Add GOOGLE_API_KEY to backend/.env.",
                    }
                ),
                400,
            )

        language = payload.get("language", "English")
        summary = payload.get("summary", "No summary provided.")
        product_name = payload.get("product_name", "All Products")
        context = payload.get("context")

        if not context and payload.get("upload_id"):
            item = _resolve_item_from_payload(payload)
            analysis_context = analyze_dataset(
                item,
                festival_calendar,
                selected_product=payload.get("selected_product"),
            )
            context = {"analysis": analysis_context}

        genai.configure(api_key=api_key)
        model_name = _resolve_gemini_model_name()
        llm = genai.GenerativeModel(model_name)
        response = llm.generate_content(_build_ai_prompt(language, product_name, context, summary))

        return jsonify(
            {
                "success": True,
                "language": language,
                "model": model_name,
                "insights": response.text,
            }
        )
    except LookupError as error:
        return jsonify({"success": False, "error": str(error)}), 404
    except Exception as error:
        fallback_insights = _build_fallback_ai_insights(
            language=payload.get("language", "English"),
            product_name=payload.get("product_name", "All Products"),
            context=context,
            failure_reason=str(error),
        )
        return jsonify(
            {
                "success": True,
                "fallback": True,
                "warning": f"Gemini unavailable: {error}",
                "language": payload.get("language", "English"),
                "model": "local-fallback",
                "insights": fallback_insights,
            }
        )


if __name__ == "__main__":
    if load_model():
        print("[INFO] Starting Flask server on http://127.0.0.1:5000")
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        print("[WARNING] Train a model before starting the API.")
