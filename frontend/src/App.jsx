import { useState } from 'react';
import axios from 'axios';
import FileUpload from './components/FileUpload';
import ForecastChart from './components/ForecastChart';
import './App.css';

const API_URL = 'http://localhost:5000/api';

function App() {
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' or 'single'
  const [uploadedData, setUploadedData] = useState(null);
  const [fileName, setFileName] = useState('');
  const [forecastData, setForecastData] = useState(null);
  const [patternAnalysis, setPatternAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Single prediction state (original feature)
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
  });
  const [prediction, setPrediction] = useState(null);

  // Handle file upload
  const handleFileUploaded = async (data, name) => {
    setFileName(name);
    setUploadedData(data);
    setError(null);

    // Auto-generate forecast if data has 'date' and 'sales' columns
    if (data.length > 0 && data[0].date && data[0].sales) {
      generateForecast(data);
      analyzePatterns(data);
    } else {
      setError('CSV must contain "date" and "sales" columns');
    }
  };

  // Generate forecast
  const generateForecast = async (data) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/forecast`, {
        historical_data: data,
        forecast_days: 30
      });

      if (response.data.success) {
        setForecastData(response.data.forecast);
      } else {
        setError(response.data.error || 'Forecast generation failed');
      }
    } catch (err) {
      setError(`Failed to generate forecast: ${err.message}`);
      console.error('Forecast error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Analyze patterns
  const analyzePatterns = async (data) => {
    try {
      const response = await axios.post(`${API_URL}/analyze-patterns`, {
        historical_data: data
      });

      if (response.data.success) {
        setPatternAnalysis(response.data.patterns);
      }
    } catch (err) {
      console.error('Pattern analysis error:', err);
    }
  };

  // Handle single prediction (original feature)
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const processedData = {
        ...formData,
        Item_Weight: parseFloat(formData.Item_Weight),
        Item_Visibility: parseFloat(formData.Item_Visibility),
        Item_MRP: parseFloat(formData.Item_MRP),
        Outlet_Establishment_Year: parseInt(formData.Outlet_Establishment_Year)
      };

      const response = await axios.post(`${API_URL}/predict`, processedData);

      if (response.data.success) {
        setPrediction(response.data.predicted_sales);
      } else {
        setError(response.data.error || 'Prediction failed');
      }
    } catch (err) {
      setError(`Failed to connect to server: ${err.message}`);
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
            🛒 Indian Retail Sales Forecasting System
          </h1>
          <p className="mt-2 text-gray-600">
            Upload your sales data, get AI-powered forecasts with festival impact analysis
          </p>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="flex space-x-4 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('upload')}
            className={`px-6 py-3 font-medium transition-all ${activeTab === 'upload'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
              }`}
          >
            📊 Bulk Forecast (CSV Upload)
          </button>
          <button
            onClick={() => setActiveTab('single')}
            className={`px-6 py-3 font-medium transition-all ${activeTab === 'single'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
              }`}
          >
            🔮 Single Item Prediction
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'upload' ? (
          // CSV Upload & Forecast View
          <div className="space-y-6">
            {/* Upload Section */}
            {!uploadedData && (
              <div className="bg-white rounded-lg shadow-md p-6 animate-fade-in">
                <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                  Upload Historical Sales Data
                </h2>
                <p className="text-gray-600 mb-4">
                  Upload a CSV file with columns: <code className="bg-gray-100 px-2 py-1 rounded">date</code> and <code className="bg-gray-100 px-2 py-1 rounded">sales</code>
                </p>
                <FileUpload onFileUploaded={handleFileUploaded} />
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg animate-fade-in">
                <p className="text-red-700">❌ {error}</p>
              </div>
            )}

            {/* Loading State */}
            {loading && (
              <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg animate-pulse">
                <p className="text-blue-700">⏳ Generating forecast...</p>
              </div>
            )}

            {/* Results */}
            {uploadedData && (
              <div className="space-y-6 animate-slide-up">
                {/* File Info */}
                <div className="bg-white rounded-lg shadow-md p-4">
                  <p className="text-gray-700">
                    📁 <span className="font-semibold">{fileName}</span> - {uploadedData.length} records loaded
                  </p>
                </div>

                {/* Forecast Chart */}
                {forecastData && (
                  <div className="bg-white rounded-lg shadow-md p-6">
                    <ForecastChart
                      historicalData={uploadedData}
                      forecastData={forecastData}
                      festivals={[]}
                    />
                  </div>
                )}

                {/* Pattern Analysis */}
                {patternAnalysis && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Festival Impact */}
                    <div className="bg-white rounded-lg shadow-md p-6">
                      <h3 className="text-xl font-semibold text-gray-800 mb-4">
                        🎉 Festival Impact
                      </h3>
                      <div className="space-y-2">
                        <p className="text-gray-700">
                          Normal Days: <span className="font-bold text-blue-600">
                            ${patternAnalysis.festival_impact.average_sales_normal_days}
                          </span>
                        </p>
                        <p className="text-gray-700">
                          Festival Days: <span className="font-bold text-green-600">
                            ${patternAnalysis.festival_impact.average_sales_festival_days}
                          </span>
                        </p>
                        <p className="text-gray-700">
                          Uplift: <span className="font-bold text-purple-600">
                            +{patternAnalysis.festival_impact.uplift_percentage}%
                          </span>
                        </p>
                      </div>
                    </div>

                    {/* Top Festivals */}
                    {patternAnalysis.top_festivals && patternAnalysis.top_festivals.length > 0 && (
                      <div className="bg-white rounded-lg shadow-md p-6">
                        <h3 className="text-xl font-semibold text-gray-800 mb-4">
                          🏆 Top Performing Festivals
                        </h3>
                        <ul className="space-y-2">
                          {patternAnalysis.top_festivals.map((fest, idx) => (
                            <li key={idx} className="flex justify-between items-center">
                              <span className="text-gray-700">{fest.festival}</span>
                              <span className="font-semibold text-blue-600">
                                ${fest.average_sales.toFixed(2)}
                              </span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* Reset Button */}
                <button
                  onClick={() => {
                    setUploadedData(null);
                    setForecastData(null);
                    setPatternAnalysis(null);
                    setFileName('');
                  }}
                  className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-6 rounded-lg transition-all"
                >
                  🔄 Upload New File
                </button>
              </div>
            )}
          </div>
        ) : (
          // Single Prediction View (Original Feature)
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Form */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-6">
                📝 Enter Product Details
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Item Identifier*
                  </label>
                  <input
                    type="text"
                    name="Item_Identifier"
                    value={formData.Item_Identifier}
                    onChange={handleChange}
                    placeholder="e.g., FDA15"
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Weight (kg)*
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      name="Item_Weight"
                      value={formData.Item_Weight}
                      onChange={handleChange}
                      placeholder="9.30"
                      required
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      MRP ($)*
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      name="Item_MRP"
                      value={formData.Item_MRP}
                      onChange={handleChange}
                      placeholder="249.81"
                      required
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Fat Content*
                  </label>
                  <select
                    name="Item_Fat_Content"
                    value={formData.Item_Fat_Content}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="Low Fat">Low Fat</option>
                    <option value="Regular">Regular</option>
                  </select>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
                >
                  {loading ? '⏳ Predicting...' : '🔮 Predict Sales'}
                </button>
              </form>
            </div>

            {/* Results */}
            <div className="space-y-6">
              {error && (
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
                  <p className="text-red-700">❌ {error}</p>
                </div>
              )}

              {prediction !== null && (
                <div className="bg-white rounded-lg shadow-md p-8 text-center animate-slide-up">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">
                    ✅ Prediction Result
                  </h3>
                  <div className="text-5xl font-bold text-green-600 my-6">
                    ${prediction.toFixed(2)}
                  </div>
                  <p className="text-gray-600">Estimated Sales</p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white shadow-md mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-gray-600">
          <p>Built with React + Tailwind + Flask + XGBoost + Prophet | Indian Festival Analysis Enabled 🎉</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
