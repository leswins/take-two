import { useMemo } from 'react';

interface HeatMapCell {
  label: string;
  value: number;
  count?: number;
}

interface HeatMapRow {
  rowLabel: string;
  cells: HeatMapCell[];
}

interface SentimentHeatMapProps {
  data: HeatMapRow[];
  title?: string;
  columnLabels?: string[];
}

export default function SentimentHeatMap({
  data,
  title,
  columnLabels,
}: SentimentHeatMapProps) {
  const { minValue, maxValue } = useMemo(() => {
    const allValues = data.flatMap((row) => row.cells.map((cell) => cell.value));
    return {
      minValue: Math.min(...allValues, -1),
      maxValue: Math.max(...allValues, 1),
    };
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No heat map data available
      </div>
    );
  }

  const getBackgroundColor = (value: number) => {
    // Normalize value to 0-1 range where 0.5 is neutral
    const normalized = (value + 1) / 2; // -1 to 1 becomes 0 to 1

    if (normalized > 0.55) {
      // Positive - green
      const intensity = (normalized - 0.5) * 2; // 0 to 1
      return `rgba(34, 197, 94, ${0.2 + intensity * 0.6})`;
    } else if (normalized < 0.45) {
      // Negative - red
      const intensity = (0.5 - normalized) * 2; // 0 to 1
      return `rgba(239, 68, 68, ${0.2 + intensity * 0.6})`;
    } else {
      // Neutral - gray
      return 'rgba(156, 163, 175, 0.2)';
    }
  };

  const getTextColor = (value: number) => {
    const absValue = Math.abs(value);
    if (absValue > 0.5) {
      return 'text-white';
    }
    return value > 0.1 ? 'text-green-900' : value < -0.1 ? 'text-red-900' : 'text-gray-700';
  };

  return (
    <div>
      {title && (
        <h3 className="text-sm font-medium text-gray-700 mb-3">{title}</h3>
      )}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          {columnLabels && columnLabels.length > 0 && (
            <thead>
              <tr>
                <th className="p-2 text-left text-xs font-medium text-gray-500"></th>
                {columnLabels.map((label, i) => (
                  <th
                    key={i}
                    className="p-2 text-center text-xs font-medium text-gray-500"
                  >
                    {label}
                  </th>
                ))}
              </tr>
            </thead>
          )}
          <tbody>
            {data.map((row, rowIndex) => (
              <tr key={rowIndex}>
                <td className="p-2 text-sm font-medium text-gray-700 whitespace-nowrap">
                  {row.rowLabel}
                </td>
                {row.cells.map((cell, cellIndex) => (
                  <td
                    key={cellIndex}
                    className={`p-2 text-center text-sm font-medium transition-all duration-200 ${getTextColor(
                      cell.value
                    )}`}
                    style={{
                      backgroundColor: getBackgroundColor(cell.value),
                      minWidth: '60px',
                    }}
                    title={`${cell.label}: ${cell.value.toFixed(3)}${
                      cell.count ? ` (${cell.count} mentions)` : ''
                    }`}
                  >
                    {cell.value.toFixed(2)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center mt-4 gap-2">
        <span className="text-xs text-gray-500">Negative</span>
        <div className="flex h-3 w-48 rounded overflow-hidden">
          <div className="flex-1 bg-red-500" />
          <div className="flex-1 bg-red-300" />
          <div className="flex-1 bg-gray-300" />
          <div className="flex-1 bg-green-300" />
          <div className="flex-1 bg-green-500" />
        </div>
        <span className="text-xs text-gray-500">Positive</span>
      </div>
    </div>
  );
}
