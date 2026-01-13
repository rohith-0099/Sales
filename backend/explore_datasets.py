"""
Dataset Exploration Script
Analyzes the structure of the three Kaggle datasets
"""

import pandas as pd
import numpy as np
import os

print("=" * 70)
print("KAGGLE DATASETS EXPLORATION")
print("=" * 70)

# ========== 1. DIWALI SALES DATA ==========
print("\n📊 1. DIWALI SALES DATASET")
print("-" * 70)

diwali_path = 'data/diwali_sales/Diwali Sales Data.csv'
df_diwali = pd.read_csv(diwali_path, encoding='latin-1')

print(f"Shape: {df_diwali.shape}")
print(f"\nColumns:\n{df_diwali.columns.tolist()}")
print(f"\nFirst 5 rows:")
print(df_diwali.head())
print(f"\nData Types:")
print(df_diwali.dtypes)
print(f"\nMissing Values:")
print(df_diwali.isnull().sum())
print(f"\nBasic Statistics:")
print(df_diwali.describe())

# ========== 2. INDIAN RETAIL DATA ==========
print("\n\n📊 2. INDIAN RETAIL DATASET")
print("-" * 70)

retail_path = 'data/indian_retail/INDIA_RETAIL_DATA.xlsx'
df_retail = pd.read_excel(retail_path)

print(f"Shape: {df_retail.shape}")
print(f"\nColumns:\n{df_retail.columns.tolist()}")
print(f"\nFirst 5 rows:")
print(df_retail.head())
print(f"\nData Types:")
print(df_retail.dtypes)
print(f"\nMissing Values:")
print(df_retail.isnull().sum())
print(f"\nBasic Statistics:")
print(df_retail.describe())

# ========== 3. HOLIDAYS DATASET ==========
print("\n\n📊 3. HOLIDAYS DATASET")
print("-" * 70)

holidays_path = 'data/holidays/INDIA_RETAIL_DATA.xlsx'
if os.path.exists(holidays_path):
    df_holidays = pd.read_excel(holidays_path)
    
    print(f"Shape: {df_holidays.shape}")
    print(f"\nColumns:\n{df_holidays.columns.tolist()}")
    print(f"\nFirst 10 rows:")
    print(df_holidays.head(10))
    print(f"\nData Types:")
    print(df_holidays.dtypes)
    print(f"\nMissing Values:")
    print(df_holidays.isnull().sum())
else:
    print("Holidays dataset not found or same as retail dataset")

# ========== SUMMARY ==========
print("\n\n📋 DATASET SUMMARY")
print("=" * 70)
print(f"1. Diwali Sales: {df_diwali.shape[0]:,} records, {df_diwali.shape[1]} columns")
print(f"2. Indian Retail: {df_retail.shape[0]:,} records, {df_retail.shape[1]} columns")
if 'df_holidays' in locals():
    print(f"3. Holidays: {df_holidays.shape[0]:,} records, {df_holidays.shape[1]} columns")

# Save summary to file
with open('data/dataset_summary.txt', 'w') as f:
    f.write("DATASET EXPLORATION SUMMARY\n")
    f.write("=" * 70 + "\n\n")
    
    f.write("1. DIWALI SALES DATA\n")
    f.write(f"   Records: {df_diwali.shape[0]:,}\n")
    f.write(f"   Columns: {', '.join(df_diwali.columns.tolist())}\n\n")
    
    f.write("2. INDIAN RETAIL DATA\n")
    f.write(f"   Records: {df_retail.shape[0]:,}\n")
    f.write(f"   Columns: {', '.join(df_retail.columns.tolist())}\n\n")

print("\n✅ Summary saved to data/dataset_summary.txt")
print("\nExploration complete!")
