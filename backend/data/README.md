# Kaggle Datasets - Documentation

This folder contains three datasets downloaded from Kaggle for enhancing Indian retail sales forecasting.

## 📁 Dataset Structure

### 1. Diwali Sales Data (`diwali_sales/`)
- **File**: `Diwali Sales Data.csv`
- **Records**: 11,251 transactions
- **Purpose**: Diwali festival shopping behavior analysis
- **Key Columns**:
  - `User_ID`: Customer identifier
  - `Gender`, `Age Group`, `Age`: Demographics
  - `State`, `Zone`: Geographic information
  - `Product_Category`: Product type
  - `Amount`: Transaction value
  - `Orders`: Number of items
  - `Marital_Status`, `Occupation`: Customer profile

**Usage**: Perfect for training models to recognize Diwali season sales spikes and customer behavior patterns during India's biggest shopping festival.

---

### 2. Indian Retail Data (`indian_retail/`)
- **File**: `INDIA_RETAIL_DATA.xlsx`
- **Records**: 2,534 orders
- **Purpose**: General Indian retail transaction data
- **Key Columns**:
  - `Order Date`, `Ship Date`: Temporal features
  - `State`, `City`, `Region`, `Country`: Geographic data
  - `Product Type`, `Product Sub-Category`: Product classification
  - `Sales`, `Profit`: Financial metrics
  - `QtyOrdered`: Quantity
  - `Discount offered`, `Unit Price`: Pricing
  - `Freight Mode`, `Freight Expenses`: Logistics

**Usage**: Provides regional sales patterns, product performance, and pricing insights for Indian retail sector.

---

### 3. Holidays Dataset (`holidays/`)
- **File**: `INDIA_RETAIL_DATA.xlsx` (appears same as Indian Retail)
- **Records**: 2,534
- **Note**: This dataset appears to be identical to the Indian Retail dataset

**Alternative**: The system uses Python's `holidays` library for Indian festival detection (already integrated in `indian_holidays.py`)

---

## 🎯 Integration Approach

### Option 1: Diwali-Specific Model
Train a specialized model using Diwali Sales Data to predict festive season performance:
- Focus on demographics (age, gender, location)
- Product category preferences during festivit
ies
- Regional variations in Diwali shopping

### Option 2: General Retail Model
Use Indian Retail Data for broader predictions:
- Time-series analysis with order dates
- Regional sales patterns
- Product subcategory performance
- Discount impact on sales

### Option 3: Combined Approach
Merge both datasets:
1. Use Diwali data for festival-specific training
2. Use Retail data for general baseline
3. Apply festival calendar overlays from `indian_holidays.py`

---

## 📊 Data Quality Notes

### Diwali Sales Data
- ✅ Clean dataset with minimal missing values
- ✅ Rich demographic information
- ⚠️ No explicit date column (Diwali season implied)
- ✅ Good for customer segmentation

### Indian Retail Data
- ✅ Includes date columns for time-series
- ✅ Regional diversity (multiple states/cities)
- ✅ Product hierarchy (type → sub-category)
- ⚠️ Smaller dataset (2,534 records)

---

## 🚀 Next Steps

1. **Feature Engineering**:
   - Extract month/day from Order Date in Retail data
   - Tag Diwali Sales records with approximate dates
   - Create regional dummy variables
   - Encode product categories

2. **Model Training**:
   - Enhance XGBoost with demographic features (from Diwali data)
   - Train Prophet with regional regressors (from Retail data)
   - Cross-validate on festival vs. non-festival periods

3. **API Integration**:
   - Add demographic-based prediction endpoint
   - Regional forecast capabilities
   - Product category-specific predictions

---

## 📝 Example Use Cases

### Scenario 1: Diwali Season Forecast
"A retailer in Maharashtra wants to predict Diwali week sales for Electronics category"
- Use: Diwali Sales Data (State=Maharashtra segment)
- Features: Product_Category, Zone, Demographics
- Output: Expected sales volume and customer segments

### Scenario 2: Regional Expansion
"Chain planning to open in Bangalore needs Q4 forecast"
- Use: Indian Retail Data (City=Bangalore if available, or similar region)
- Features: Regional patterns, seasonal trends
- Output: Monthly sales projections

### Scenario 3: Inventory Planning
"Optimize stock levels for Baby Care products across North India"
- Use: Both datasets combined
- Features: Product category + Regional data + Festival calendar
- Output: Weekly demand forecast with festival overlays

---

## 🔗 Related Files

- [`indian_holidays.py`](file:///c:/Users/rohit/Desktop/sales-prediction-system/backend/indian_holidays.py) - Festival calendar module
- [`explore_datasets.py`](file:///c:/Users/rohit/Desktop/sales-prediction-system/backend/explore_datasets.py) - Data exploration script
- [`dataset_summary.txt`](file:///c:/Users/rohit/Desktop/sales-prediction-system/backend/data/dataset_summary.txt) - Quick summary

---

**🎉 These datasets significantly enhance the system's ability to predict Indian retail sales with cultural and regional context!**
