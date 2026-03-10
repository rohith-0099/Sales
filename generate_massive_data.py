import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

output_dir = r"c:\Users\rohit\Desktop\sales-prediction-system\test_data"
os.makedirs(output_dir, exist_ok=True)

# Generate 1 year of dates
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)
date_list = [start_date + timedelta(days=x) for x in range((end_date-start_date).days + 1)]

# Household categories
categories = [
    ("Groceries", "Rice, Wheat, Dal, Spices, Oil, Sugar"),
    ("Snacks & Beverages", "Tea, Coffee, Biscuits, Chips, Namkeen"),
    ("Personal Care", "Soap, Shampoo, Toothpaste, Hair Oil"),
    ("Home Care", "Detergent, Floor Cleaner, Dishwash"),
    ("Electronics", "Bulbs, Batteries, Extension Cords"),
    ("Dairy", "Milk, Ghee, Butter, Paneer")
]

# Generate 1000 products
products = []
for i in range(1, 1001):
    cat, types = random.choice(categories)
    item_type = random.choice(types.split(", ")).strip()
    brand_prefix = random.choice(["Premium", "Everyday", "Value", "Fresh", "Pure", "Royal", "Gold"])
    product_name = f"{brand_prefix} {item_type} - Variant {i}"
    
    products.append({
        "product_code": f"IND-HH-{i:04d}",
        "product_name": product_name,
        "category": cat,
        "base_sales": random.randint(50, 5000),  # Daily sales volume
        "volatility": random.randint(10, 500)
    })

print("Generating 1 year of sales data for 1000 products...")
records = []

# Process chunks to save memory
for date in date_list:
    seasonality = 1.0
    # Indian festival season boost
    if date.month in [10, 11]:
        seasonality = 1.6  
    # Summer/minor holidays
    elif date.month in [3, 4, 5]:
        seasonality = 1.2
    
    # Randomly select a subset of products sold each day to make it realistic
    daily_products = random.sample(products, k=random.randint(400, 800))
    
    for prod in daily_products:
        noise = np.random.normal(0, prod["volatility"])
        sales = max(0, int((prod["base_sales"] + noise) * seasonality))
        
        # Outliers
        if random.random() > 0.99:
            sales = int(sales * 2.5)
            
        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "product_code": prod["product_code"],
            "product_name": prod["product_name"],
            "category": prod["category"],
            "sales": sales
        })

df = pd.DataFrame(records)
output_file = os.path.join(output_dir, "indian_household_1000_products_1yr.csv")
df.to_csv(output_file, index=False)
print(f"Generated {len(df)} records successfully!")
print(f"Saved to: {output_file}")
