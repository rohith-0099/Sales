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
} from 'recharts';

function formatCurrency(value) {
  const number = Number(value ?? 0);
  return new Intl.NumberFormat('en-IN', {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  }).format(Number.isFinite(number) ? number : 0);
}

function ForecastChart({ historicalData = [], forecastData = [], festivals = [], granularity = 'daily' }) {
  const combinedData = [
    ...historicalData.map((point) => ({ ...point, series: 'Historical' })),
    ...forecastData.map((point) => ({ ...point, series: 'Forecast' })),
  ];
  const forecastBoundary = historicalData.length ? historicalData[historicalData.length - 1].date : null;

  const tooltip = ({ active, payload }) => {
    if (!active || !payload?.length) {
      return null;
    }

    const point = payload[0].payload;
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-lg">
        <p className="text-sm font-semibold text-slate-900">{point.date}</p>
        {point.sales !== undefined && (
          <p className="mt-2 text-sm text-slate-600">
            Historical sales: <span className="font-semibold text-slate-900">{formatCurrency(point.sales)}</span>
          </p>
        )}
        {point.predicted_sales !== undefined && (
          <>
            <p className="text-sm text-slate-600">
              Forecast sales:{' '}
              <span className="font-semibold text-emerald-700">{formatCurrency(point.predicted_sales)}</span>
            </p>
            <p className="text-xs text-slate-500">
              Range: {formatCurrency(point.lower_bound)} to {formatCurrency(point.upper_bound)}
            </p>
          </>
        )}
      </div>
    );
  };

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
          <YAxis tick={{ fontSize: 12, fill: '#475569' }} />
          <Tooltip content={tooltip} />
          <Legend />
          {forecastBoundary ? (
            <ReferenceLine
              x={forecastBoundary}
              stroke="#94a3b8"
              strokeDasharray="4 4"
              label={{ value: 'Forecast starts', fill: '#64748b', fontSize: 12, position: 'insideTopRight' }}
            />
          ) : null}
          {festivals.map((festival) => (
            <ReferenceLine
              key={`${festival.date}-${festival.festival}`}
              x={festival.date}
              stroke="#7c3aed"
              strokeDasharray="3 3"
            />
          ))}
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
