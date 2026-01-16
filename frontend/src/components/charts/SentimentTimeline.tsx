import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  AreaChart,
} from 'recharts';

interface TimelineDataPoint {
  position: number;
  sentiment: number;
  text?: string;
}

interface SentimentTimelineProps {
  data: TimelineDataPoint[];
  title?: string;
  showArea?: boolean;
  height?: number;
}

export default function SentimentTimeline({
  data,
  title = 'Sentiment Over Time',
  showArea = true,
  height = 300,
}: SentimentTimelineProps) {
  if (!data || data.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No timeline data available
      </div>
    );
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const sentiment = data.sentiment;
      const sentimentLabel =
        sentiment > 0.1 ? 'Positive' : sentiment < -0.1 ? 'Negative' : 'Neutral';
      const sentimentColor =
        sentiment > 0.1
          ? 'text-green-600'
          : sentiment < -0.1
          ? 'text-red-600'
          : 'text-gray-600';

      return (
        <div className="bg-white p-3 shadow-lg rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500">Position {data.position}</p>
          <p className={`text-sm font-semibold ${sentimentColor}`}>
            {sentimentLabel}: {sentiment.toFixed(3)}
          </p>
          {data.text && (
            <p className="text-xs text-gray-600 mt-1 max-w-xs truncate">
              "{data.text}"
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  const gradientOffset = () => {
    const dataMax = Math.max(...data.map((d) => d.sentiment));
    const dataMin = Math.min(...data.map((d) => d.sentiment));

    if (dataMax <= 0) return 0;
    if (dataMin >= 0) return 1;

    return dataMax / (dataMax - dataMin);
  };

  const off = gradientOffset();

  return (
    <div>
      {title && (
        <h3 className="text-sm font-medium text-gray-700 mb-3">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        {showArea ? (
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="splitColor" x1="0" y1="0" x2="0" y2="1">
                <stop offset={off} stopColor="#22c55e" stopOpacity={0.8} />
                <stop offset={off} stopColor="#ef4444" stopOpacity={0.8} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="position"
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis
              domain={[-1, 1]}
              ticks={[-1, -0.5, 0, 0.5, 1]}
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" />
            <Area
              type="monotone"
              dataKey="sentiment"
              stroke="#6366f1"
              fill="url(#splitColor)"
              strokeWidth={2}
            />
          </AreaChart>
        ) : (
          <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="position"
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis
              domain={[-1, 1]}
              ticks={[-1, -0.5, 0, 0.5, 1]}
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" />
            <Line
              type="monotone"
              dataKey="sentiment"
              stroke="#6366f1"
              strokeWidth={2}
              dot={{ fill: '#6366f1', strokeWidth: 0, r: 3 }}
              activeDot={{ r: 5, fill: '#4f46e5' }}
            />
          </LineChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
