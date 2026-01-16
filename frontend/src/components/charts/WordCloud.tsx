import { useMemo } from 'react';

interface WordData {
  word: string;
  count: number;
  sentiment?: 'positive' | 'negative' | 'neutral';
}

interface WordCloudProps {
  words: WordData[];
  maxWords?: number;
  title?: string;
}

export default function WordCloud({
  words,
  maxWords = 30,
  title,
}: WordCloudProps) {
  const processedWords = useMemo(() => {
    if (!words || words.length === 0) return [];

    // Sort by count and take top N
    const sorted = [...words]
      .sort((a, b) => b.count - a.count)
      .slice(0, maxWords);

    // Calculate min and max for scaling
    const counts = sorted.map((w) => w.count);
    const maxCount = Math.max(...counts);
    const minCount = Math.min(...counts);
    const range = maxCount - minCount || 1;

    // Scale font sizes between 0.75rem and 2.5rem
    return sorted.map((word) => {
      const normalized = (word.count - minCount) / range;
      const fontSize = 0.75 + normalized * 1.75; // 0.75rem to 2.5rem
      const opacity = 0.6 + normalized * 0.4; // 0.6 to 1.0

      return {
        ...word,
        fontSize,
        opacity,
      };
    });
  }, [words, maxWords]);

  // Shuffle words for visual variety
  const shuffledWords = useMemo(() => {
    const arr = [...processedWords];
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }, [processedWords]);

  if (!words || words.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No word data available
      </div>
    );
  }

  const getColorClass = (sentiment?: string) => {
    switch (sentiment) {
      case 'positive':
        return 'text-green-600 hover:text-green-700';
      case 'negative':
        return 'text-red-600 hover:text-red-700';
      default:
        return 'text-indigo-600 hover:text-indigo-700';
    }
  };

  return (
    <div>
      {title && (
        <h3 className="text-sm font-medium text-gray-700 mb-3">{title}</h3>
      )}
      <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-2 p-4 bg-gray-50 rounded-lg min-h-[200px]">
        {shuffledWords.map((word, index) => (
          <span
            key={`${word.word}-${index}`}
            className={`font-medium transition-all duration-200 cursor-default hover:scale-110 ${getColorClass(
              word.sentiment
            )}`}
            style={{
              fontSize: `${word.fontSize}rem`,
              opacity: word.opacity,
            }}
            title={`${word.word}: ${word.count} occurrences`}
          >
            {word.word}
          </span>
        ))}
      </div>
      <div className="flex justify-center gap-4 mt-3 text-xs text-gray-500">
        <span className="flex items-center">
          <span className="w-2 h-2 bg-green-500 rounded-full mr-1" />
          Positive
        </span>
        <span className="flex items-center">
          <span className="w-2 h-2 bg-indigo-500 rounded-full mr-1" />
          Neutral
        </span>
        <span className="flex items-center">
          <span className="w-2 h-2 bg-red-500 rounded-full mr-1" />
          Negative
        </span>
      </div>
    </div>
  );
}
