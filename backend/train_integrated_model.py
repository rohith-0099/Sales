"""
Integrated Model Training
Trains enhanced XGBoost model on unified Indian retail dataset
"""

import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn import metrics
import matplotlib.pyplot as plt
import seaborn as sns
import os

print("=" * 70)
print("INTEGRATED MODEL TRAINING - INDIAN RETAIL FORECASTING")
print("=" * 70)

# ========== 1. LOAD UNIFIED DATA ==========
print("\n📂 Step 1: Loading Unified Dataset...")
print("-" * 70)

df = pd.read_csv('data/unified_training_data.csv')
print(f"✅ Loaded: {len(df):,} records")
print(f"   Columns: {len(df.columns)}")
print(f"   Date range: {df['date'].min()} to {df['date'].max()}")

#========== 2. SELECT FEATURES ==========
print("\n🔧 Step 2: Feature Selection...")
print("-" * 70)

# Target variable
target = 'sales'

# Feature groups
temporal_features = ['year', 'month', 'day', 'dayofweek', 'quarter']
festival_features = ['is_holiday', 'days_to_festival', 'is_pre_festival', 
                    'is_post_festival', 'is_festival_season']
demographic_features_encoded = [col for col in df.columns if '_encoded' in col]

# Combine all features
feature_columns = (temporal_features + festival_features + 
                  demographic_features_encoded)

# Add numerical features if available
numerical_cols = ['item_mrp', 'profit', 'discount']
for col in numerical_cols:
    if col in df.columns:
        df[col] = df[col].fillna(df[col].median())
        feature_columns.append(col)

# Remove any features with all NaN
feature_columns = [col for col in feature_columns 
                  if col in df.columns and df[col].notna().any()]

print(f"✅ Selected {len(feature_columns)} features:")
for feat in feature_columns[:10]:
    print(f"   - {feat}")
if len(feature_columns) > 10:
    print(f"   ... and {len(feature_columns) - 10} more")

# ========== 3. PREPARE DATA ==========
print("\n📊 Step 3: Preparing Training Data...")
print("-" * 70)

# Drop rows with missing target
df_clean = df.dropna(subset=[target])
print(f"Records after cleaning: {len(df_clean):,}")

# Split features and target
X = df_clean[feature_columns].fillna(0)
Y = df_clean[target]

print(f"✅ Features shape: {X.shape}")
print(f"✅ Target shape: {Y.shape}")

# ========== 4. TRAIN-TEST SPLIT ==========
print("\n✂️ Step 4: Train-Test Split...")
print("-" * 70)

X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=42
)

print(f"Training set: {X_train.shape[0]:,} samples")
print(f"Testing set: {X_test.shape[0]:,} samples")

# ========== 5. TRAIN MODEL ==========
print("\n🤖 Step 5: Training Enhanced XGBoost Model...")
print("-" * 70)

model = XGBRegressor(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=7,
    min_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    objective='reg:squarederror'
)

print("Training in progress...")
model.fit(X_train, Y_train)
print("✅ Model training complete!")

# ========== 6. EVALUATE MODEL ==========
print("\n📈 Step 6: Model Evaluation...")
print("=" * 70)

# Training performance
train_predictions = model.predict(X_train)
train_r2 = metrics.r2_score(Y_train, train_predictions)
train_mae = metrics.mean_absolute_error(Y_train, train_predictions)
train_rmse = np.sqrt(metrics.mean_squared_error(Y_train, train_predictions))

print("\n🎯 TRAINING SET PERFORMANCE:")
print(f"   R² Score: {train_r2:.4f}")
print(f"   MAE: {train_mae:.2f}")
print(f"   RMSE: {train_rmse:.2f}")

# Testing performance
test_predictions = model.predict(X_test)
test_r2 = metrics.r2_score(Y_test, test_predictions)
test_mae = metrics.mean_absolute_error(Y_test, test_predictions)
test_rmse = np.sqrt(metrics.mean_squared_error(Y_test, test_predictions))

print("\n🎯 TEST SET PERFORMANCE:")
print(f"   R² Score: {test_r2:.4f}")
print(f"   MAE: {test_mae:.2f}")
print(f"   RMSE: {test_rmse:.2f}")

# ========== 7. FEATURE IMPORTANCE ==========
print("\n🔍 Step 7: Feature Importance Analysis...")
print("-" * 70)

feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 10 Most Important Features:")
print(feature_importance.head(10).to_string(index=False))

# Visualizations
os.makedirs('visualizations', exist_ok=True)

# Feature importance plot
plt.figure(figsize=(10, 8))
top_features = feature_importance.head(15)
sns.barplot(x='importance', y='feature', data=top_features, palette='viridis')
plt.title('Top 15 Feature Importance - Integrated Model')
plt.xlabel('Importance Score')
plt.tight_layout()
plt.savefig('visualizations/integrated_feature_importance.png', dpi=300)
plt.close()
print("✅ Saved: visualizations/integrated_feature_importance.png")

# Actual vs Predicted
plt.figure(figsize=(10, 6))
plt.scatter(Y_test, test_predictions, alpha=0.5, s=10)
plt.plot([Y_test.min(), Y_test.max()], [Y_test.min(), Y_test.max()], 
         'r--', lw=2, label='Perfect Prediction')
plt.xlabel('Actual Sales')
plt.ylabel('Predicted Sales')
plt.title(f'Actual vs Predicted Sales - Integrated Model (R² = {test_r2:.4f})')
plt.legend()
plt.tight_layout()
plt.savefig('visualizations/integrated_actual_vs_predicted.png', dpi=300)
plt.close()
print("✅ Saved: visualizations/integrated_actual_vs_predicted.png")

# ========== 8. SAVE MODEL ==========
print("\n💾 Step 8: Saving Enhanced Model...")
print("-" * 70)

# Load encoders
with open('models/unified_encoders.pkl', 'rb') as f:
    encoders = pickle.load(f)

# Prepare model package
model_package = {
    'model': model,
    'feature_columns': feature_columns,
    'encoders': encoders,
    'performance': {
        'train_r2': train_r2,
        'test_r2': test_r2,
        'train_mae': train_mae,
        'test_mae': test_mae,
        'train_rmse': train_rmse,
        'test_rmse': test_rmse
    },
    'training_info': {
        'total_records': len(df_clean),
        'train_records': len(X_train),
        'test_records': len(X_test),
        'num_features': len(feature_columns),
        'datasets_used': ['BigMart', 'Diwali Sales', 'Indian Retail']
    }
}

with open('models/integrated_sales_model.pkl', 'wb') as f:
    pickle.dump(model_package, f)

print(f"✅ Saved: models/integrated_sales_model.pkl")
print(f"   Model type: XGBoost Regressor")
print(f"   Features: {len(feature_columns)}")
print(f"   Training records: {len(X_train):,}")
print(f"   Test R²: {test_r2:.4f}")

# ========== 9. COMPARISON WITH ORIGINAL ==========
print("\n📊 Step 9: Comparison with Original Model...")
print("=" * 70)

try:
    with open('models/sales_model.pkl', 'rb') as f:
        original_model_data = pickle.load(f)
        original_performance = original_model_data.get('performance', {})
        
    print("\nOriginal BigMart Model:")
    print(f"   Test R²: {original_performance.get('test_r2', 'N/A')}")
    print(f"   Test RMSE: {original_performance.get('test_rmse', 'N/A')}")
    
    print("\nIntegrated Model (NEW):")
    print(f"   Test R²: {test_r2:.4f}")
    print(f"   Test RMSE: {test_rmse:.2f}")
    
    if original_performance.get('test_r2'):
        improvement = ((test_r2 - original_performance['test_r2']) / 
                      original_performance['test_r2'] * 100)
        print(f"\n{'🎉' if improvement > 0 else ''} R² Improvement: {improvement:+.2f}%")
except:
    print("\nOriginal model not found for comparison")

# ========== 10. SUMMARY ==========
print("\n" + "=" * 70)
print("✅ MODEL TRAINING COMPLETE!")
print("=" * 70)

print(f"\n📦 Model Package Includes:")
print(f"   - XGBoost model with {len(feature_columns)} features")
print(f"   - {len(encoders)} category encoders")
print(f"   - Festival calendar integration")
print(f"   - Demographic features (age, gender, location)")
print(f"   - Regional features (state, zone, city)")

print(f"\n🎯 Performance Metrics:")
print(f"   Test R² Score: {test_r2:.4f}")
print(f"   Test MAE: {test_mae:.2f}")
print(f"   Test RMSE: {test_rmse:.2f}")

print(f"\n📁 Output Files:")
print(f"   1. models/integrated_sales_model.pkl")
print(f"   2. visualizations/integrated_feature_importance.png")
print(f"   3. visualizations/integrated_actual_vs_predicted.png")

print(f"\n🚀 Next Steps:")
print(f"   - Update app.py to use integrated model")
print(f"   - Test predictions with new features")
print(f"   - Deploy to production!")
