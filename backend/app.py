"""
Enhanced Flask Backend for Sales Forecasting System
Includes CSV upload, time-series forecasting, and festival analysis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle
import numpy as np
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta
import io
from prophet import Prophet
from indian_holidays import IndianFestivalCalendar

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin requests from React

# Global variables
model = None
encoders = {}
feature_columns = None
festival_calendar = IndianFestivalCalendar()
model_type = "original"  # Track which model is loaded

# Load the trained model
def load_model():
    """Load the saved model and preprocessing objects (tries integrated model first)"""
    global model, encoders, feature_columns, model_type
    
    # Try loading integrated model first
    try:
        with open('models/integrated_sales_model.pkl', 'rb') as f:
            saved_data = pickle.load(f)
            model = saved_data['model']
            encoders = saved_data.get('encoders', {})
            feature_columns = saved_data['feature_columns']
            model_type = "integrated"
        print("✅ Integrated model loaded successfully!")
        print(f"   Features: {len(feature_columns)}")
        print(f"   Test R²: {saved_data['performance']['test_r2']:.4f}")
        print(f"   Datasets: {', '.join(saved_data['training_info']['datasets_used'])}")
        return True
    except FileNotFoundError:
        print("⚠️  Integrated model not found, trying original...")
        
        # Fallback to original model
        try:
            with open('models/sales_model.pkl', 'rb') as f:
                saved_data = pickle.load(f)
                model = saved_data['model']
                encoders = saved_data['encoders']
                feature_columns = saved_data['feature_columns']
                model_type = "original"
            print("✅ Original BigMart model loaded successfully!")
            return True
        except FileNotFoundError:
            print("❌ No model found. Please train a model first.")
            return False

# Preprocess single prediction input
def preprocess_input(data):
    """Preprocess user input to match training data format"""
    df = pd.DataFrame([data])
    
    # Standardize Item_Fat_Content
    fat_content_mapping = {
        'low fat': 'Low Fat',
        'LF': 'Low Fat',
        'reg': 'Regular',
        'Low Fat': 'Low Fat',
        'Regular': 'Regular'
    }
    df['Item_Fat_Content'] = df['Item_Fat_Content'].map(fat_content_mapping)
    
    # Encode categorical variables
    categorical_cols = [
        'Item_Identifier', 'Item_Fat_Content', 'Item_Type',
        'Outlet_Identifier', 'Outlet_Size', 
        'Outlet_Location_Type', 'Outlet_Type'
    ]
    
    for col in categorical_cols:
        if col in encoders:
            try:
                df[col] = encoders[col].transform(df[col])
            except ValueError:
                print(f"Warning: Unseen category in {col}, using default value")
                df[col] = 0
    
    df = df[feature_columns]
    return df


# ========== API ROUTES ==========

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "message": "Enhanced Sales Forecasting API is running!",
        "version": "2.0",
        "endpoints": {
            "predict": "/api/predict",
            "upload_csv": "/api/upload-csv",
            "forecast": "/api/forecast",
            "pattern_analysis": "/api/analyze-patterns",
            "festival_impact": "/api/festival-impact",
            "model_info": "/api/model-info",
            "health": "/api/health"
        }
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if model is loaded and ready"""
    if model is not None:
        return jsonify({
            "status": "healthy",
            "model_loaded": True
        })
    else:
        return jsonify({
            "status": "error",
            "model_loaded": False,
            "message": "Model not loaded"
        }), 500


@app.route('/api/predict', methods=['POST'])
def predict_sales():
    """Single item prediction (original functionality)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'Item_Identifier', 'Item_Weight', 'Item_Fat_Content',
            'Item_Visibility', 'Item_Type', 'Item_MRP',
            'Outlet_Identifier', 'Outlet_Establishment_Year',
            'Outlet_Size', 'Outlet_Location_Type', 'Outlet_Type'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Preprocess and predict
        processed_data = preprocess_input(data)
        prediction = model.predict(processed_data)[0]
        
        return jsonify({
            "success": True,
            "predicted_sales": round(float(prediction), 2),
            "input_data": data,
            "message": "Prediction successful!"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Prediction failed"
        }), 500


@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    """
    Upload and parse CSV file containing historical sales data
    Expected columns: date, sales, (optional: product, category, etc.)
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file uploaded"
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "Empty filename"
            }), 400
        
        # Read the CSV file
        try:
            df = pd.read_csv(file)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Failed to parse CSV: {str(e)}"
            }), 400
        
        # Validate required columns
        if 'date' not in df.columns or 'sales' not in df.columns:
            return jsonify({
                "success": False,
                "error": "CSV must contain 'date' and 'sales' columns"
            }), 400
        
        # Add festival features
        df = festival_calendar.add_festival_features(df, 'date')
        
        # Basic statistics
        stats = {
            "total_records": len(df),
            "date_range": {
                "start": str(df['date'].min()),
                "end": str(df['date'].max())
            },
            "sales_stats": {
                "mean": round(float(df['sales'].mean()), 2),
                "median": round(float(df['sales'].median()), 2),
                "min": round(float(df['sales'].min()), 2),
                "max": round(float(df['sales'].max()), 2)
            },
            "festival_days": int(df['is_holiday'].sum())
        }
        
        # Return preview data
        preview = df.head(10).to_dict('records')
        
        # Convert datetime to string for JSON serialization
        for record in preview:
            if 'date' in record:
                record['date'] = str(record['date'])
        
        return jsonify({
            "success": True,
            "stats": stats,
            "preview": preview,
            "columns": list(df.columns),
            "message": "CSV uploaded and processed successfully"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/forecast', methods=['POST'])
def forecast():
    """
    Generate time-series forecast using Prophet
    Input: historical sales data, forecast period (days)
    """
    try:
        data = request.get_json()
        
        if 'historical_data' not in data:
            return jsonify({
                "success": False,
                "error": "No historical data provided"
            }), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(data['historical_data'])
        
        # Validate columns
        if 'date' not in df.columns or 'sales' not in df.columns:
            return jsonify({
                "success": False,
                "error": "Data must contain 'date' and 'sales' columns"
            }), 400
        
        # Prepare data for Prophet
        prophet_df = df[['date', 'sales']].copy()
        prophet_df.columns = ['ds', 'y']
        prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
        
        # Add festival features as regressors
        df_with_features = festival_calendar.add_festival_features(df.copy(), 'date')
        prophet_df['festival_impact'] = df_with_features['days_to_festival'].apply(
            lambda x: 1 if abs(x) <= 7 else 0
        )
        
        # Train Prophet model
        prophet_model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True
        )
        prophet_model.add_regressor('festival_impact')
        prophet_model.fit(prophet_df)
        
        # Forecast period (default 30 days)
        forecast_days = data.get('forecast_days', 30)
        
        # Create future dataframe
        future = prophet_model.make_future_dataframe(periods=forecast_days)
        
        # Add festival impact for future dates
        future_df = pd.DataFrame({'date': future['ds']})
        future_with_features = festival_calendar.add_festival_features(future_df, 'date')
        future['festival_impact'] = future_with_features['days_to_festival'].apply(
            lambda x: 1 if abs(x) <= 7 else 0
        )
        
        # Make prediction
        forecast_result = prophet_model.predict(future)
        
        # Extract predictions
        predictions = forecast_result[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(forecast_days)
        
        # Format results
        forecast_data = []
        for _, row in predictions.iterrows():
            forecast_data.append({
                "date": str(row['ds'].date()),
                "predicted_sales": round(float(row['yhat']), 2),
                "lower_bound": round(float(row['yhat_lower']), 2),
                "upper_bound": round(float(row['yhat_upper']), 2)
            })
        
        return jsonify({
            "success": True,
            "forecast": forecast_data,
            "forecast_days": forecast_days,
            "message": "Forecast generated successfully"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Forecast generation failed"
        }), 500


@app.route('/api/analyze-patterns', methods=['POST'])
def analyze_patterns():
    """
    Analyze sales patterns from historical data
    Identify monthly trends, product performance, etc.
    """
    try:
        data = request.get_json()
        
        if 'historical_data' not in data:
            return jsonify({
                "success": False,
                "error": "No historical data provided"
            }), 400
        
        df = pd.DataFrame(data['historical_data'])
        df['date'] = pd.to_datetime(df['date'])
        
        # Add festival features
        df = festival_calendar.add_festival_features(df, 'date')
        
        # Monthly analysis
        df['month'] = df['date'].dt.month
        df['month_name'] = df['date'].dt.strftime('%B')
        monthly_sales = df.groupby('month_name')['sales'].agg(['mean', 'sum']).reset_index()
        
        # Festival impact analysis
        festival_sales = df.groupby('is_holiday')['sales'].mean()
        festival_impact = {
            "average_sales_normal_days": round(float(festival_sales.get(False, 0)), 2),
            "average_sales_festival_days": round(float(festival_sales.get(True, 0)), 2),
            "uplift_percentage": round(
                ((festival_sales.get(True, 0) - festival_sales.get(False, 0)) / 
                 festival_sales.get(False, 1)) * 100, 2
            ) if festival_sales.get(False, 0) > 0 else 0
        }
        
        # Top festival categories
        festival_category_sales = df[df['festival_category'].notna()].groupby(
            'festival_category'
        )['sales'].mean().sort_values(ascending=False).head(5)
        
        top_festivals = [
            {
                "festival": festival,
                "average_sales": round(float(sales), 2)
            }
            for festival, sales in festival_category_sales.items()
        ]
        
        return jsonify({
            "success": True,
            "patterns": {
                "monthly_trends": monthly_sales.to_dict('records'),
                "festival_impact": festival_impact,
                "top_festivals": top_festivals
            },
            "message": "Pattern analysis complete"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/festival-impact', methods=['GET'])
def festival_impact():
    """
    Get upcoming festivals and their expected impact
    """
    try:
        # Get next 60 days
        today = datetime.now()
        upcoming_festivals = []
        
        for i in range(60):
            date = today + timedelta(days=i)
            if festival_calendar.is_holiday(date):
                holiday_name = festival_calendar.get_holiday_name(date)
                category = festival_calendar.get_festival_category(holiday_name)
                impact_score = festival_calendar.get_festival_impact_score(date)
                
                upcoming_festivals.append({
                    "date": str(date.date()),
                    "festival": holiday_name,
                    "category": category,
                    "impact_score": round(impact_score, 2),
                    "days_from_now": i
                })
        
        return jsonify({
            "success": True,
            "upcoming_festivals": upcoming_festivals,
            "message": f"Found {len(upcoming_festivals)} upcoming festivals"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Get information about the trained model"""
    if model is None:
        return jsonify({
            "success": False,
            "message": "Model not loaded"
        }), 500
    
    return jsonify({
        "success": True,
        "model_type": "XGBoost Regressor",
        "features": feature_columns,
        "num_features": len(feature_columns),
        "encoders_loaded": list(encoders.keys()),
        "festival_support": True
    })


@app.route('/api/batch-predict', methods=['POST'])
def batch_predict():
    """Predict sales for multiple items at once"""
    try:
        data = request.get_json()
        items = data.get('items', [])
        
        if not items:
            return jsonify({
                "success": False,
                "error": "No items provided"
            }), 400
        
        predictions = []
        for item in items:
            processed_data = preprocess_input(item)
            prediction = model.predict(processed_data)[0]
            predictions.append({
                "item": item.get('Item_Identifier', 'Unknown'),
                "predicted_sales": round(float(prediction), 2)
            })
        
        return jsonify({
            "success": True,
            "predictions": predictions,
            "total_items": len(predictions)
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ========== RUN SERVER ==========

if __name__ == '__main__':
    if load_model():
        print("🚀 Starting Enhanced Flask server...")
        print("📊 Festival calendar loaded")
        print("🔮 Forecasting capabilities enabled")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("⚠️  Please train the model first by running model.py")
