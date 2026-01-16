interface SentimentDistributionProps {
  positive: number;
  negative: number;
  neutral: number;
  showLegend?: boolean;
}

export default function SentimentDistribution({
  positive,
  negative,
  neutral,
  showLegend = true,
}: SentimentDistributionProps) {
  const total = positive + negative + neutral;

  if (total === 0) {
    return (
      <div className="text-center text-gray-500 py-4">
        No sentiment data available
      </div>
    );
  }

  const positivePercent = (positive / total) * 100;
  const negativePercent = (negative / total) * 100;
  const neutralPercent = (neutral / total) * 100;

  return (
    <div>
      {/* Stacked bar */}
      <div className="h-8 flex rounded-lg overflow-hidden">
        {positivePercent > 0 && (
          <div
            className="bg-green-500 flex items-center justify-center text-white text-xs font-medium transition-all duration-300"
            style={{ width: `${positivePercent}%` }}
            title={`Positive: ${positive}`}
          >
            {positivePercent >= 10 && `${positivePercent.toFixed(0)}%`}
          </div>
        )}
        {neutralPercent > 0 && (
          <div
            className="bg-gray-400 flex items-center justify-center text-white text-xs font-medium transition-all duration-300"
            style={{ width: `${neutralPercent}%` }}
            title={`Neutral: ${neutral}`}
          >
            {neutralPercent >= 10 && `${neutralPercent.toFixed(0)}%`}
          </div>
        )}
        {negativePercent > 0 && (
          <div
            className="bg-red-500 flex items-center justify-center text-white text-xs font-medium transition-all duration-300"
            style={{ width: `${negativePercent}%` }}
            title={`Negative: ${negative}`}
          >
            {negativePercent >= 10 && `${negativePercent.toFixed(0)}%`}
          </div>
        )}
      </div>

      {/* Legend */}
      {showLegend && (
        <div className="flex justify-center space-x-6 mt-3">
          <div className="flex items-center">
            <span className="w-3 h-3 bg-green-500 rounded-full mr-2" />
            <span className="text-sm text-gray-600">
              Positive ({positive})
            </span>
          </div>
          <div className="flex items-center">
            <span className="w-3 h-3 bg-gray-400 rounded-full mr-2" />
            <span className="text-sm text-gray-600">
              Neutral ({neutral})
            </span>
          </div>
          <div className="flex items-center">
            <span className="w-3 h-3 bg-red-500 rounded-full mr-2" />
            <span className="text-sm text-gray-600">
              Negative ({negative})
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
