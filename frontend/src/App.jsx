import { useDeferredValue, useEffect, useState } from 'react';
import axios from 'axios';
import FileUpload from './components/FileUpload';
import ForecastChart from './components/ForecastChart';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const MARKETS = [
  { code: 'IN', label: 'India', currency: 'INR', locale: 'en-IN' },
  { code: 'US', label: 'United States', currency: 'USD', locale: 'en-US' },
  { code: 'GB', label: 'United Kingdom', currency: 'GBP', locale: 'en-GB' },
  { code: 'AE', label: 'UAE', currency: 'AED', locale: 'en-AE' },
  { code: 'AU', label: 'Australia', currency: 'AUD', locale: 'en-AU' },
  { code: 'CA', label: 'Canada', currency: 'CAD', locale: 'en-CA' },
];

function formatCurrency(value, marketCode = 'IN') {
  const market = MARKETS.find(m => m.code === marketCode) || MARKETS[0];
  const numericValue = Number(value ?? 0);
  return new Intl.NumberFormat(market.locale, {
    style: 'currency',
    currency: market.currency,
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  }).format(Number.isFinite(numericValue) ? numericValue : 0);
}

function formatPercent(value) {
  const numericValue = Number(value ?? 0);
  return `${numericValue >= 0 ? '+' : ''}${numericValue.toFixed(2)}%`;
}

function getRequestErrorMessage(error, fallbackMessage) {
  return error?.response?.data?.error || error?.message || fallbackMessage;
}

function MetricCard({ label, value, hint, accent = 'slate' }) {
  const accents = {
    slate: 'border-slate-200 bg-white text-slate-900',
    emerald: 'border-emerald-200 bg-emerald-50 text-emerald-900',
    amber: 'border-amber-200 bg-amber-50 text-amber-900',
    rose: 'border-rose-200 bg-rose-50 text-rose-900',
  };

  return (
    <div className={`min-w-0 rounded-3xl border p-5 shadow-sm ${accents[accent] || accents.slate}`}>
      <p className="break-words text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">{label}</p>
      <p
        className="mt-3 break-words text-[clamp(1.35rem,2.6vw,1.875rem)] font-semibold leading-tight [overflow-wrap:anywhere]"
        title={String(value ?? '')}
      >
        {value}
      </p>
      {hint ? <p className="mt-2 break-words text-sm text-slate-600">{hint}</p> : null}
    </div>
  );
}

function ProductSuggestions({ suggestions, selectedProduct, onSelect }) {
  if (!suggestions.length) {
    return null;
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-sm">
      <p className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Product suggestions</p>
      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion.value}
            type="button"
            onClick={() => onSelect(suggestion.value)}
            className={[
              'rounded-full px-3 py-2 text-sm transition',
              selectedProduct === suggestion.value
                ? 'bg-slate-900 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200',
            ].join(' ')}
          >
            {suggestion.value}
          </button>
        ))}
      </div>
    </div>
  );
}

function TopProductsTable({ products, onFocus, marketCode }) {
  if (!products?.length) {
    return null;
  }

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-end justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Product Ranking</p>
          <h3 className="text-2xl font-semibold text-slate-900">Top products by total sales</h3>
        </div>
        <p className="text-sm text-slate-500">Focus on a product to open its own forecast.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="text-slate-500">
            <tr className="border-b border-slate-200">
              <th className="pb-3 pr-4 font-medium">Rank</th>
              <th className="pb-3 pr-4 font-medium">Product</th>
              <th className="pb-3 pr-4 font-medium">Total sales</th>
              <th className="pb-3 pr-4 font-medium">Average sale</th>
              <th className="pb-3 pr-4 font-medium">Records</th>
              <th className="pb-3 font-medium">Action</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.product} className="border-b border-slate-100 last:border-0">
                <td className="py-3 pr-4 text-slate-600">{product.rank}</td>
                <td className="py-3 pr-4 font-medium text-slate-900">{product.product}</td>
                <td className="py-3 pr-4 text-slate-700">{formatCurrency(product.total_sales, marketCode)}</td>
                <td className="py-3 pr-4 text-slate-700">{formatCurrency(product.average_sales, marketCode)}</td>
                <td className="py-3 pr-4 text-slate-700">{product.records}</td>
                <td className="py-3">
                  <button
                    type="button"
                    onClick={() => onFocus(product.product)}
                    className="rounded-full bg-slate-900 px-3 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-white transition hover:bg-slate-700"
                  >
                    Analyze
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function TrendTable({ periods, marketCode }) {
  if (!periods?.length) {
    return null;
  }

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Trend Breakdown</p>
      <h3 className="mt-2 text-2xl font-semibold text-slate-900">Recent performance by period</h3>
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="text-slate-500">
            <tr className="border-b border-slate-200">
              <th className="pb-3 pr-4 font-medium">Period</th>
              <th className="pb-3 pr-4 font-medium">Total sales</th>
              <th className="pb-3 pr-4 font-medium">Average sales</th>
              <th className="pb-3 font-medium">Growth</th>
            </tr>
          </thead>
          <tbody>
            {periods.slice(-8).map((period) => (
              <tr key={period.label} className="border-b border-slate-100 last:border-0">
                <td className="py-3 pr-4 font-medium text-slate-900">{period.label}</td>
                <td className="py-3 pr-4 text-slate-700">{formatCurrency(period.total_sales, marketCode)}</td>
                <td className="py-3 pr-4 text-slate-700">{formatCurrency(period.average_sales, marketCode)}</td>
                <td className={`py-3 ${period.growth_pct >= 0 ? 'text-emerald-700' : 'text-rose-700'}`}>
                  {formatPercent(period.growth_pct)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function App() {
  const [market, setMarket] = useState('IN');
  const [uploadId, setUploadId] = useState('');
  const [fileName, setFileName] = useState('');
  const [uploadStats, setUploadStats] = useState(null);
  const [previewRows, setPreviewRows] = useState([]);
  const [granularity, setGranularity] = useState('daily');
  const [productEnabled, setProductEnabled] = useState(false);
  const [productQuery, setProductQuery] = useState('');
  const [selectedProduct, setSelectedProduct] = useState('');
  const [productSuggestions, setProductSuggestions] = useState([]);
  const [historicalSeries, setHistoricalSeries] = useState([]);
  const [forecastData, setForecastData] = useState([]);
  const [forecastSummary, setForecastSummary] = useState(null);
  const [forecastUnit, setForecastUnit] = useState('days');
  const [forecastHorizon, setForecastHorizon] = useState(30);
  const [patternAnalysis, setPatternAnalysis] = useState(null);
  const [festivals, setFestivals] = useState([]);
  const [aiLanguage, setAiLanguage] = useState('English');
  const [aiInsights, setAiInsights] = useState('');
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [error, setError] = useState('');
  const [statusMessage, setStatusMessage] = useState('');

  const deferredProductQuery = useDeferredValue(productQuery);

  useEffect(() => {
    if (!uploadId || !productEnabled) {
      setProductSuggestions([]);
      return undefined;
    }

    let ignore = false;
    const timerId = window.setTimeout(async () => {
      try {
        const response = await axios.get(`${API_URL}/products/search`, {
          params: {
            upload_id: uploadId,
            q: deferredProductQuery,
            limit: 8,
          },
        });

        if (!ignore && response.data.success) {
          setProductSuggestions(response.data.matches);
        }
      } catch {
        if (!ignore) {
          setProductSuggestions([]);
        }
      }
    }, 250);

    return () => {
      ignore = true;
      window.clearTimeout(timerId);
    };
  }, [deferredProductQuery, productEnabled, uploadId]);

  function resetAnalysisState() {
    setHistoricalSeries([]);
    setForecastData([]);
    setForecastSummary(null);
    setPatternAnalysis(null);
    setAiInsights('');
  }

  function resetDashboard() {
    setUploadId('');
    setFileName('');
    setUploadStats(null);
    setPreviewRows([]);
    setGranularity('daily');
    setProductEnabled(false);
    setProductQuery('');
    setSelectedProduct('');
    setProductSuggestions([]);
    resetAnalysisState();
    setError('');
    setStatusMessage('');
    setFestivals([]);
  }

  async function handleFileSelected(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('country_code', market);

    setUploading(true);
    setError('');
    setStatusMessage('Uploading and normalizing the dataset.');
    resetAnalysisState();

    try {
      const response = await axios.post(`${API_URL}/upload-csv`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (!response.data.success) {
        throw new Error(response.data.error || 'Upload failed.');
      }

      setUploadId(response.data.upload_id);
      setFileName(response.data.file_name);
      setUploadStats(response.data.stats);
      setPreviewRows(response.data.preview || []);
      setGranularity(response.data.granularity || 'daily');
      setProductEnabled(Boolean(response.data.product_column));
      setSelectedProduct('');
      setProductQuery('');
      setProductSuggestions(
        (response.data.sample_products || []).map((value) => ({
          value,
          total_sales: 0,
          records: 0,
          rank: null,
        })),
      );
        
        // Auto-set default horizon based on granularity
        const gran = response.data.granularity || 'daily';
        if (gran === 'monthly') setForecastHorizon(12);
        else if (gran === 'yearly') setForecastHorizon(3);
        else setForecastHorizon(30);

        setStatusMessage('Dataset uploaded successfully. Run analysis to generate forecasts and trends.');
    } catch (requestError) {
      setUploadId('');
      setFileName('');
      setUploadStats(null);
      setPreviewRows([]);
      setGranularity('daily');
      setProductEnabled(false);
      setProductQuery('');
      setSelectedProduct('');
      setProductSuggestions([]);
      resetAnalysisState();
      setError(getRequestErrorMessage(requestError, 'Upload failed.'));
      setStatusMessage('');
    } finally {
      setUploading(false);
    }
  }

  async function runAnalysis(productValue = selectedProduct) {
    if (!uploadId) {
      setError('Upload a dataset before running analysis.');
      return;
    }

    const normalizedProduct = productValue.trim();
    if (normalizedProduct) {
      setSelectedProduct(normalizedProduct);
      setProductQuery(normalizedProduct);
    } else {
      setSelectedProduct('');
      setProductQuery('');
    }

    setAnalyzing(true);
    setError('');
    setStatusMessage('Running pattern analysis and forecast generation.');
    setAiInsights('');

    try {
      const payload = {
        upload_id: uploadId,
        selected_product: normalizedProduct || null,
        country_code: market,
        forecast_periods: forecastHorizon,
      };

      const [forecastResponse, analysisResponse] = await Promise.all([
        axios.post(`${API_URL}/forecast`, payload),
        axios.post(`${API_URL}/analyze-patterns`, payload),
      ]);

      if (!forecastResponse.data.success) {
        throw new Error(forecastResponse.data.error || 'Forecast request failed.');
      }
      if (!analysisResponse.data.success) {
        throw new Error(analysisResponse.data.error || 'Analysis request failed.');
      }

      setHistoricalSeries(forecastResponse.data.historical_series || []);
      setForecastData(forecastResponse.data.forecast || []);
      setForecastSummary(
        forecastResponse.data.summary
          ? {
              ...forecastResponse.data.summary,
              confidence: forecastResponse.data.confidence || null,
              metrics: forecastResponse.data.metrics || null,
            }
          : null,
      );
      setForecastUnit(forecastResponse.data.forecast_unit || 'days');
      setPatternAnalysis(analysisResponse.data.patterns || null);
      setGranularity(forecastResponse.data.granularity || granularity);
      setSelectedProduct(forecastResponse.data.selected_product || normalizedProduct || '');
      
      // Fetch holidays for the chart
      const start = forecastResponse.data.historical_series?.[0]?.date;
      const end = forecastResponse.data.forecast?.[forecastResponse.data.forecast.length - 1]?.date;
      if (start && end) {
        try {
          const holidaysRes = await axios.get(`${API_URL}/holidays`, {
            params: { market, start, end }
          });
          if (holidaysRes.data.success) {
            setFestivals(holidaysRes.data.holidays || []);
          }
        } catch (e) {
          console.error("Failed to fetch holidays", e);
        }
      }

      setStatusMessage(
        forecastResponse.data.selected_product
          ? `Analysis ready for ${forecastResponse.data.selected_product}.`
          : 'Analysis ready for the full dataset.',
      );
    } catch (requestError) {
      setError(getRequestErrorMessage(requestError, 'Analysis failed.'));
    } finally {
      setAnalyzing(false);
    }
  }

  async function focusOnProduct(product) {
    setProductQuery(product);
    await runAnalysis(product);
  }

  async function viewAggregate() {
    await runAnalysis('');
  }

  function buildAiContext() {
    return {
      dataset: {
        file_name: fileName,
        granularity,
        selected_scope: selectedProduct || 'All products',
        stats: uploadStats,
      },
      analysis: patternAnalysis
        ? {
            summary: patternAnalysis.summary,
            trend_highlights: patternAnalysis.trend_highlights,
            selected_product_stats: patternAnalysis.selected_product_stats,
            top_products: (patternAnalysis.top_products || []).slice(0, 5),
            recent_periods: (patternAnalysis.period_trends || []).slice(-6),
            festival_impact: patternAnalysis.festival_impact,
            top_festivals: patternAnalysis.top_festivals,
          }
        : null,
      forecast: forecastSummary
        ? {
            summary: forecastSummary,
            unit: forecastUnit,
            periods: forecastData.length,
            preview: [
              ...forecastData.slice(0, 3),
              ...forecastData.slice(-2),
            ],
          }
        : null,
    };
  }

  async function fetchAiInsights() {
    if (!forecastSummary || !patternAnalysis) {
      setError('Run the analysis before requesting AI insights.');
      return;
    }

    setAiLoading(true);
    setAiInsights('');
    setError('');

    const summary = [
      `Granularity: ${granularity}.`,
      `Current run rate: ${formatCurrency(patternAnalysis.summary.current_run_rate, market)}.`,
      `Latest sales: ${formatCurrency(patternAnalysis.summary.latest_sales, market)}.`,
      `Trend direction: ${patternAnalysis.summary.trend_direction}.`,
      `Projected direction: ${forecastSummary.projected_direction}.`,
      `Projected cumulative sales: ${formatCurrency(forecastSummary.cumulative_predicted_sales, market)}.`,
    ].join(' ');
    const marketDetails = MARKETS.find((entry) => entry.code === market) || MARKETS[0];
    const festivalSignal = festivals.length
      ? festivals.slice(0, 2).map((festival) => festival.festival).join(', ')
      : 'None';

    try {
      const response = await axios.post(`${API_URL}/ai-insights`, {
        language: aiLanguage,
        product_name: selectedProduct || 'All products',
        summary,
        total_sales: patternAnalysis.summary.total_sales,
        trend: `${patternAnalysis.summary.trend_direction}; forecast ${forecastSummary.projected_direction}`,
        growth_rate: patternAnalysis.summary.growth_pct,
        festival: festivalSignal,
        granularity,
        market: marketDetails.label,
        context: buildAiContext(),
        country_code: market,
      });

      if (!response.data.success) {
        throw new Error(response.data.error || 'AI insight generation failed.');
      }

      if (response.data.fallback) {
        setStatusMessage('The AI service is unavailable right now. Showing a local fallback insight summary.');
      }
      setAiInsights(response.data.insights || '');
    } catch (requestError) {
      setError(getRequestErrorMessage(requestError, 'AI insight generation failed.'));
    } finally {
      setAiLoading(false);
    }
  }

  function downloadForecastReport() {
    if (!forecastData.length) return;
    
    const productLabel = selectedProduct || 'Total_Store';
    const today = new Date().toISOString().split('T')[0];
    const fileName = `${productLabel.replace(/[^a-z0-9]/gi, '_')}_forecast_${today}.csv`;
    
    const headers = ['date', 'predicted_sales', 'lower_bound', 'upper_bound', 'is_festival', 'festival_name'];
    const rows = forecastData.map(row => [
      row.date,
      row.predicted_sales,
      row.lower_bound,
      row.upper_bound,
      row.is_festival ? 'YES' : 'NO',
      row.festival_name || ''
    ]);
    
    const csvContent = [
      headers.join(','),
      ...rows.map(r => r.join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", fileName);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  const analysisReady = Boolean(patternAnalysis && forecastSummary);

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(253,224,71,0.18),_transparent_28%),linear-gradient(180deg,_#fffef6_0%,_#f8fafc_42%,_#eef2ff_100%)]">
      <header className="border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <p className="text-sm font-semibold uppercase tracking-[0.25em] text-amber-600">
              Retail Intelligence Platform
            </p>
            <div className="flex items-center gap-3">
              <label htmlFor="market-select" className="text-sm font-medium text-slate-700">Market:</label>
              <select
                id="market-select"
                value={market}
                onChange={(e) => setMarket(e.target.value)}
                className="rounded-full border border-slate-300 px-4 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-900"
              >
                {MARKETS.map(m => <option key={m.code} value={m.code}>{m.label} ({m.currency})</option>)}
              </select>
            </div>
          </div>
          <div className="mt-4 grid gap-6 lg:grid-cols-[1.7fr_1fr] lg:items-end">
            <div>
              <h1 className="max-w-4xl text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
                Upload retail sales data, inspect product-level trends, and forecast what comes next.
              </h1>
              <p className="mt-4 max-w-3xl text-lg leading-8 text-slate-600">
                The dashboard accepts daily, weekly, monthly, or yearly retail sales data, identifies product
                entities automatically, generates forecasts, and explains the pattern in multiple languages with
                AI.
              </p>
            </div>
            <div className="rounded-3xl border border-amber-200 bg-amber-50 p-5 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-amber-700">Current scope</p>
              <p className="mt-3 text-2xl font-semibold text-slate-900">
                {selectedProduct || 'All products'}
              </p>
              <p className="mt-2 text-sm text-slate-600">
                {uploadStats
                  ? `${uploadStats.series_points} time points from ${uploadStats.start_date} to ${uploadStats.end_date}`
                  : 'Upload a file to initialize the analysis session.'}
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="space-y-6">
          <section className="rounded-[2rem] border border-slate-200 bg-white/90 p-6 shadow-sm">
            <div className="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Step 1</p>
                <h2 className="text-2xl font-semibold text-slate-900">Upload the source data</h2>
              </div>
              {fileName ? <p className="text-sm text-slate-500">Current file: {fileName}</p> : null}
            </div>
            <FileUpload onFileSelected={handleFileSelected} disabled={uploading || analyzing} />
          </section>

          {error ? (
            <section className="rounded-3xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700 shadow-sm">
              {error}
            </section>
          ) : null}

          {statusMessage ? (
            <section className="rounded-3xl border border-sky-200 bg-sky-50 px-5 py-4 text-sm text-sky-700 shadow-sm">
              {statusMessage}
            </section>
          ) : null}

          {uploadStats ? (
            <>
              <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <MetricCard
                  label="Detected granularity"
                  value={granularity}
                  hint={`${uploadStats.series_points} normalized time points`}
                  accent="amber"
                />
                <MetricCard
                  label="Total historical sales"
                  value={formatCurrency(uploadStats.total_sales, market)}
                  hint={`${uploadStats.rows} parsed rows`}
                  accent="emerald"
                />
                <MetricCard
                  label="Average sales"
                  value={formatCurrency(uploadStats.average_sales, market)}
                  hint={`Latest sale ${formatCurrency(uploadStats.latest_sales, market)}`}
                />
                <MetricCard
                  label="Product coverage"
                  value={productEnabled ? uploadStats.unique_products : 0}
                  hint={productEnabled ? 'Search is enabled for this dataset' : 'No product identifiers were detected'}
                />
              </section>

              <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
                <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                  <div className="mb-4 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Step 2</p>
                      <h2 className="text-2xl font-semibold text-slate-900">Choose scope and run analysis</h2>
                    </div>
                    <button
                      type="button"
                      onClick={viewAggregate}
                      disabled={analyzing}
                      className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      View aggregate dataset
                    </button>
                  </div>

                  {productEnabled ? (
                    <div className="space-y-4">
                      <label className="block">
                        <span className="mb-2 block text-sm font-medium text-slate-700">
                          Search by product name or identifier
                        </span>
                        <input
                          type="text"
                          value={productQuery}
                          onChange={(event) => {
                            setProductQuery(event.target.value);
                            setSelectedProduct(event.target.value);
                          }}
                          placeholder="Type a product name or ID"
                          className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-slate-900 outline-none transition focus:border-slate-900"
                        />
                      </label>
                      <ProductSuggestions
                        suggestions={productSuggestions}
                        selectedProduct={selectedProduct}
                        onSelect={(value) => {
                          setSelectedProduct(value);
                          setProductQuery(value);
                        }}
                      />
                      
                      <div className="mt-6">
                        <span className="mb-2 block text-sm font-medium text-slate-700">Forecast Horizon</span>
                        <div className="flex flex-wrap gap-2">
                          {[
                            { label: '7 Days', value: 7 },
                            { label: '30 Days', value: 30 },
                            { label: '90 Days', value: 90 },
                            { label: '12 Months', value: 12 },
                            { label: '1 Year', value: 365 },
                          ].map((opt) => (
                            <button
                              key={opt.label}
                              type="button"
                              onClick={() => setForecastHorizon(opt.value)}
                              className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                                forecastHorizon === opt.value
                                  ? 'bg-amber-500 text-white'
                                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                              }`}
                            >
                              {opt.label}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
                      No product-level search field was detected in this upload. Analysis will run on the full
                      dataset only.
                    </p>
                  )}

                  <div className="mt-6 flex flex-wrap gap-3">
                    <button
                      type="button"
                      onClick={() => runAnalysis(selectedProduct)}
                      disabled={uploading || analyzing}
                      className="rounded-full bg-slate-900 px-5 py-3 text-sm font-semibold uppercase tracking-[0.12em] text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {analyzing ? 'Analyzing' : 'Generate forecast and insights'}
                    </button>
                    <button
                      type="button"
                      onClick={resetDashboard}
                      disabled={uploading || analyzing}
                      className="rounded-full border border-slate-300 px-5 py-3 text-sm font-semibold uppercase tracking-[0.12em] text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      Reset session
                    </button>
                  </div>
                </div>

                <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Upload preview</p>
                  <h2 className="mt-2 text-2xl font-semibold text-slate-900">Normalized sample rows</h2>
                  <div className="mt-4 overflow-x-auto">
                    <table className="min-w-full text-left text-sm">
                      <thead className="text-slate-500">
                        <tr className="border-b border-slate-200">
                          {previewRows[0]
                            ? Object.keys(previewRows[0]).map((column) => (
                                <th key={column} className="pb-3 pr-4 font-medium">
                                  {column}
                                </th>
                              ))
                            : null}
                        </tr>
                      </thead>
                      <tbody>
                        {previewRows.map((row, index) => (
                          <tr key={`${row.date}-${index}`} className="border-b border-slate-100 last:border-0">
                            {Object.values(row).map((value, cellIndex) => (
                              <td key={`${index}-${cellIndex}`} className="py-3 pr-4 text-slate-700">
                                {String(value ?? '')}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </section>
            </>
          ) : null}

          {analysisReady ? (
            <>
              <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <MetricCard
                  label="Total sales"
                  value={formatCurrency(patternAnalysis.summary.total_sales, market)}
                  hint={`Range ${patternAnalysis.summary.start_date} to ${patternAnalysis.summary.end_date}`}
                  accent="emerald"
                />
                <MetricCard
                  label="Current run rate"
                  value={formatCurrency(patternAnalysis.summary.current_run_rate, market)}
                  hint={`Previous run rate ${formatCurrency(patternAnalysis.summary.previous_run_rate, market)}`}
                />
                <MetricCard
                  label="Growth"
                  value={formatPercent(patternAnalysis.summary.growth_pct)}
                  hint={`Trend is ${patternAnalysis.summary.trend_direction}`}
                  accent={patternAnalysis.summary.growth_pct >= 0 ? 'amber' : 'rose'}
                />
                <MetricCard
                  label="Forecast total"
                  value={formatCurrency(forecastSummary.cumulative_predicted_sales, market)}
                  hint={`Across the next ${forecastData.length} ${forecastUnit}`}
                  accent="amber"
                />
              </section>

              {forecastSummary.comparison_to_current ? (
                <section className="grid gap-4 md:grid-cols-3">
                  <MetricCard
                    label="Current average sales"
                    value={formatCurrency(forecastSummary.comparison_to_current.current_average_sales, market)}
                    hint={`Based on the latest ${forecastSummary.comparison_to_current.baseline_window_points} data points`}
                  />
                  <MetricCard
                    label="Predicted average sales"
                    value={formatCurrency(forecastSummary.comparison_to_current.forecast_average_sales, market)}
                    hint={`Expected average across the next ${forecastData.length} ${forecastUnit}`}
                    accent="amber"
                  />
                  <MetricCard
                    label="Forecast vs current"
                    value={formatPercent(forecastSummary.comparison_to_current.delta_pct)}
                    hint={`Next period change ${formatPercent(forecastSummary.comparison_to_current.next_period_delta_pct)}`}
                    accent={forecastSummary.comparison_to_current.delta_pct >= 0 ? 'emerald' : 'rose'}
                  />
                </section>
              ) : null}

              {patternAnalysis.selected_product_stats ? (
                <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Selected product</p>
                  <div className="mt-3 grid gap-4 md:grid-cols-4">
                    <MetricCard
                      label="Product rank"
                      value={`#${patternAnalysis.selected_product_stats.rank}`}
                      hint={patternAnalysis.selected_product_stats.product}
                    />
                    <MetricCard
                      label="Product sales"
                      value={formatCurrency(patternAnalysis.selected_product_stats.total_sales, market)}
                      hint={`${patternAnalysis.selected_product_stats.records} records`}
                    />
                    <MetricCard
                      label="Average product sale"
                      value={formatCurrency(patternAnalysis.selected_product_stats.average_sales, market)}
                      hint="Based on filtered records"
                    />
                    <MetricCard
                      label="Catalog share"
                      value={formatPercent(patternAnalysis.selected_product_stats.share_of_catalog_sales_pct)}
                      hint="Share of aggregate sales"
                    />
                  </div>
                </section>
              ) : null}

              <ForecastChart
                historicalData={historicalSeries}
                forecastData={forecastData}
                festivals={festivals}
                granularity={granularity}
                marketCode={market}
                confidence={forecastSummary?.confidence}
                metrics={forecastSummary?.metrics}
              />

              <div className="flex justify-end">
                <button
                  onClick={downloadForecastReport}
                  className="flex items-center gap-2 rounded-xl bg-emerald-600 px-6 py-3 font-semibold text-white shadow-lg transition hover:bg-emerald-700"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                  Download Forecast Report (.csv)
                </button>
              </div>

              <section className="grid gap-6 lg:grid-cols-2">
                <TrendTable periods={patternAnalysis.period_trends} marketCode={market} />

                <div className="space-y-6">
                  <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Trend highlights</p>
                    <h3 className="mt-2 text-2xl font-semibold text-slate-900">What the system found</h3>
                    <div className="mt-4 space-y-3 text-sm text-slate-700">
                      <p>
                        Momentum: <span className="font-semibold text-slate-900">{patternAnalysis.trend_highlights.momentum}</span>
                      </p>
                      {patternAnalysis.trend_highlights.best_period ? (
                        <p>
                          Best period: <span className="font-semibold text-slate-900">{patternAnalysis.trend_highlights.best_period.label}</span>{' '}
                          with {formatCurrency(patternAnalysis.trend_highlights.best_period.total_sales, market)} in sales.
                        </p>
                      ) : null}
                      {patternAnalysis.trend_highlights.weakest_period ? (
                        <p>
                          Weakest period:{' '}
                          <span className="font-semibold text-slate-900">{patternAnalysis.trend_highlights.weakest_period.label}</span>{' '}
                          with {formatCurrency(patternAnalysis.trend_highlights.weakest_period.total_sales, market)} in sales.
                        </p>
                      ) : null}
                      <p>
                        Forecast direction:{' '}
                        <span className="font-semibold text-slate-900">{forecastSummary.projected_direction}</span>
                      </p>
                      <p>
                        Forecast peak: <span className="font-semibold text-slate-900">{forecastSummary.peak_forecast_date}</span>{' '}
                        at {formatCurrency(forecastSummary.peak_forecast_sales, market)}.
                      </p>
                    </div>
                  </div>

                  <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Festival effect</p>
                    <h3 className="mt-2 text-2xl font-semibold text-slate-900">Holiday sensitivity</h3>
                    <div className="mt-4 grid gap-4 md:grid-cols-3">
                      <MetricCard
                        label="Normal days"
                        value={formatCurrency(patternAnalysis.festival_impact.average_sales_normal_days, market)}
                        hint="Average sales outside holidays"
                      />
                      <MetricCard
                        label="Festival days"
                        value={formatCurrency(patternAnalysis.festival_impact.average_sales_festival_days, market)}
                        hint="Average sales on holidays"
                        accent="amber"
                      />
                      <MetricCard
                        label="Uplift"
                        value={formatPercent(patternAnalysis.festival_impact.uplift_percentage)}
                        hint="Relative difference"
                        accent={patternAnalysis.festival_impact.uplift_percentage >= 0 ? 'emerald' : 'rose'}
                      />
                    </div>
                    {patternAnalysis.festival_impact.resolution_note ? (
                      <p className="mt-4 text-sm text-slate-500">{patternAnalysis.festival_impact.resolution_note}</p>
                    ) : null}
                    {patternAnalysis.top_festivals?.length ? (
                      <div className="mt-4 space-y-2 text-sm text-slate-700">
                        {patternAnalysis.top_festivals.map((festival) => (
                          <div
                            key={festival.festival}
                            className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3"
                          >
                            <span>{festival.festival}</span>
                            <span className="font-semibold text-slate-900">
                              {formatCurrency(festival.average_sales, market)}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : null}
                  </div>
                </div>
              </section>

              {!selectedProduct ? (
                <TopProductsTable products={patternAnalysis.top_products} onFocus={focusOnProduct} marketCode={market} />
              ) : null}

              <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-4 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">AI Analyst</p>
                    <h3 className="text-2xl font-semibold text-slate-900">AI analyst brief</h3>
                    <p className="mt-2 text-sm text-slate-600">
                      Get a short brief with the core problem, where to focus now, and a future sales strategy.
                    </p>
                  </div>
                  <div className="w-full md:w-64">
                    <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="ai-language">
                      Response language
                    </label>
                    <select
                      id="ai-language"
                      value={aiLanguage}
                      onChange={(event) => setAiLanguage(event.target.value)}
                      className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-slate-900 outline-none transition focus:border-slate-900"
                    >
                      <option>English</option>
                      <option>Hindi</option>
                      <option>Marathi</option>
                      <option>Bengali</option>
                      <option>Telugu</option>
                      <option>Tamil</option>
                      <option>Malayalam</option>
                    </select>
                  </div>
                </div>
                <div className="flex flex-wrap gap-3">
                  <button
                    type="button"
                    onClick={fetchAiInsights}
                    disabled={aiLoading}
                    className="rounded-full bg-slate-900 px-5 py-3 text-sm font-semibold uppercase tracking-[0.12em] text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {aiLoading ? 'Generating brief' : 'Generate short brief'}
                  </button>
                </div>
                {aiInsights ? (
                  <div className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 p-6 whitespace-pre-line text-sm leading-7 text-slate-700">
                    {aiInsights}
                  </div>
                ) : null}
              </section>
            </>
          ) : null}

        </div>
      </main>
    </div>
  );
}

export default App;
