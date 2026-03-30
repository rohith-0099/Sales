import { useEffect, useState } from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

function formatCurrency(value, marketCode = 'IN') {
  const number = Number(value ?? 0);
  const locales = { IN: 'en-IN', US: 'en-US', GB: 'en-GB', AE: 'en-AE', AU: 'en-AU', CA: 'en-CA' };
  const currencies = { IN: 'INR', US: 'USD', GB: 'GBP', AE: 'AED', AU: 'AUD', CA: 'CAD' };

  return new Intl.NumberFormat(locales[marketCode] || 'en-US', {
    style: 'currency',
    currency: currencies[marketCode] || 'USD',
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  }).format(Number.isFinite(number) ? number : 0);
}

const CustomTooltip = ({ active, payload, marketCode }) => {
  if (!active || !payload?.length) {
    return null;
  }

  const point = payload[0].payload;

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-lg">
      <p className="text-sm font-semibold text-slate-900">{point.date}</p>
      {point.sales !== undefined ? (
        <p className="mt-2 text-sm text-slate-600">
          Historical sales: <span className="font-semibold text-slate-900">{formatCurrency(point.sales, marketCode)}</span>
        </p>
      ) : null}
      {point.predicted_sales !== undefined ? (
        <>
          <p className="text-sm text-slate-600">
            Forecast sales:{' '}
            <span className="font-semibold text-emerald-700">{formatCurrency(point.predicted_sales, marketCode)}</span>
          </p>
          <p className="text-xs text-slate-500">
            Range: {formatCurrency(point.lower_bound, marketCode)} to {formatCurrency(point.upper_bound, marketCode)}
          </p>
        </>
      ) : null}
    </div>
  );
};

function ForecastChart({
  historicalData = [],
  forecastData = [],
  festivals = [],
  granularity = 'daily',
  marketCode = 'IN',
  confidence,
  metrics,
}) {
  const [isExpanded, setIsExpanded] = useState(false);
  const combinedData = [
    ...historicalData.map((point) => ({ ...point, series: 'Historical' })),
    ...forecastData.map((point) => ({ ...point, series: 'Forecast' })),
  ];
  const forecastBoundary = historicalData.length ? historicalData[historicalData.length - 1].date : null;
  const isHighConfidence = String(confidence || '').toLowerCase().startsWith('high');

  useEffect(() => {
    if (!isExpanded) {
      return undefined;
    }

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        setIsExpanded(false);
      }
    };

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isExpanded]);

  function renderChartCard(expanded = false) {
    const chartHeight = expanded ? 620 : 420;
    const visibleFestivalItems = expanded ? festivals : festivals.slice(0, 12);
    const hiddenFestivalCount = Math.max(festivals.length - visibleFestivalItems.length, 0);
    const hasForecastQuality = Boolean(confidence || metrics);

    return (
      <div className={expanded ? 'flex h-full flex-col' : 'rounded-3xl border border-slate-200 bg-white p-6 shadow-sm'}>
        <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div className="min-w-0">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Forecast View</p>
            <h3 className="text-2xl font-semibold text-slate-900">Historical trend and future projection</h3>
            <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-slate-600">
              <span className="inline-flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-teal-700" />
                Historical sales
              </span>
              <span className="inline-flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-orange-600" />
                Forecast sales
              </span>
              <span className="inline-flex items-center gap-2">
                <span className="h-0.5 w-5 border-t-2 border-dashed border-amber-500" />
                Festival markers
              </span>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-3 md:justify-end">
            <p className="text-sm text-slate-500">Detected granularity: {granularity}</p>
            <button
              type="button"
              onClick={() => setIsExpanded((currentState) => !currentState)}
              className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-900 hover:text-slate-900"
            >
              {expanded ? 'Close expanded view' : 'Expand view'}
            </button>
          </div>
        </div>

        <div style={{ height: chartHeight }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={combinedData}
              margin={{
                top: expanded ? 42 : 32,
                right: expanded ? 18 : 8,
                left: expanded ? 6 : 0,
                bottom: 4,
              }}
            >
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
              <XAxis
                dataKey="date"
                tick={{ fontSize: expanded ? 12 : 11, fill: '#475569' }}
                minTickGap={expanded ? 20 : 34}
              />
              <YAxis
                width={expanded ? 74 : 58}
                tickFormatter={(value) => new Intl.NumberFormat('en-US', { notation: 'compact' }).format(value)}
                stroke="#94a3b8"
                fontSize={12}
              />
              <Tooltip content={<CustomTooltip marketCode={marketCode} />} />

              {forecastBoundary ? (
                <ReferenceLine
                  x={forecastBoundary}
                  stroke="#94a3b8"
                  strokeDasharray="4 4"
                  label={{ value: 'Forecast starts', fill: '#64748b', fontSize: 12, position: 'insideTopRight' }}
                />
              ) : null}

              {festivals.map((festival, index) => (
                <ReferenceLine
                  key={`${festival.date}-${index}`}
                  x={festival.date}
                  stroke="#f59e0b"
                  strokeDasharray="3 3"
                  strokeWidth={1}
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

        {hasForecastQuality ? (
          <div className="mt-5 rounded-2xl border border-slate-200 bg-slate-50/80 p-4">
            <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Forecast Quality</p>
                <p className="mt-1 text-sm text-slate-600">
                  This label is based on ensemble behavior and available training history, so it is shown outside the chart as forecast metadata.
                </p>
              </div>
              <span
                className={`inline-flex w-fit rounded-full px-3 py-1 text-sm font-semibold ${
                  isHighConfidence ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
                }`}
              >
                {confidence || 'Analysis Pending'}
              </span>
            </div>

            {metrics ? (
              <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3">
                  <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">RMSE</p>
                  <p className="mt-2 text-lg font-semibold text-slate-900">{metrics.rmse?.toFixed(2) || 'N/A'}</p>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3">
                  <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">MAE</p>
                  <p className="mt-2 text-lg font-semibold text-slate-900">{metrics.mae?.toFixed(2) || 'N/A'}</p>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3">
                  <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">Rows Trained</p>
                  <p className="mt-2 text-lg font-semibold text-slate-900">{metrics.row_count || '0'}</p>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3">
                  <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">Scope</p>
                  <p className="mt-2 break-words text-lg font-semibold text-slate-900">{metrics.scope || 'forecast'}</p>
                </div>
              </div>
            ) : null}
          </div>
        ) : null}

        {festivals.length ? (
          <div className="mt-5 rounded-2xl border border-slate-200 bg-slate-50/80 p-4">
            <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Festival Markers</p>
                <p className="mt-1 text-sm text-slate-600">
                  Amber dashed lines on the chart match the festival dates listed here.
                </p>
              </div>
              <p className="text-sm font-medium text-slate-500">
                {festivals.length} festival{festivals.length === 1 ? '' : 's'} in view
              </p>
            </div>

            <div className={`mt-4 grid gap-2 ${expanded ? 'max-h-40 overflow-y-auto pr-1 md:grid-cols-3' : 'md:grid-cols-2 xl:grid-cols-3'}`}>
              {visibleFestivalItems.map((festival, index) => (
                <div
                  key={`${festival.date}-${festival.festival}-${index}`}
                  className="rounded-2xl border border-amber-200 bg-white px-3 py-2"
                >
                  <p className="text-xs font-semibold uppercase tracking-[0.12em] text-amber-700">{festival.date}</p>
                  <p className="mt-1 break-words text-sm font-medium text-slate-800">{festival.festival}</p>
                  {festival.category ? <p className="mt-1 text-xs text-slate-500">{festival.category}</p> : null}
                </div>
              ))}
            </div>

            {hiddenFestivalCount > 0 ? (
              <p className="mt-3 text-xs text-slate-500">
                Showing the first {visibleFestivalItems.length} festivals here. Use expanded view to see the full list.
              </p>
            ) : null}
          </div>
        ) : null}
      </div>
    );
  }

  return (
    <>
      {renderChartCard(false)}
      {isExpanded ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 p-4 backdrop-blur-sm">
          <div className="max-h-[95vh] w-full max-w-7xl overflow-auto rounded-[2rem] border border-slate-200 bg-white p-6 shadow-2xl">
            {renderChartCard(true)}
          </div>
        </div>
      ) : null}
    </>
  );
}

export default ForecastChart;
