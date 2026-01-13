# 🚀 Sales Prediction System

A full-stack machine learning application that predicts retail sales using XGBoost. Built with Flask (backend) and React (frontend).

## 📋 Features

- **Machine Learning Model**: XGBoost regressor trained on Big Mart sales data
- **REST API**: Flask backend with CORS support
- **Modern UI**: React frontend with responsive design
- **Real-time Predictions**: Instant sales predictions based on product and outlet features
- **Prediction History**: Track recent predictions
- **Data Visualization**: Model performance charts and feature importance

## 🛠️ Technology Stack

### Backend
- Python 3.8+
- Flask 3.0.0
- XGBoost 2.0.3
- Pandas, NumPy, Scikit-learn
- Matplotlib, Seaborn

### Frontend
- React 18
- Vite
- Axios
- Modern CSS with gradients

## 📂 Project Structure

```
sales-prediction-system/
├── backend/
│   ├── app.py                    # Flask API
│   ├── model.py                  # ML training script
│   ├── requirements.txt          # Python dependencies
│   ├── models/                   # Saved models
│   ├── data/                     # Training data (Train.csv)
│   └── visualizations/           # Generated charts
│
└── frontend/
    ├── src/
    │   ├── App.jsx              # Main React component
    │   └── App.css              # Styling
    ├── package.json
    └── vite.config.js
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm

### Backend Setup

1. **Navigate to backend folder**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your dataset**
   - Place `Train.csv` in the `data/` folder

5. **Train the model**
   ```bash
   python model.py
   ```

6. **Start Flask server**
   ```bash
   python app.py
   ```
   Server runs on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend folder**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```
   App runs on `http://localhost:5173`

## 📊 How to Use

1. Open `http://localhost:5173` in your browser
2. Fill in the product details:
   - Item information (ID, weight, type, MRP, etc.)
   - Outlet information (ID, size, location, type, etc.)
3. Click "Predict Sales"
4. View the predicted sales amount

### Sample Input
```
Item Identifier: FDA15
Item Weight: 9.30
Item Fat Content: Low Fat
Item Visibility: 0.016
Item Type: Dairy
Item MRP: 249.81
Outlet Identifier: OUT049
Outlet Establishment Year: 1999
Outlet Size: Medium
Outlet Location Type: Tier 1
Outlet Type: Supermarket Type1
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/health` | Model status |
| POST | `/api/predict` | Single prediction |
| GET | `/api/model-info` | Model details |
| POST | `/api/batch-predict` | Batch predictions |

### Example API Request
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

## 📈 Model Performance

- **R² Score**: ~0.56 (56% variance explained)
- **MAE**: ~$847 (average error)
- **RMSE**: ~$1,093 (root mean squared error)

## 🎯 Key Features

### Machine Learning
- Data preprocessing and cleaning
- Label encoding for categorical variables
- XGBoost regression model
- Model persistence with pickle
- Feature importance analysis

### Backend
- RESTful API design
- CORS enabled for frontend integration
- Input validation
- Error handling
- Model loading on startup

### Frontend
- Responsive design
- Form validation
- Loading states
- Error handling
- Prediction history
- Modern gradient UI

## 🔧 Customization

### Change Model Parameters
Edit `backend/model.py`:
```python
model = XGBRegressor(
    n_estimators=200,      # More trees
    learning_rate=0.05,    # Slower learning
    max_depth=7,           # Deeper trees
    random_state=42
)
```

### Change API URL
Edit `frontend/src/App.jsx`:
```javascript
const API_URL = 'http://your-backend-url/api'
```

## 🐛 Troubleshooting

### "Model not found" error
- Make sure you ran `python model.py` first

### "Failed to connect to server"
- Check if Flask is running on port 5000
- Verify CORS is enabled in `app.py`

### CORS errors
- Ensure `flask-cors` is installed
- Check API_URL in `App.jsx`

## 📚 Dataset

This project uses the Big Mart Sales dataset with the following features:

**Item Features:**
- Item_Identifier
- Item_Weight
- Item_Fat_Content
- Item_Visibility
- Item_Type
- Item_MRP

**Outlet Features:**
- Outlet_Identifier
- Outlet_Establishment_Year
- Outlet_Size
- Outlet_Location_Type
- Outlet_Type

**Target:**
- Item_Outlet_Sales (predicted value)

## 🎓 Learning Outcomes

- Machine Learning with XGBoost
- Data preprocessing and encoding
- Flask REST API development
- React frontend with hooks
- Full-stack integration
- Model deployment

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ using React, Flask, and XGBoost**
