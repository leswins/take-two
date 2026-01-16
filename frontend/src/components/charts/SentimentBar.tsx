import { useMemo } from 'react';

interface SentimentBarProps {
  score: number; // -1 to 1
  showLabel?: boolean;
  height?: number;
}

export default function SentimentBar({ score, showLabel = true, height = 8 }: SentimentBarProps) {
  const { percentage, color, label } = useMemo(() => {
    // Convert -1 to 1 scale to 0-100 percentage
    const pct = ((score + 1) / 2) * 100;

    let clr: string;
    let lbl: string;

    if (score > 0.1) {
      clr = 'bg-green-500';
      lbl = 'Positive';
    } else if (score < -0.1) {
      clr = 'bg-red-500';
      lbl = 'Negative';
    } else {
      clr = 'bg-gray-400';
      lbl = 'Neutral';
    }

    return { percentage: pct, color: clr, label: lbl };
  }, [score]);

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-1">
        {showLabel && (
          <>
            <span className="text-xs text-gray-500">Negative</span>
            <span className="text-xs font-medium text-gray-700">{label}</span>
            <span className="text-xs text-gray-500">Positive</span>
          </>
        )}
      </div>
      <div
        className="w-full bg-gray-200 rounded-full overflow-hidden"
        style={{ height: `${height}px` }}
      >
        <div className="h-full flex">
          {/* Negative side (left half) */}
          <div className="w-1/2 flex justify-end bg-red-100">
            {score < 0 && (
              <div
                className="bg-red-500 h-full"
                style={{ width: `${Math.abs(score) * 100}%` }}
              />
            )}
          </div>
          {/* Positive side (right half) */}
          <div className="w-1/2 bg-green-100">
            {score > 0 && (
              <div
                className="bg-green-500 h-full"
                style={{ width: `${score * 100}%` }}
              />
            )}
          </div>
        </div>
      </div>
      <div className="flex justify-center mt-1">
        <span className="text-xs font-medium text-gray-600">
          {score > 0 ? '+' : ''}{score.toFixed(2)}
        </span>
      </div>
    </div>
  );
}
