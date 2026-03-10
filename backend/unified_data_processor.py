"""
Unified Data Processor for Indian Retail Forecasting
Combines BigMart, Diwali Sales, and Indian Retail datasets
"""

import pandas as pd
import numpy as np
from datetime import datetime
from indian_holidays import IndianFestivalCalendar
from sklearn.preprocessing import LabelEncoder
import pickle

print("=" * 70)
print("UNIFIED DATA PROCESSING FOR INDIAN RETAIL FORECASTING")
print("=" * 70)

# Initialize festival calendar
calendar = IndianFestivalCalendar()

# ========== 1. LOAD DATASETS ==========
print("\n[INFO] Step 1: Loading Datasets...")
print("-" * 70)

# BigMart (original dataset)
bigmart = pd.read_csv('data/Train.csv')
print(f"[OK] BigMart: {bigmart.shape[0]:,} records")

# Diwali Sales
diwali = pd.read_csv('data/diwali_sales/Diwali Sales Data.csv', encoding='latin-1')
print(f"[OK] Diwali Sales: {diwali.shape[0]:,} records")

# Indian Retail
retail = pd.read_excel('data/indian_retail/INDIA_RETAIL_DATA.xlsx')
print(f"[OK] Indian Retail: {retail.shape[0]:,} records")

# ========== 2. PROCESS DIWALI SALES DATA ==========
print("\n[INFO] Step 2: Processing Diwali Sales Data...")
print("-" * 70)

# Create a unified schema for Diwali data
diwali_processed = pd.DataFrame({
    'sales': diwali['Amount'],
    'quantity': diwali['Orders'],
    'product_category': diwali['Product_Category'],
    'state': diwali['State'],
    'zone': diwali['Zone'],
    'gender': diwali['Gender'],
    'age_group': diwali['Age Group'],
    'marital_status': diwali['Marital_Status'],
    'occupation': diwali['Occupation'],
    # Assign Diwali 2019 dates (approximate)
    'date': pd.date_range(start='2019-10-20', periods=len(diwali), freq='H')[:len(diwali)]
})

print(f"Processed Diwali data: {diwali_processed.shape}")

# ========== 3. PROCESS INDIAN RETAIL DATA ==========
print("\n[INFO] Step 3: Processing Indian Retail Data...")
print("-" * 70)

# Standardize Indian Retail data
retail_processed = pd.DataFrame({
    'sales': retail['Sales'],
    'quantity': retail['QtyOrdered'],
    'product_category': retail['Product Type'],
    'product_subcategory': retail['Product Sub-Category'],
    'state': retail['State'],
    'city': retail['City'],
    'region': retail['Region'],
    'discount': retail['Discount offered'],
    'unit_price': retail['Unit Price'],
    'profit': retail['Profit'],
    'date': pd.to_datetime(retail['Order Date'])
})

print(f"Processed Indian Retail data: {retail_processed.shape}")

# ========== 4. PROCESS BIGMART DATA ==========
print("\n[INFO] Step 4: Processing BigMart Data...")
print("-" * 70)

# BigMart doesn't have dates, assign synthetic dates (2018 baseline)
bigmart_processed = pd.DataFrame({
    'sales': bigmart['Item_Outlet_Sales'],
    'item_weight': bigmart['Item_Weight'],
    'item_visibility': bigmart['Item_Visibility'],
    'item_mrp': bigmart['Item_MRP'],
    'product_category': bigmart['Item_Type'],
    'item_fat_content': bigmart['Item_Fat_Content'],
    'outlet_size': bigmart['Outlet_Size'],
    'outlet_location_type': bigmart['Outlet_Location_Type'],
    'outlet_type': bigmart['Outlet_Type'],
    'outlet_establishment_year': bigmart['Outlet_Establishment_Year'],
    # Assign dates scattered across 2018
    'date': pd.date_range(start='2018-01-01', periods=len(bigmart), freq='H')[:len(bigmart)]
})

print(f"Processed BigMart data: {bigmart_processed.shape}")

# ========== 5. ADD FESTIVAL FEATURES TO ALL DATASETS ==========
print("\n[INFO] Step 5: Adding Festival Features...")
print("-" * 70)

def add_festival_features(df):
    """Add festival-related features to any dataset with a 'date' column"""
    df = df.copy()
    df = calendar.add_festival_features(df, 'date')
    
    # Additional temporal features
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['dayofweek'] = df['date'].dt.dayofweek
    df['quarter'] = df['date'].dt.quarter
    
    # Festival season indicators
    df['is_festival_season'] = (
        df['is_diwali_season'] | 
        df['is_christmas_season'] | 
        df['is_pre_festival'] | 
        df['is_post_festival']
    ).astype(int)
    
    return df

diwali_processed = add_festival_features(diwali_processed)
retail_processed = add_festival_features(retail_processed)
bigmart_processed = add_festival_features(bigmart_processed)

print("[OK] Festival features added to all datasets")

# ========== 6. CREATE UNIFIED DATASET ==========
print("\n[INFO] Step 6: Creating Unified Dataset...")
print("-" * 70)

# Add source identifier
diwali_processed['data_source'] = 'diwali'
retail_processed['data_source'] = 'retail'
bigmart_processed['data_source'] = 'bigmart'

# Find common columns
common_cols = ['sales', 'date', 'product_category', 'data_source',
               'is_holiday', 'festival_category', 'days_to_festival',
               'is_pre_festival', 'is_post_festival', 'is_festival_season',
               'year', 'month', 'day', 'dayofweek', 'quarter']

# Merge datasets
unified_data = pd.concat([
    diwali_processed[common_cols + ['gender', 'age_group', 'state', 'zone', 'marital_status', 'occupation']],
    retail_processed[common_cols + ['region', 'city', 'state', 'profit', 'discount']],
    bigmart_processed[common_cols + ['item_mrp', 'outlet_size', 'outlet_type']]
], axis=0, ignore_index=True, sort=False)

print(f"[OK] Unified dataset created: {unified_data.shape}")
print(f"   - Total records: {len(unified_data):,}")
print(f"   - Date range: {unified_data['date'].min()} to {unified_data['date'].max()}")
print(f"   - Columns: {len(unified_data.columns)}")

# ========== 7. FEATURE ENGINEERING ==========
print("\n[INFO] Step 7: Feature Engineering...")
print("-" * 70)

# Encode categorical variables
categorical_features = ['product_category', 'festival_category', 'data_source',
                       'gender', 'age_group', 'state', 'zone', 'marital_status',
                       'occupation', 'region', 'outlet_size', 'outlet_type']

encoders = {}
for col in categorical_features:
    if col in unified_data.columns and unified_data[col].notna().any():
        le = LabelEncoder()
        # Handle NaN values
        unified_data[col] = unified_data[col].fillna('Unknown')
        unified_data[f'{col}_encoded'] = le.fit_transform(unified_data[col].astype(str))
        encoders[col] = le
        print(f"   [OK] Encoded {col}: {len(le.classes_)} categories")

# Fill missing numerical values
numerical_features = ['item_mrp', 'profit', 'discount']
for col in numerical_features:
    if col in unified_data.columns:
        unified_data[col] = unified_data[col].fillna(unified_data[col].median())

print(f"\n[OK] Feature engineering complete")

# ========== 8. SAVE PROCESSED DATA ==========
print("\n[INFO] Step 8: Saving Processed Data...")
print("-" * 70)

# Save unified dataset
unified_data.to_csv('data/unified_training_data.csv', index=False)
print(f"[OK] Saved: data/unified_training_data.csv ({len(unified_data):,} records)")

# Save encoders
with open('models/unified_encoders.pkl', 'wb') as f:
    pickle.dump(encoders, f)
print(f"[OK] Saved: models/unified_encoders.pkl ({len(encoders)} encoders)")

# ========== 9. GENERATE SUMMARY ==========
print("\n[INFO] Step 9: Data Summary...")
print("=" * 70)

summary = unified_data.groupby('data_source').agg({
    'sales': ['count', 'mean', 'sum'],
    'is_holiday': 'sum'
}).round(2)

print("\nRecords by Source:")
print(summary)

print("\nFestival Distribution:")
print(unified_data['festival_category'].value_counts().head(10))

print("\nDate Range by Source:")
for source in unified_data['data_source'].unique():
    subset = unified_data[unified_data['data_source'] == source]
    print(f"  {source}: {subset['date'].min().date()} to {subset['date'].max().date()}")

print("\n" + "=" * 70)
print("[OK] DATA PROCESSING COMPLETE!")
print("=" * 70)
print(f"\n[INFO] Output Files:")
print(f"   1. data/unified_training_data.csv - {len(unified_data):,} records")
print(f"   2. models/unified_encoders.pkl - {len(encoders)} encoders")
print(f"\n[INFO] Ready for model training!")
