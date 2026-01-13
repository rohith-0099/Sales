"""
Machine Learning Model Training
File: backend/model.py

This script:
1. Loads and preprocesses the Big Mart data
2. Trains an XGBoost model
3. Evaluates model performance
4. Saves the model and encoders for use in Flask API
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn import metrics
import pickle
import os

# Create directories if they don't exist
os.makedirs('models', exist_ok=True)
os.makedirs('visualizations', exist_ok=True)

print("=" * 60)
print("SALES PREDICTION MODEL TRAINING")
print("=" * 60)

# ========== 1. LOAD DATA ==========
print("\n📂 Loading data...")
big_mart_data = pd.read_csv('data/Train.csv')
print(f"✅ Data loaded: {big_mart_data.shape[0]} rows, {big_mart_data.shape[1]} columns")
print("\nFirst 5 rows:")
print(big_mart_data.head())

# ========== 2. DATA EXPLORATION ==========
print("\n" + "=" * 60)
print("DATA EXPLORATION")
print("=" * 60)

print("\n📊 Dataset Info:")
print(big_mart_data.info())

print("\n📈 Statistical Summary:")
print(big_mart_data.describe())

print("\n❓ Missing Values:")
missing = big_mart_data.isnull().sum()
print(missing[missing > 0])

# ========== 3. DATA CLEANING ==========
print("\n" + "=" * 60)
print("DATA CLEANING")
print("=" * 60)

# Fill missing Item_Weight with mean
print("\n🔧 Filling missing Item_Weight with mean...")
mean_weight = big_mart_data['Item_Weight'].mean()
big_mart_data['Item_Weight'].fillna(mean_weight, inplace=True)
print(f"   Mean weight: {mean_weight:.2f}")

# Fill missing Outlet_Size with mode based on Outlet_Type
print("\n🔧 Filling missing Outlet_Size with mode by Outlet_Type...")
mode_of_outlet_size = big_mart_data.pivot_table(
    values='Outlet_Size', 
    columns='Outlet_Type', 
    aggfunc=(lambda x: x.mode()[0])
)
print(mode_of_outlet_size)

miss_values = big_mart_data['Outlet_Size'].isnull()
big_mart_data.loc[miss_values, 'Outlet_Size'] = big_mart_data.loc[
    miss_values, 'Outlet_Type'
].apply(lambda x: mode_of_outlet_size[x])

print("\n✅ Missing values after cleaning:")
print(big_mart_data.isnull().sum().sum(), "missing values")

# ========== 4. DATA VISUALIZATION ==========
print("\n" + "=" * 60)
print("CREATING VISUALIZATIONS")
print("=" * 60)

sns.set()

# Item_Weight distribution
plt.figure(figsize=(8, 5))
sns.histplot(big_mart_data['Item_Weight'], kde=True)
plt.title('Item Weight Distribution')
plt.savefig('visualizations/item_weight_dist.png')
plt.close()
print("✅ Saved: item_weight_dist.png")

# Item_MRP distribution
plt.figure(figsize=(8, 5))
sns.histplot(big_mart_data['Item_MRP'], kde=True)
plt.title('Item MRP Distribution')
plt.savefig('visualizations/item_mrp_dist.png')
plt.close()
print("✅ Saved: item_mrp_dist.png")

# Item_Outlet_Sales distribution (TARGET)
plt.figure(figsize=(8, 5))
sns.histplot(big_mart_data['Item_Outlet_Sales'], kde=True, color='green')
plt.title('Item Outlet Sales Distribution (Target Variable)')
plt.savefig('visualizations/sales_dist.png')
plt.close()
print("✅ Saved: sales_dist.png")

# Outlet_Establishment_Year
plt.figure(figsize=(10, 5))
sns.countplot(x='Outlet_Establishment_Year', data=big_mart_data)
plt.title('Outlet Establishment Year')
plt.savefig('visualizations/establishment_year.png')
plt.close()
print("✅ Saved: establishment_year.png")

# Item_Fat_Content (before standardization)
plt.figure(figsize=(8, 5))
sns.countplot(x='Item_Fat_Content', data=big_mart_data)
plt.title('Item Fat Content (Before Cleaning)')
plt.savefig('visualizations/fat_content_before.png')
plt.close()
print("✅ Saved: fat_content_before.png")

# ========== 5. DATA STANDARDIZATION ==========
print("\n" + "=" * 60)
print("DATA STANDARDIZATION")
print("=" * 60)

print("\n🔧 Standardizing Item_Fat_Content...")
print("Before:")
print(big_mart_data['Item_Fat_Content'].value_counts())

big_mart_data.replace({
    'Item_Fat_Content': {
        'low fat': 'Low Fat',
        'LF': 'Low Fat',
        'reg': 'Regular'
    }
}, inplace=True)

print("\nAfter:")
print(big_mart_data['Item_Fat_Content'].value_counts())

# Item_Fat_Content (after standardization)
plt.figure(figsize=(8, 5))
sns.countplot(x='Item_Fat_Content', data=big_mart_data)
plt.title('Item Fat Content (After Cleaning)')
plt.savefig('visualizations/fat_content_after.png')
plt.close()
print("✅ Saved: fat_content_after.png")

# ========== 6. LABEL ENCODING ==========
print("\n" + "=" * 60)
print("LABEL ENCODING")
print("=" * 60)

# Save encoders for later use in API
encoders = {}

categorical_columns = [
    'Item_Identifier', 'Item_Fat_Content', 'Item_Type',
    'Outlet_Identifier', 'Outlet_Size', 
    'Outlet_Location_Type', 'Outlet_Type'
]

print("\n🔧 Encoding categorical variables...")
for col in categorical_columns:
    encoder = LabelEncoder()
    big_mart_data[col] = encoder.fit_transform(big_mart_data[col])
    encoders[col] = encoder
    print(f"   ✅ {col}: {len(encoder.classes_)} unique values")

print("\n📊 Data after encoding:")
print(big_mart_data.head())

# ========== 7. FEATURE ENGINEERING ==========
print("\n" + "=" * 60)
print("FEATURE ENGINEERING")
print("=" * 60)

# Split features and target
X = big_mart_data.drop(columns='Item_Outlet_Sales', axis=1)
Y = big_mart_data['Item_Outlet_Sales']

print(f"\n📊 Features (X): {X.shape}")
print(f"📊 Target (Y): {Y.shape}")
print(f"\nFeature columns: {list(X.columns)}")

# ========== 8. TRAIN-TEST SPLIT ==========
print("\n" + "=" * 60)
print("TRAIN-TEST SPLIT")
print("=" * 60)

X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=42
)

print(f"\n📊 Training set: {X_train.shape[0]} samples")
print(f"📊 Testing set: {X_test.shape[0]} samples")

# ========== 9. MODEL TRAINING ==========
print("\n" + "=" * 60)
print("MODEL TRAINING")
print("=" * 60)

print("\n🤖 Training XGBoost Regressor...")
model = XGBRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42
)

model.fit(X_train, Y_train)
print("✅ Model training complete!")

# ========== 10. MODEL EVALUATION ==========
print("\n" + "=" * 60)
print("MODEL EVALUATION")
print("=" * 60)

# Predictions on training data
train_predictions = model.predict(X_train)
train_r2 = metrics.r2_score(Y_train, train_predictions)
train_mae = metrics.mean_absolute_error(Y_train, train_predictions)
train_rmse = np.sqrt(metrics.mean_squared_error(Y_train, train_predictions))

print("\n📈 Training Set Performance:")
print(f"   R² Score: {train_r2:.4f}")
print(f"   MAE: {train_mae:.2f}")
print(f"   RMSE: {train_rmse:.2f}")

# Predictions on test data
test_predictions = model.predict(X_test)
test_r2 = metrics.r2_score(Y_test, test_predictions)
test_mae = metrics.mean_absolute_error(Y_test, test_predictions)
test_rmse = np.sqrt(metrics.mean_squared_error(Y_test, test_predictions))

print("\n📈 Test Set Performance:")
print(f"   R² Score: {test_r2:.4f}")
print(f"   MAE: {test_mae:.2f}")
print(f"   RMSE: {test_rmse:.2f}")

# Visualization: Actual vs Predicted
plt.figure(figsize=(10, 6))
plt.scatter(Y_test, test_predictions, alpha=0.5)
plt.plot([Y_test.min(), Y_test.max()], [Y_test.min(), Y_test.max()], 'r--', lw=2)
plt.xlabel('Actual Sales')
plt.ylabel('Predicted Sales')
plt.title(f'Actual vs Predicted Sales (R² = {test_r2:.4f})')
plt.savefig('visualizations/actual_vs_predicted.png')
plt.close()
print("\n✅ Saved: actual_vs_predicted.png")

# Feature Importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(x='importance', y='feature', data=feature_importance)
plt.title('Feature Importance')
plt.savefig('visualizations/feature_importance.png')
plt.close()
print("✅ Saved: feature_importance.png")

print("\n🎯 Top 5 Important Features:")
print(feature_importance.head())

# ========== 11. SAVE MODEL ==========
print("\n" + "=" * 60)
print("SAVING MODEL")
print("=" * 60)

# Save model, encoders, and feature columns
model_data = {
    'model': model,
    'encoders': encoders,
    'feature_columns': list(X.columns),
    'performance': {
        'train_r2': train_r2,
        'test_r2': test_r2,
        'train_mae': train_mae,
        'test_mae': test_mae,
        'train_rmse': train_rmse,
        'test_rmse': test_rmse
    }
}

with open('models/sales_model.pkl', 'wb') as f:
    pickle.dump(model_data, f)

print("✅ Model saved to models/sales_model.pkl")

# ========== 12. TEST PREDICTION ==========
print("\n" + "=" * 60)
print("TEST PREDICTION")
print("=" * 60)

# Test with a sample
sample_idx = 0
sample_input = X_test.iloc[sample_idx:sample_idx+1]
sample_actual = Y_test.iloc[sample_idx]
sample_prediction = model.predict(sample_input)[0]

print("\n🧪 Sample Prediction:")
print(f"   Actual Sales: ${sample_actual:.2f}")
print(f"   Predicted Sales: ${sample_prediction:.2f}")
print(f"   Difference: ${abs(sample_actual - sample_prediction):.2f}")

print("\n" + "=" * 60)
print("✅ TRAINING COMPLETE!")
print("=" * 60)
print("\n💡 Next steps:")
print("   1. Run the Flask API: python app.py")
print("   2. Start the React frontend: npm run dev")
print("   3. Test predictions through the web interface")
