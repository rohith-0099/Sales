/**
 * Main React Component for Sales Prediction System
 * File: frontend/src/App.jsx
 */

import { useState } from 'react'
import './App.css'

// API base URL (change this to your backend URL)
const API_URL = 'http://localhost:5000/api'

function App() {
  // Form state
  const [formData, setFormData] = useState({
    Item_Identifier: '',
    Item_Weight: '',
    Item_Fat_Content: 'Low Fat',
    Item_Visibility: '',
    Item_Type: 'Dairy',
    Item_MRP: '',
    Outlet_Identifier: '',
    Outlet_Establishment_Year: '',
    Outlet_Size: 'Medium',
    Outlet_Location_Type: 'Tier 1',
    Outlet_Type: 'Supermarket Type1'
  })

  // Result state
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setPrediction(null)

    try {
      // Convert string numbers to actual numbers
      const processedData = {
        ...formData,
        Item_Weight: parseFloat(formData.Item_Weight),
        Item_Visibility: parseFloat(formData.Item_Visibility),
        Item_MRP: parseFloat(formData.Item_MRP),
        Outlet_Establishment_Year: parseInt(formData.Outlet_Establishment_Year)
      }

      // Make API call
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(processedData)
      })

      const data = await response.json()

      if (data.success) {
        setPrediction(data.predicted_sales)
        
        // Add to history
        const newEntry = {
          id: Date.now(),
          item: formData.Item_Identifier,
          sales: data.predicted_sales,
          timestamp: new Date().toLocaleString()
        }
        setHistory(prev => [newEntry, ...prev].slice(0, 10)) // Keep last 10
      } else {
        setError(data.error || 'Prediction failed')
      }
    } catch (err) {
      setError('Failed to connect to server. Make sure backend is running on port 5000.')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  // Reset form
  const handleReset = () => {
    setFormData({
      Item_Identifier: '',
      Item_Weight: '',
      Item_Fat_Content: 'Low Fat',
      Item_Visibility: '',
      Item_Type: 'Dairy',
      Item_MRP: '',
      Outlet_Identifier: '',
      Outlet_Establishment_Year: '',
      Outlet_Size: 'Medium',
      Outlet_Location_Type: 'Tier 1',
      Outlet_Type: 'Supermarket Type1'
    })
    setPrediction(null)
    setError(null)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🛒 Big Mart Sales Prediction System</h1>
        <p>Predict sales using Machine Learning (XGBoost)</p>
      </header>

      <div className="container">
        {/* Prediction Form */}
        <div className="form-section">
          <h2>📝 Enter Product Details</h2>
          <form onSubmit={handleSubmit}>
            {/* Item Information */}
            <div className="form-group">
              <label>Item Identifier*</label>
              <input
                type="text"
                name="Item_Identifier"
                value={formData.Item_Identifier}
                onChange={handleChange}
                placeholder="e.g., FDA15"
                required
              />
            </div>

            <div className="form-group">
              <label>Item Weight (kg)*</label>
              <input
                type="number"
                step="0.01"
                name="Item_Weight"
                value={formData.Item_Weight}
                onChange={handleChange}
                placeholder="e.g., 9.30"
                required
              />
            </div>

            <div className="form-group">
              <label>Item Fat Content*</label>
              <select
                name="Item_Fat_Content"
                value={formData.Item_Fat_Content}
                onChange={handleChange}
                required
              >
                <option value="Low Fat">Low Fat</option>
                <option value="Regular">Regular</option>
              </select>
            </div>

            <div className="form-group">
              <label>Item Visibility*</label>
              <input
                type="number"
                step="0.001"
                name="Item_Visibility"
                value={formData.Item_Visibility}
                onChange={handleChange}
                placeholder="e.g., 0.016"
                required
              />
            </div>

            <div className="form-group">
              <label>Item Type*</label>
              <select
                name="Item_Type"
                value={formData.Item_Type}
                onChange={handleChange}
                required
              >
                <option value="Dairy">Dairy</option>
                <option value="Soft Drinks">Soft Drinks</option>
                <option value="Meat">Meat</option>
                <option value="Fruits and Vegetables">Fruits and Vegetables</option>
                <option value="Household">Household</option>
                <option value="Baking Goods">Baking Goods</option>
                <option value="Snack Foods">Snack Foods</option>
                <option value="Frozen Foods">Frozen Foods</option>
                <option value="Breakfast">Breakfast</option>
                <option value="Health and Hygiene">Health and Hygiene</option>
                <option value="Hard Drinks">Hard Drinks</option>
                <option value="Canned">Canned</option>
                <option value="Breads">Breads</option>
                <option value="Starchy Foods">Starchy Foods</option>
                <option value="Others">Others</option>
                <option value="Seafood">Seafood</option>
              </select>
            </div>

            <div className="form-group">
              <label>Item MRP ($)*</label>
              <input
                type="number"
                step="0.01"
                name="Item_MRP"
                value={formData.Item_MRP}
                onChange={handleChange}
                placeholder="e.g., 249.81"
                required
              />
            </div>

            {/* Outlet Information */}
            <h3>🏪 Outlet Information</h3>

            <div className="form-group">
              <label>Outlet Identifier*</label>
              <input
                type="text"
                name="Outlet_Identifier"
                value={formData.Outlet_Identifier}
                onChange={handleChange}
                placeholder="e.g., OUT049"
                required
              />
            </div>

            <div className="form-group">
              <label>Outlet Establishment Year*</label>
              <input
                type="number"
                name="Outlet_Establishment_Year"
                value={formData.Outlet_Establishment_Year}
                onChange={handleChange}
                placeholder="e.g., 1999"
                min="1985"
                max="2024"
                required
              />
            </div>

            <div className="form-group">
              <label>Outlet Size*</label>
              <select
                name="Outlet_Size"
                value={formData.Outlet_Size}
                onChange={handleChange}
                required
              >
                <option value="Small">Small</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
            </div>

            <div className="form-group">
              <label>Outlet Location Type*</label>
              <select
                name="Outlet_Location_Type"
                value={formData.Outlet_Location_Type}
                onChange={handleChange}
                required
              >
                <option value="Tier 1">Tier 1</option>
                <option value="Tier 2">Tier 2</option>
                <option value="Tier 3">Tier 3</option>
              </select>
            </div>

            <div className="form-group">
              <label>Outlet Type*</label>
              <select
                name="Outlet_Type"
                value={formData.Outlet_Type}
                onChange={handleChange}
                required
              >
                <option value="Supermarket Type1">Supermarket Type1</option>
                <option value="Supermarket Type2">Supermarket Type2</option>
                <option value="Supermarket Type3">Supermarket Type3</option>
                <option value="Grocery Store">Grocery Store</option>
              </select>
            </div>

            {/* Buttons */}
            <div className="button-group">
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? '⏳ Predicting...' : '🔮 Predict Sales'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={handleReset}>
                🔄 Reset
              </button>
            </div>
          </form>
        </div>

        {/* Results Section */}
        <div className="results-section">
          {/* Prediction Result */}
          {prediction !== null && (
            <div className="result-card success">
              <h3>✅ Prediction Result</h3>
              <div className="prediction-value">
                ${prediction.toFixed(2)}
              </div>
              <p>Estimated Sales</p>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="result-card error">
              <h3>❌ Error</h3>
              <p>{error}</p>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="result-card loading">
              <div className="spinner"></div>
              <p>Analyzing product data...</p>
            </div>
          )}

          {/* Prediction History */}
          {history.length > 0 && (
            <div className="history-card">
              <h3>📊 Recent Predictions</h3>
              <table>
                <thead>
                  <tr>
                    <th>Item ID</th>
                    <th>Predicted Sales</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((entry) => (
                    <tr key={entry.id}>
                      <td>{entry.item}</td>
                      <td>${entry.sales.toFixed(2)}</td>
                      <td>{entry.timestamp}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <footer className="footer">
        <p>Built with React + Flask + XGBoost | Data: Big Mart Sales Dataset</p>
      </footer>
    </div>
  )
}

export default App
