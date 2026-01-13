# ⚠️ DATASET REQUIRED

This folder should contain your training dataset: **Train.csv**

## Where to get the dataset:

1. **Kaggle**: Search for "Big Mart Sales Dataset"
2. **Analytics Vidhya**: Big Mart Sales III practice problem
3. **Custom Dataset**: Use your own retail sales data

## Required Columns:

Your CSV file must have these columns:
- Item_Identifier (e.g., "FDA15")
- Item_Weight (numeric)
- Item_Fat_Content (e.g., "Low Fat", "Regular")
- Item_Visibility (numeric, 0-1)
- Item_Type (e.g., "Dairy", "Soft Drinks")
- Item_MRP (numeric, price)
- Outlet_Identifier (e.g., "OUT049")
- Outlet_Establishment_Year (numeric, year)
- Outlet_Size (e.g., "Small", "Medium", "High")
- Outlet_Location_Type (e.g., "Tier 1", "Tier 2", "Tier 3")
- Outlet_Type (e.g., "Supermarket Type1", "Grocery Store")
- Item_Outlet_Sales (numeric, target variable)

## Expected Format:

```csv
Item_Identifier,Item_Weight,Item_Fat_Content,Item_Visibility,Item_Type,Item_MRP,Outlet_Identifier,Outlet_Establishment_Year,Outlet_Size,Outlet_Location_Type,Outlet_Type,Item_Outlet_Sales
FDA15,9.30,Low Fat,0.016047301,Dairy,249.8092,OUT049,1999,Medium,Tier 1,Supermarket Type1,3735.1380
DRC01,5.92,Regular,0.019278216,Soft Drinks,48.2692,OUT018,2009,Medium,Tier 3,Supermarket Type2,443.4228
```

## After adding Train.csv:

Run the model training:
```bash
python model.py
```

This will:
1. Load and preprocess the data
2. Train the XGBoost model
3. Save the model to `../models/sales_model.pkl`
4. Generate visualizations in `../visualizations/`
