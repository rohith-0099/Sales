import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  ReferenceArea,
  Label,
} from 'recharts';

function formatCurrency(value, marketCode = 'IN') {
  const number = Number(value ?? 0);
  const locales = { 'IN': 'en-IN', 'US': 'en-US', 'GB': 'en-GB', 'AE': 'en-AE', 'AU': 'en-AU', 'CA': 'en-CA' };
  const currencies = { 'IN': 'INR', 'US': 'USD', 'GB': 'GBP', 'AE': 'AED', 'AU': 'AUD', 'CA': 'CAD' };
  return new Intl.NumberFormat(locales[marketCode] || 'en-US', {
    style: 'currency',
    currency: currencies[marketCode] || 'USD',
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  }).format(Number.isFinite(number) ? number : 0);
}

// CustomTooltip component (assuming it's defined elsewhere or will be added by the user)
// For the purpose of this edit, we'll define a basic one to make the code syntactically correct.
const CustomTooltip = ({ active, payload, marketCode }) => {
  if (!active || !payload?.length) {
    return null;
  }

  const point = payload[0].payload;
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-lg">
      <p className="text-sm font-semibold text-slate-900">{point.date}</p>
      {point.sales !== undefined && (
        <p className="mt-2 text-sm text-slate-600">
          Historical sales: <span className="font-semibold text-slate-900">{formatCurrency(point.sales, marketCode)}</span>
        </p>
      )}
      {point.predicted_sales !== undefined && (
        <>
          <p className="text-sm text-slate-600">
            Forecast sales:{' '}
            <span className="font-semibold text-emerald-700">{formatCurrency(point.predicted_sales, marketCode)}</span>
          </p>
          <p className="text-xs text-slate-500">
            Range: {formatCurrency(point.lower_bound, marketCode)} to {formatCurrency(point.upper_bound, marketCode)}
          </p>
        </>
      )}
    </div>
  );
};


function ForecastChart({ historicalData = [], forecastData = [], festivals = [], granularity = 'daily', marketCode = 'IN', confidence, metrics }) {
  const combinedData = [
    ...historicalData.map((point) => ({ ...point, series: 'Historical' })),
    ...forecastData.map((point) => ({ ...point, series: 'Forecast' })),
  ];
  const forecastBoundary = historicalData.length ? historicalData[historicalData.length - 1].date : null;


  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-5 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Forecast View</p>
          <h3 className="text-2xl font-semibold text-slate-900">Historical trend and future projection</h3>
        </div>
        <p className="text-sm text-slate-500">Detected granularity: {granularity}</p>
      </div>

      <ResponsiveContainer width="100%" height={420}>
        <AreaChart data={combinedData}>
          <defs>
            <linearGradient id="historicalFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#0f766e" stopOpacity={0.22} />
              <stop offset="95%" stopColor="#0f766e" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="forecastFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ea580c" stopOpacity={0.24} />
              <stop offset="95%" stopColor="#ea580c" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 12, fill: '#475569' }} minTickGap={24} />
          <YAxis
            tickFormatter={(val) => new Intl.NumberFormat('en-US', { notation: 'compact' }).format(val)}
            stroke="#94a3b8"
            fontSize={12}
          />
          <Tooltip content={<CustomTooltip marketCode={marketCode} />} />
          <Legend verticalAlign="top" height={36} />

          {forecastBoundary ? (
            <ReferenceLine
              x={forecastBoundary}
              stroke="#94a3b8"
              strokeDasharray="4 4"
              label={{ value: 'Forecast starts', fill: '#64748b', fontSize: 12, position: 'insideTopRight' }}
            />
          ) : null}
          {/* Festival Markers */}
          {festivals.map((fest, idx) => (
            <ReferenceLine
              key={`${fest.date}-${idx}`}
              x={fest.date}
              stroke="#f59e0b"
              strokeDasharray="3 3"
              strokeWidth={1}
              label={{
                value: fest.festival,
                position: 'top',
                fill: '#d97706',
                fontSize: 10,
                fontWeight: 600
              }}
            />
          ))}

          {/* Confidence & Metrics Overlay */}
          {forecastData.length > 0 && (
            <ReferenceArea
              x1={forecastData[0]?.date}
              x2={forecastData[forecastData.length - 1]?.date}
              fill="#f8fafc"
              fillOpacity={0.5}
              strokeOpacity={0.3}
            >
              <Label
                content={({ viewBox }) => {
                  const { x, y } = viewBox;
                  return (
                    <g>
                      <foreignObject x={x + 10} y={y + 110} width="200" height="150">
                        <div className="flex flex-col gap-2 rounded-xl border border-slate-200 bg-white/80 p-3 shadow-sm backdrop-blur-sm">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Confidence</span>
                            <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                              confidence === 'High 🟢' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
                            }`}>
                              {confidence || 'Analysis Pending'}
                            </span>
                          </div>
                          {metrics && (
                            <div className="space-y-1 border-t border-slate-100 pt-2">
                              <div className="flex justify-between text-[10px]">
                                <span className="text-slate-500">RMSE</span>
                                <span className="font-mono font-bold text-slate-800">{metrics.rmse?.toFixed(2) || 'N/A'}</span>
                              </div>
                              <div className="flex justify-between text-[10px]">
                                <span className="text-slate-500">MAE</span>
                                <span className="font-mono font-bold text-slate-800">{metrics.mae?.toFixed(2) || 'N/A'}</span>
                              </div>
                              <div className="flex justify-between text-[10px]">
                                <span className="text-slate-500">Rows Trained</span>
                                <span className="font-mono font-bold text-slate-800">{metrics.row_count || '0'}</span>
                              </div>
                            </div>
                          )}
                        </div>
                      </foreignObject>
                    </g>
                  );
                }}
              />
            </ReferenceArea>
          )}

          <Area
            type="monotone"
            dataKey="sales"
            name="Historical sales"
            stroke="#0f766e"
            strokeWidth={2}
            fill="url(#historicalFill)"
            connectNulls
          />
          <Area
            type="monotone"
            dataKey="predicted_sales"
            name="Forecast sales"
            stroke="#ea580c"
            strokeWidth={2}
            strokeDasharray="6 4"
            fill="url(#forecastFill)"
            connectNulls
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ForecastChart;
