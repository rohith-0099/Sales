import re
import traceback

try:
    with open('c:/Users/rohit/Desktop/sales-prediction-system/frontend/src/App.jsx', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. formatCurrency definition
    old_format = """function formatCurrency(value) {
  const numericValue = Number(value ?? 0);
  return new Intl.NumberFormat('en-IN', {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  }).format(Number.isFinite(numericValue) ? numericValue : 0);
}"""

    new_format = """export const MARKETS = [
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
}"""
    content = content.replace(old_format, new_format)

    # 2. Add market to state
    content = content.replace("function App() {\n  const [uploadId", "function App() {\n  const [market, setMarket] = useState('IN');\n  const [uploadId")

    # 3. Add marketCode to functional components
    content = content.replace("function TopProductsTable({ products, onFocus }) {", "function TopProductsTable({ products, onFocus, marketCode }) {")
    content = content.replace("function TrendTable({ periods }) {", "function TrendTable({ periods, marketCode }) {")
    content = content.replace("<TopProductsTable products={patternAnalysis.top_products} onFocus={focusOnProduct} />", "<TopProductsTable products={patternAnalysis.top_products} onFocus={focusOnProduct} marketCode={market} />")
    content = content.replace("<TrendTable periods={patternAnalysis.period_trends} />", "<TrendTable periods={patternAnalysis.period_trends} marketCode={market} />")

    # 4. Replace formatCurrency calls strictly inside App.jsx
    content = re.sub(r'formatCurrency\(product\.total_sales\)', 'formatCurrency(product.total_sales, marketCode)', content)
    content = re.sub(r'formatCurrency\(product\.average_sales\)', 'formatCurrency(product.average_sales, marketCode)', content)
    content = re.sub(r'formatCurrency\(period\.total_sales\)', 'formatCurrency(period.total_sales, marketCode)', content)
    content = re.sub(r'formatCurrency\(period\.average_sales\)', 'formatCurrency(period.average_sales, marketCode)', content)

    # For App component (using global `market` state)
    def app_replacer(m):
        full = m.group(0)
        inner = m.group(1).strip()
        if 'marketCode' in full or 'm.currency' in full or inner == 'value' or inner == 'legacyPrediction':
            return full
        return f'formatCurrency({inner}, market)'

    content = re.sub(r'formatCurrency\(([^)]+)\)', app_replacer, content)
    # Fix the missing replacements if legacyPrediction got skipped, since legacy is always IN or maybe should be market
    content = content.replace('formatCurrency(legacyPrediction)', 'formatCurrency(legacyPrediction, market)')

    # 5. APIs: payload modifications
    content = content.replace("selected_product: normalizedProduct || null,", "selected_product: normalizedProduct || null,\n        country_code: market,")
    content = content.replace("context: buildAiContext(),", "context: buildAiContext(),\n        country_code: market,")

    # 6. Header
    old_header2 = """          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-amber-600">
            Retail Intelligence Platform
          </p>
          <div className="mt-4 grid gap-6 lg:grid-cols-[1.7fr_1fr] lg:items-end">"""

    new_header2 = """          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
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
          <div className="mt-4 grid gap-6 lg:grid-cols-[1.7fr_1fr] lg:items-end">"""
    
    content = content.replace(old_header2, new_header2)

    # 7. Add marketCode to ForecastChart component rendering
    content = content.replace("granularity={granularity}", "granularity={granularity}\n                marketCode={market}")

    with open('c:/Users/rohit/Desktop/sales-prediction-system/frontend/src/App.jsx', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully updated App.jsx")

    with open('c:/Users/rohit/Desktop/sales-prediction-system/frontend/src/components/ForecastChart.jsx', 'r', encoding='utf-8') as f:
        chart_content = f.read()

    old_chart_format = """function formatCurrency(value) {
  const number = Number(value ?? 0);
  return new Intl.NumberFormat('en-IN', {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  }).format(Number.isFinite(number) ? number : 0);
}"""

    new_chart_format = """function formatCurrency(value, marketCode = 'IN') {
  const number = Number(value ?? 0);
  const locales = { 'IN': 'en-IN', 'US': 'en-US', 'GB': 'en-GB', 'AE': 'en-AE', 'AU': 'en-AU', 'CA': 'en-CA' };
  const currencies = { 'IN': 'INR', 'US': 'USD', 'GB': 'GBP', 'AE': 'AED', 'AU': 'AUD', 'CA': 'CAD' };
  return new Intl.NumberFormat(locales[marketCode] || 'en-US', {
    style: 'currency',
    currency: currencies[marketCode] || 'USD',
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  }).format(Number.isFinite(number) ? number : 0);
}"""

    chart_content = chart_content.replace(old_chart_format, new_chart_format)
    chart_content = chart_content.replace("function ForecastChart({ historicalData = [], forecastData = [], festivals = [], granularity = 'daily' }) {", "function ForecastChart({ historicalData = [], forecastData = [], festivals = [], granularity = 'daily', marketCode = 'IN' }) {")

    def chart_replacer(m):
        full = m.group(0)
        inner = m.group(1).strip()
        if 'marketCode' in full or inner == 'value':
            return full
        return f'formatCurrency({inner}, marketCode)'

    chart_content = re.sub(r'formatCurrency\(([^)]+)\)', chart_replacer, chart_content)

    with open('c:/Users/rohit/Desktop/sales-prediction-system/frontend/src/components/ForecastChart.jsx', 'w', encoding='utf-8') as f:
        f.write(chart_content)
    print("Successfully updated ForecastChart.jsx")

except Exception as e:
    print(traceback.format_exc())
