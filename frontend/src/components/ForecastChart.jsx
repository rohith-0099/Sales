import { useEffect, useState } from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  Label,
  Legend,
  ReferenceArea,
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

function formatFestivalLabel(label, expanded) {
  if (!label) {
    return '';
  }

  const maxLength = expanded ? 22 : 14;
  return label.length > maxLength ? `${label.slice(0, maxLength - 1)}...` : label;
}

function getLabeledFestivalDates(festivals, expanded) {
  const sortedFestivals = [...festivals]
    .filter((festival) => festival?.date)
    .sort((left, right) => new Date(left.date) - new Date(right.date));

  if (sortedFestivals.length <= (expanded ? 14 : 8)) {
    return new Set(sortedFestivals.map((festival) => festival.date));
  }

  const minimumGapDays = expanded ? 12 : 21;
  const minimumGapMs = minimumGapDays * 24 * 60 * 60 * 1000;
  const labeledDates = new Set();
  let lastLabeledTs = Number.NEGATIVE_INFINITY;

  for (const festival of sortedFestivals) {
    const currentTs = new Date(festival.date).getTime();
    if (!Number.isFinite(currentTs)) {
      continue;
    }

    if (currentTs - lastLabeledTs >= minimumGapMs) {
      labeledDates.add(festival.date);
      lastLabeledTs = currentTs;
    }
  }

  return labeledDates;
}

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
  const compactFestivalLabels = getLabeledFestivalDates(festivals, false);
  const expandedFestivalLabels = getLabeledFestivalDates(festivals, true);

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
    const labeledFestivals = expanded ? expandedFestivalLabels : compactFestivalLabels;
    const showFestivalNote = festivals.length > labeledFestivals.size;

    return (
      <div className={expanded ? 'flex h-full flex-col' : 'rounded-3xl border border-slate-200 bg-white p-6 shadow-sm'}>
        <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div className="min-w-0">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Forecast View</p>
            <h3 className="text-2xl font-semibold text-slate-900">Historical trend and future projection</h3>
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
              <Legend
                verticalAlign="top"
                align="right"
                iconType="circle"
                height={expanded ? 42 : 36}
                wrapperStyle={{ fontSize: expanded ? '14px' : '12px' }}
              />

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
                  label={
                    labeledFestivals.has(festival.date)
                      ? {
                          value: formatFestivalLabel(festival.festival, expanded),
                          position: 'top',
                          fill: '#d97706',
                          fontSize: expanded ? 10 : 9,
                          fontWeight: 600,
                        }
                      : undefined
                  }
                />
              ))}

              {forecastData.length > 0 ? (
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
                          <foreignObject x={x + 10} y={y + (expanded ? 140 : 110)} width={expanded ? 220 : 200} height="150">
                            <div className="flex flex-col gap-2 rounded-xl border border-slate-200 bg-white/80 p-3 shadow-sm backdrop-blur-sm">
                              <div className="flex items-center justify-between gap-2">
                                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Confidence</span>
                                <span
                                  className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                                    isHighConfidence ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
                                  }`}
                                >
                                  {confidence || 'Analysis Pending'}
                                </span>
                              </div>
                              {metrics ? (
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
                              ) : null}
                            </div>
                          </foreignObject>
                        </g>
                      );
                    }}
                  />
                </ReferenceArea>
              ) : null}

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

        {showFestivalNote ? (
          <p className="mt-4 text-xs text-slate-500">
            Festival labels are sampled in the compact view to avoid overlap. Expand the chart for a wider forecast view.
          </p>
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
