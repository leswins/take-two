interface Adjective {
  word: string;
  count: number;
  sentiment?: string;
}

interface WordFrequencyChartProps {
  adjectives: Adjective[];
  maxItems?: number;
  title?: string;
}

export default function WordFrequencyChart({
  adjectives,
  maxItems = 10,
  title = 'Most Used Adjectives',
}: WordFrequencyChartProps) {
  const displayItems = adjectives.slice(0, maxItems);
  const maxCount = Math.max(...displayItems.map((a) => a.count), 1);

  const getSentimentColor = (sentiment?: string) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-500';
      case 'negative':
        return 'bg-red-500';
      default:
        return 'bg-blue-500';
    }
  };

  const getSentimentBgColor = (sentiment?: string) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-100';
      case 'negative':
        return 'bg-red-100';
      default:
        return 'bg-blue-100';
    }
  };

  if (displayItems.length === 0) {
    return (
      <div className="text-center text-gray-500 py-4">
        No adjectives found
      </div>
    );
  }

  return (
    <div>
      {title && (
        <h3 className="text-sm font-medium text-gray-700 mb-3">{title}</h3>
      )}
      <div className="space-y-2">
        {displayItems.map((adj, index) => (
          <div key={adj.word} className="flex items-center">
            <span className="w-24 text-sm text-gray-600 truncate" title={adj.word}>
              {adj.word}
            </span>
            <div className="flex-1 mx-2">
              <div className={`h-6 rounded ${getSentimentBgColor(adj.sentiment)}`}>
                <div
                  className={`h-full rounded ${getSentimentColor(adj.sentiment)} transition-all duration-300`}
                  style={{ width: `${(adj.count / maxCount) * 100}%` }}
                />
              </div>
            </div>
            <span className="w-8 text-sm text-gray-500 text-right">
              {adj.count}
            </span>
          </div>
        ))}
      </div>
      {adjectives.length > maxItems && (
        <p className="text-xs text-gray-400 mt-2 text-center">
          Showing {maxItems} of {adjectives.length} adjectives
        </p>
      )}
    </div>
  );
}
