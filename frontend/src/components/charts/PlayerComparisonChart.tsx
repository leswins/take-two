import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  Legend,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';

interface PlayerData {
  name: string;
  sentiment: number;
  mentions: number;
  biasScore?: number;
  positivePercent?: number;
  negativePercent?: number;
}

interface PlayerComparisonChartProps {
  players: PlayerData[];
  title?: string;
  chartType?: 'bar' | 'radar';
  metric?: 'sentiment' | 'mentions' | 'bias';
  height?: number;
}

export default function PlayerComparisonChart({
  players,
  title = 'Player Comparison',
  chartType = 'bar',
  metric = 'sentiment',
  height = 300,
}: PlayerComparisonChartProps) {
  if (!players || players.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No comparison data available
      </div>
    );
  }

  const getBarColor = (value: number, metric: string) => {
    if (metric === 'mentions') {
      return '#6366f1'; // Indigo for mentions
    }
    if (metric === 'bias') {
      // Higher bias = more amber/red
      if (value > 0.6) return '#ef4444';
      if (value > 0.4) return '#f97316';
      if (value > 0.2) return '#eab308';
      return '#22c55e';
    }
    // Sentiment
    if (value > 0.1) return '#22c55e';
    if (value < -0.1) return '#ef4444';
    return '#9ca3af';
  };

  const getDataKey = () => {
    switch (metric) {
      case 'mentions':
        return 'mentions';
      case 'bias':
        return 'biasScore';
      default:
        return 'sentiment';
    }
  };

  const getYAxisDomain = () => {
    switch (metric) {
      case 'mentions':
        return [0, 'auto'];
      case 'bias':
        return [0, 1];
      default:
        return [-1, 1];
    }
  };

  const formatValue = (value: number) => {
    if (metric === 'mentions') return value;
    return value.toFixed(2);
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 shadow-lg rounded-lg border border-gray-200">
          <p className="font-medium text-gray-900">{data.name}</p>
          <div className="mt-1 space-y-1 text-sm">
            <p className="text-gray-600">
              Sentiment:{' '}
              <span
                className={
                  data.sentiment > 0.1
                    ? 'text-green-600'
                    : data.sentiment < -0.1
                    ? 'text-red-600'
                    : 'text-gray-600'
                }
              >
                {data.sentiment?.toFixed(3) || 'N/A'}
              </span>
            </p>
            <p className="text-gray-600">Mentions: {data.mentions}</p>
            {data.biasScore !== undefined && (
              <p className="text-gray-600">
                Bias Score: {data.biasScore.toFixed(3)}
              </p>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  if (chartType === 'radar' && players.length >= 3) {
    // Prepare radar data - normalize all metrics to 0-1 scale
    const radarData = [
      {
        metric: 'Sentiment',
        ...Object.fromEntries(
          players.map((p) => [p.name, (p.sentiment + 1) / 2]) // -1 to 1 -> 0 to 1
        ),
      },
      {
        metric: 'Mentions',
        ...Object.fromEntries(
          players.map((p) => {
            const maxMentions = Math.max(...players.map((pl) => pl.mentions));
            return [p.name, p.mentions / maxMentions];
          })
        ),
      },
      {
        metric: 'Positive %',
        ...Object.fromEntries(
          players.map((p) => [p.name, (p.positivePercent || 50) / 100])
        ),
      },
    ];

    if (players.some((p) => p.biasScore !== undefined)) {
      radarData.push({
        metric: 'Fairness',
        ...Object.fromEntries(
          players.map((p) => [p.name, 1 - (p.biasScore || 0)]) // Invert so higher = better
        ),
      });
    }

    const colors = ['#6366f1', '#22c55e', '#f97316', '#ec4899', '#14b8a6'];

    return (
      <div>
        {title && (
          <h3 className="text-sm font-medium text-gray-700 mb-3">{title}</h3>
        )}
        <ResponsiveContainer width="100%" height={height}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#e5e7eb" />
            <PolarAngleAxis
              dataKey="metric"
              tick={{ fontSize: 11, fill: '#6b7280' }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 1]}
              tick={{ fontSize: 10 }}
            />
            {players.map((player, index) => (
              <Radar
                key={player.name}
                name={player.name}
                dataKey={player.name}
                stroke={colors[index % colors.length]}
                fill={colors[index % colors.length]}
                fillOpacity={0.2}
                strokeWidth={2}
              />
            ))}
            <Legend />
            <Tooltip />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    );
  }

  return (
    <div>
      {title && (
        <h3 className="text-sm font-medium text-gray-700 mb-3">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={players}
          layout="vertical"
          margin={{ top: 10, right: 30, left: 60, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            type="number"
            domain={getYAxisDomain() as [number, number | string]}
            tick={{ fontSize: 11 }}
            tickFormatter={(v) => formatValue(v).toString()}
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fontSize: 11 }}
            width={80}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey={getDataKey()} radius={[0, 4, 4, 0]}>
            {players.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={getBarColor(
                  metric === 'mentions'
                    ? 0
                    : metric === 'bias'
                    ? entry.biasScore || 0
                    : entry.sentiment,
                  metric
                )}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
