"""
Flask Backend for Sales Prediction System
File: backend/app.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle
import numpy as np
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin requests from React

# Global variables for model and encoders
model = None
encoders = {}
feature_columns = None

# Load the trained model and encoders
def load_model():
    """Load the saved model and preprocessing objects"""
    global model, encoders, feature_columns
    try:
        with open('models/sales_model.pkl', 'rb') as f:
            saved_data = pickle.load(f)
            model = saved_data['model']
            encoders = saved_data['encoders']
            feature_columns = saved_data['feature_columns']
        print("✅ Model loaded successfully!")
        return True
    except FileNotFoundError:
        print("❌ Model not found. Please train the model first.")
        return False

# Preprocess input data (same as training)
def preprocess_input(data):
    """
    Preprocess user input to match training data format
    
    Args:
        data (dict): Raw input from frontend
    
    Returns:
        pd.DataFrame: Preprocessed data ready for prediction
    """
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
    
    # Encode categorical variables using saved encoders
    categorical_cols = [
        'Item_Identifier', 'Item_Fat_Content', 'Item_Type',
        'Outlet_Identifier', 'Outlet_Size', 
        'Outlet_Location_Type', 'Outlet_Type'
    ]
    
    for col in categorical_cols:
        if col in encoders:
            try:
                # Transform using saved encoder
                df[col] = encoders[col].transform(df[col])
            except ValueError:
                # Handle unseen categories (use mode or default)
                print(f"Warning: Unseen category in {col}, using default value")
                df[col] = 0
    
    # Ensure columns are in the same order as training
    df = df[feature_columns]
    
    return df


# ========== API ROUTES ==========

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "message": "Sales Prediction API is running!",
        "version": "1.0",
        "endpoints": {
            "predict": "/api/predict",
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
    """
    Main prediction endpoint
    
    Expected JSON input:
    {
        "Item_Identifier": "FDA15",
        "Item_Weight": 9.3,
        "Item_Fat_Content": "Low Fat",
        "Item_Visibility": 0.016,
        "Item_Type": "Dairy",
        "Item_MRP": 249.81,
        "Outlet_Identifier": "OUT049",
        "Outlet_Establishment_Year": 1999,
        "Outlet_Size": "Medium",
        "Outlet_Location_Type": "Tier 1",
        "Outlet_Type": "Supermarket Type1"
    }
    """
    try:
        # Get JSON data from request
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
        
        # Preprocess the input
        processed_data = preprocess_input(data)
        
        # Make prediction
        prediction = model.predict(processed_data)[0]
        
        # Return result
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
        "encoders_loaded": list(encoders.keys())
    })


@app.route('/api/batch-predict', methods=['POST'])
def batch_predict():
    """
    Predict sales for multiple items at once
    
    Expected JSON input:
    {
        "items": [
            {...item1_data...},
            {...item2_data...}
        ]
    }
    """
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
    # Load the model when server starts
    if load_model():
        print("🚀 Starting Flask server...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("⚠️  Please train the model first by running model.py")
