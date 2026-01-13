import React from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
    ResponsiveContainer, Area, AreaChart, ReferenceLine
} from 'recharts';

function ForecastChart({ historicalData, forecastData, festivals }) {
    // Combine historical and forecast data
    const combinedData = [
        ...historicalData.map(d => ({ ...d, type: 'historical' })),
        ...forecastData.map(d => ({ ...d, type: 'forecast' }))
    ];

    // Custom tooltip
    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-200">
                    <p className="font-semibold text-gray-800">{data.date}</p>
                    {data.sales && (
                        <p className="text-sm text-gray-600">
                            Actual Sales: <span className="font-medium text-blue-600">${data.sales.toFixed(2)}</span>
                        </p>
                    )}
                    {data.predicted_sales && (
                        <>
                            <p className="text-sm text-gray-600">
                                Predicted: <span className="font-medium text-green-600">${data.predicted_sales.toFixed(2)}</span>
                            </p>
                            {data.lower_bound && data.upper_bound && (
                                <p className="text-xs text-gray-500 mt-1">
                                    Range: ${data.lower_bound.toFixed(2)} - ${data.upper_bound.toFixed(2)}
                                </p>
                            )}
                        </>
                    )}
                    {data.festival && (
                        <p className="text-sm font-medium text-purple-600 mt-1">
                            🎉 {data.festival}
                        </p>
                    )}
                </div>
            );
        }
        return null;
    };

    return (
        <div className="chart-container">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
                Sales Forecast with Festival Impact
            </h3>
            <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={combinedData}>
                    <defs>
                        <linearGradient id="colorHistorical" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis
                        dataKey="date"
                        tick={{ fontSize: 12 }}
                        stroke="#6b7280"
                    />
                    <YAxis
                        tick={{ fontSize: 12 }}
                        stroke="#6b7280"
                        label={{ value: 'Sales ($)', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />

                    {/* Historical Data */}
                    <Area
                        type="monotone"
                        dataKey="sales"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        fill="url(#colorHistorical)"
                        name="Historical Sales"
                    />

                    {/* Forecast Data */}
                    <Area
                        type="monotone"
                        dataKey="predicted_sales"
                        stroke="#10b981"
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        fill="url(#colorForecast)"
                        name="Predicted Sales"
                    />

                    {/* Festival markers */}
                    {festivals && festivals.map((festival, idx) => (
                        <ReferenceLine
                            key={idx}
                            x={festival.date}
                            stroke="#8b5cf6"
                            strokeDasharray="3 3"
                            label={{ value: '🎉', position: 'top' }}
                        />
                    ))}
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}

export default ForecastChart;
