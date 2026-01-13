/**
 * Main React Component for Sales Prediction System
 * File: frontend/src/App.jsx
 */

import { useState } from 'react'
import './App.css'

// API base URL (change this to your backend URL)
const API_URL = 'http://localhost:5000/api'

// Icons
const CartIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="logo-icon"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
)

const RefreshIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/></svg>
)

const TrendingIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
)

const HistoryIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3v5h5"/><path d="M3.05 13A9 9 0 1 0 6 5.3L3 8"/><path d="M12 7v5l4 2"/></svg>
)

const EmptyStateIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="empty-icon"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>
)

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
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
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
        <div className="brand">
          <CartIcon />
          <h1>Sales Prediction System</h1>
        </div>
        <div className="header-subtitle">
          AI-Powered Retail Analytics
        </div>
      </header>

      <main className="main-content">
        {/* Input Form Section */}
        <section className="input-section">
          <div className="card">
            <div className="card-header">
              <h2>Product & Store Details</h2>
            </div>
            
            <form onSubmit={handleSubmit} className="form-body">
              <div className="form-grid">
                
                {/* Product Details Group */}
                <div className="form-section-title">Product Information</div>

                <div className="form-group">
                  <label>Item Identifier</label>
                  <input
                    className="form-control"
                    type="text"
                    name="Item_Identifier"
                    value={formData.Item_Identifier}
                    onChange={handleChange}
                    placeholder="e.g., FDA15"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Item Weight (kg)</label>
                  <input
                    className="form-control"
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
                  <label>Item Fat Content</label>
                  <select
                    className="form-control"
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
                  <label>Item Visibility</label>
                  <input
                    className="form-control"
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
                  <label>Item Type</label>
                  <select
                    className="form-control"
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
                  <label>Item MRP ($)</label>
                  <input
                    className="form-control"
                    type="number"
                    step="0.01"
                    name="Item_MRP"
                    value={formData.Item_MRP}
                    onChange={handleChange}
                    placeholder="e.g., 249.81"
                    required
                  />
                </div>

                {/* Store Details Group */}
                <div className="form-section-title" style={{ marginTop: '1rem' }}>Store Information</div>

                <div className="form-group">
                  <label>Outlet Identifier</label>
                  <input
                    className="form-control"
                    type="text"
                    name="Outlet_Identifier"
                    value={formData.Outlet_Identifier}
                    onChange={handleChange}
                    placeholder="e.g., OUT049"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Establishment Year</label>
                  <input
                    className="form-control"
                    type="number"
                    name="Outlet_Establishment_Year"
                    value={formData.Outlet_Establishment_Year}
                    onChange={handleChange}
                    placeholder="e.g., 1999"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Outlet Size</label>
                  <select
                    className="form-control"
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
                  <label>Location Type</label>
                  <select
                    className="form-control"
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

                <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                  <label>Outlet Type</label>
                  <select
                    className="form-control"
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

                <div className="actions">
                  <button type="button" className="btn btn-secondary" onClick={handleReset} disabled={loading}>
                    <RefreshIcon /> Reset
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? <div className="spinner"></div> : <><TrendingIcon /> Predict Sales</>}
                  </button>
                </div>

              </div>
            </form>
          </div>
        </section>

        {/* Results Panel */}
        <aside className="results-panel">
          
          {/* Prediction Card */}
          <div className="card prediction-card">
            {prediction !== null ? (
              <div className="prediction-content">
                <div className="prediction-label">Predicted Sales</div>
                <div className="prediction-amount">
                  <span className="prediction-currency">$</span>
                  {prediction.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div>Predicted revenue for this item</div>
              </div>
            ) : (
              <div className="empty-state" style={{ color: 'rgba(255,255,255,0.7)', padding: '1rem' }}>
                <TrendingIcon style={{ width: 48, height: 48, marginBottom: '1rem', opacity: 0.5 }} />
                <p>Enter details and click predict to see projected sales revenue</p>
              </div>
            )}
          </div>

          {/* History Card */}
          <div className="card">
            <div className="card-header">
              <h2><HistoryIcon /> Recent Predictions</h2>
            </div>
            {history.length > 0 ? (
              <ul className="history-list">
                {history.map((item) => (
                  <li key={item.id} className="history-item">
                    <div className="history-meta">
                      <span className="history-id">{item.item}</span>
                      <span className="history-time">{item.timestamp}</span>
                    </div>
                    <span className="history-value">${item.sales.toFixed(2)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="empty-state">
                <EmptyStateIcon />
                <p>No predictions yet</p>
              </div>
            )}
          </div>

          {error && (
            <div className="card" style={{ borderLeft: '4px solid var(--error)', padding: '1rem' }}>
              <p style={{ color: 'var(--error)' }}>{error}</p>
            </div>
          )}

        </aside>
      </main>
    </div>
  )
}

export default App
