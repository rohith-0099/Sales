import { useDeferredValue, useEffect, useState } from 'react';
import axios from 'axios';
import FileUpload from './components/FileUpload';
import ForecastChart from './components/ForecastChart';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const initialLegacyForm = {
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
  Outlet_Type: 'Supermarket Type1',
};

function formatCurrency(value) {
  const numericValue = Number(value ?? 0);
  return new Intl.NumberFormat('en-IN', {
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
    <div className={`rounded-3xl border p-5 shadow-sm ${accents[accent] || accents.slate}`}>
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">{label}</p>
      <p className="mt-3 text-3xl font-semibold">{value}</p>
      {hint ? <p className="mt-2 text-sm text-slate-600">{hint}</p> : null}
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

function TopProductsTable({ products, onFocus }) {
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
                <td className="py-3 pr-4 text-slate-700">{formatCurrency(product.total_sales)}</td>
                <td className="py-3 pr-4 text-slate-700">{formatCurrency(product.average_sales)}</td>
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

function TrendTable({ periods }) {
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
                <td className="py-3 pr-4 text-slate-700">{formatCurrency(period.total_sales)}</td>
                <td className="py-3 pr-4 text-slate-700">{formatCurrency(period.average_sales)}</td>
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
  const [patternAnalysis, setPatternAnalysis] = useState(null);
  const [aiLanguage, setAiLanguage] = useState('English');
  const [aiInsights, setAiInsights] = useState('');
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [error, setError] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [legacyFormData, setLegacyFormData] = useState(initialLegacyForm);
  const [legacyPrediction, setLegacyPrediction] = useState(null);
  const [legacyLoading, setLegacyLoading] = useState(false);

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
  }

  async function handleFileSelected(file) {
    const formData = new FormData();
    formData.append('file', file);

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
      setForecastSummary(forecastResponse.data.summary || null);
      setForecastUnit(forecastResponse.data.forecast_unit || 'days');
      setPatternAnalysis(analysisResponse.data.patterns || null);
      setGranularity(forecastResponse.data.granularity || granularity);
      setSelectedProduct(forecastResponse.data.selected_product || normalizedProduct || '');
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
      `Current run rate: ${formatCurrency(patternAnalysis.summary.current_run_rate)}.`,
      `Latest sales: ${formatCurrency(patternAnalysis.summary.latest_sales)}.`,
      `Trend direction: ${patternAnalysis.summary.trend_direction}.`,
      `Projected direction: ${forecastSummary.projected_direction}.`,
      `Projected cumulative sales: ${formatCurrency(forecastSummary.cumulative_predicted_sales)}.`,
    ].join(' ');

    try {
      const response = await axios.post(`${API_URL}/ai-insights`, {
        language: aiLanguage,
        product_name: selectedProduct || 'All products',
        summary,
        context: buildAiContext(),
      });

      if (!response.data.success) {
        throw new Error(response.data.error || 'AI insight generation failed.');
      }

      if (response.data.fallback) {
        setStatusMessage('Gemini quota is unavailable right now. Showing a local fallback insight summary.');
      }
      setAiInsights(response.data.insights || '');
    } catch (requestError) {
      setError(getRequestErrorMessage(requestError, 'AI insight generation failed.'));
    } finally {
      setAiLoading(false);
    }
  }

  function handleLegacyFormChange(event) {
    const { name, value } = event.target;
    setLegacyFormData((previousState) => ({ ...previousState, [name]: value }));
  }

  async function submitLegacyPrediction(event) {
    event.preventDefault();
    setLegacyLoading(true);
    setLegacyPrediction(null);
    setError('');

    try {
      const payload = {
        ...legacyFormData,
        Item_Weight: Number(legacyFormData.Item_Weight),
        Item_Visibility: Number(legacyFormData.Item_Visibility),
        Item_MRP: Number(legacyFormData.Item_MRP),
        Outlet_Establishment_Year: Number(legacyFormData.Outlet_Establishment_Year),
      };

      const response = await axios.post(`${API_URL}/predict`, payload);
      if (!response.data.success) {
        throw new Error(response.data.error || 'Legacy prediction failed.');
      }

      setLegacyPrediction(response.data.predicted_sales);
    } catch (requestError) {
      setError(getRequestErrorMessage(requestError, 'Legacy prediction failed.'));
    } finally {
      setLegacyLoading(false);
    }
  }

  const analysisReady = Boolean(patternAnalysis && forecastSummary);

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(253,224,71,0.18),_transparent_28%),linear-gradient(180deg,_#fffef6_0%,_#f8fafc_42%,_#eef2ff_100%)]">
      <header className="border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-amber-600">
            Retail Intelligence Platform
          </p>
          <div className="mt-4 grid gap-6 lg:grid-cols-[1.7fr_1fr] lg:items-end">
            <div>
              <h1 className="max-w-4xl text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
                Upload retail sales data, inspect product-level trends, and forecast what comes next.
              </h1>
              <p className="mt-4 max-w-3xl text-lg leading-8 text-slate-600">
                The dashboard accepts daily, weekly, monthly, or yearly retail sales data, identifies product
                entities automatically, generates forecasts, and explains the pattern in multiple languages with
                Gemini.
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
                  value={formatCurrency(uploadStats.total_sales)}
                  hint={`${uploadStats.rows} parsed rows`}
                  accent="emerald"
                />
                <MetricCard
                  label="Average sales"
                  value={formatCurrency(uploadStats.average_sales)}
                  hint={`Latest sale ${formatCurrency(uploadStats.latest_sales)}`}
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
                  value={formatCurrency(patternAnalysis.summary.total_sales)}
                  hint={`Range ${patternAnalysis.summary.start_date} to ${patternAnalysis.summary.end_date}`}
                  accent="emerald"
                />
                <MetricCard
                  label="Current run rate"
                  value={formatCurrency(patternAnalysis.summary.current_run_rate)}
                  hint={`Previous run rate ${formatCurrency(patternAnalysis.summary.previous_run_rate)}`}
                />
                <MetricCard
                  label="Growth"
                  value={formatPercent(patternAnalysis.summary.growth_pct)}
                  hint={`Trend is ${patternAnalysis.summary.trend_direction}`}
                  accent={patternAnalysis.summary.growth_pct >= 0 ? 'amber' : 'rose'}
                />
                <MetricCard
                  label="Forecast total"
                  value={formatCurrency(forecastSummary.cumulative_predicted_sales)}
                  hint={`Across the next ${forecastData.length} ${forecastUnit}`}
                  accent="amber"
                />
              </section>

              {forecastSummary.comparison_to_current ? (
                <section className="grid gap-4 md:grid-cols-3">
                  <MetricCard
                    label="Current average sales"
                    value={formatCurrency(forecastSummary.comparison_to_current.current_average_sales)}
                    hint={`Based on the latest ${forecastSummary.comparison_to_current.baseline_window_points} data points`}
                  />
                  <MetricCard
                    label="Predicted average sales"
                    value={formatCurrency(forecastSummary.comparison_to_current.forecast_average_sales)}
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
                      value={formatCurrency(patternAnalysis.selected_product_stats.total_sales)}
                      hint={`${patternAnalysis.selected_product_stats.records} records`}
                    />
                    <MetricCard
                      label="Average product sale"
                      value={formatCurrency(patternAnalysis.selected_product_stats.average_sales)}
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
                festivals={[]}
                granularity={granularity}
              />

              <section className="grid gap-6 lg:grid-cols-2">
                <TrendTable periods={patternAnalysis.period_trends} />

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
                          with {formatCurrency(patternAnalysis.trend_highlights.best_period.total_sales)} in sales.
                        </p>
                      ) : null}
                      {patternAnalysis.trend_highlights.weakest_period ? (
                        <p>
                          Weakest period:{' '}
                          <span className="font-semibold text-slate-900">{patternAnalysis.trend_highlights.weakest_period.label}</span>{' '}
                          with {formatCurrency(patternAnalysis.trend_highlights.weakest_period.total_sales)} in sales.
                        </p>
                      ) : null}
                      <p>
                        Forecast direction:{' '}
                        <span className="font-semibold text-slate-900">{forecastSummary.projected_direction}</span>
                      </p>
                      <p>
                        Forecast peak: <span className="font-semibold text-slate-900">{forecastSummary.peak_forecast_date}</span>{' '}
                        at {formatCurrency(forecastSummary.peak_forecast_sales)}.
                      </p>
                    </div>
                  </div>

                  <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Festival effect</p>
                    <h3 className="mt-2 text-2xl font-semibold text-slate-900">Holiday sensitivity</h3>
                    <div className="mt-4 grid gap-4 md:grid-cols-3">
                      <MetricCard
                        label="Normal days"
                        value={formatCurrency(patternAnalysis.festival_impact.average_sales_normal_days)}
                        hint="Average sales outside holidays"
                      />
                      <MetricCard
                        label="Festival days"
                        value={formatCurrency(patternAnalysis.festival_impact.average_sales_festival_days)}
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
                              {formatCurrency(festival.average_sales)}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : null}
                  </div>
                </div>
              </section>

              {!selectedProduct ? (
                <TopProductsTable products={patternAnalysis.top_products} onFocus={focusOnProduct} />
              ) : null}

              <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-4 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">AI Analyst</p>
                    <h3 className="text-2xl font-semibold text-slate-900">Gemini sales explanation</h3>
                    <p className="mt-2 text-sm text-slate-600">
                      Ask Gemini to explain the trend, identify where to focus, and suggest actions to improve sales.
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
                    {aiLoading ? 'Generating insight' : 'Generate AI insight'}
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

          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Legacy model</p>
              <h2 className="mt-2 text-2xl font-semibold text-slate-900">Single-item prediction endpoint</h2>
              <p className="mt-2 max-w-3xl text-sm text-slate-600">
                This form remains available for the original attribute-driven prediction API. It is separate from
                the uploaded time-series analysis flow.
              </p>
            </div>
            <form onSubmit={submitLegacyPrediction} className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <input
                type="text"
                name="Item_Identifier"
                value={legacyFormData.Item_Identifier}
                onChange={handleLegacyFormChange}
                placeholder="Item identifier"
                className="rounded-2xl border border-slate-300 px-4 py-3"
                required
              />
              <input
                type="number"
                step="0.01"
                name="Item_Weight"
                value={legacyFormData.Item_Weight}
                onChange={handleLegacyFormChange}
                placeholder="Weight"
                className="rounded-2xl border border-slate-300 px-4 py-3"
                required
              />
              <input
                type="number"
                step="0.0001"
                name="Item_Visibility"
                value={legacyFormData.Item_Visibility}
                onChange={handleLegacyFormChange}
                placeholder="Visibility"
                className="rounded-2xl border border-slate-300 px-4 py-3"
                required
              />
              <input
                type="number"
                step="0.01"
                name="Item_MRP"
                value={legacyFormData.Item_MRP}
                onChange={handleLegacyFormChange}
                placeholder="MRP"
                className="rounded-2xl border border-slate-300 px-4 py-3"
                required
              />
              <input
                type="text"
                name="Item_Type"
                value={legacyFormData.Item_Type}
                onChange={handleLegacyFormChange}
                placeholder="Item type"
                className="rounded-2xl border border-slate-300 px-4 py-3"
                required
              />
              <select
                name="Item_Fat_Content"
                value={legacyFormData.Item_Fat_Content}
                onChange={handleLegacyFormChange}
                className="rounded-2xl border border-slate-300 px-4 py-3"
              >
                <option value="Low Fat">Low Fat</option>
                <option value="Regular">Regular</option>
              </select>
              <input
                type="text"
                name="Outlet_Identifier"
                value={legacyFormData.Outlet_Identifier}
                onChange={handleLegacyFormChange}
                placeholder="Outlet identifier"
                className="rounded-2xl border border-slate-300 px-4 py-3"
                required
              />
              <input
                type="number"
                name="Outlet_Establishment_Year"
                value={legacyFormData.Outlet_Establishment_Year}
                onChange={handleLegacyFormChange}
                placeholder="Established year"
                className="rounded-2xl border border-slate-300 px-4 py-3"
                required
              />
              <select
                name="Outlet_Size"
                value={legacyFormData.Outlet_Size}
                onChange={handleLegacyFormChange}
                className="rounded-2xl border border-slate-300 px-4 py-3"
              >
                <option value="Small">Small</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
              <select
                name="Outlet_Location_Type"
                value={legacyFormData.Outlet_Location_Type}
                onChange={handleLegacyFormChange}
                className="rounded-2xl border border-slate-300 px-4 py-3"
              >
                <option value="Tier 1">Tier 1</option>
                <option value="Tier 2">Tier 2</option>
                <option value="Tier 3">Tier 3</option>
              </select>
              <select
                name="Outlet_Type"
                value={legacyFormData.Outlet_Type}
                onChange={handleLegacyFormChange}
                className="rounded-2xl border border-slate-300 px-4 py-3"
              >
                <option value="Supermarket Type1">Supermarket Type1</option>
                <option value="Supermarket Type2">Supermarket Type2</option>
                <option value="Supermarket Type3">Supermarket Type3</option>
                <option value="Grocery Store">Grocery Store</option>
              </select>
              <button
                type="submit"
                disabled={legacyLoading}
                className="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold uppercase tracking-[0.12em] text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {legacyLoading ? 'Predicting' : 'Run legacy prediction'}
              </button>
            </form>
            {legacyPrediction !== null ? (
              <div className="mt-5 rounded-3xl border border-emerald-200 bg-emerald-50 p-5">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700">Prediction result</p>
                <p className="mt-3 text-3xl font-semibold text-emerald-900">{formatCurrency(legacyPrediction)}</p>
              </div>
            ) : null}
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;
