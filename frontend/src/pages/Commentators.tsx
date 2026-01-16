import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Mic, TrendingUp, TrendingDown, Minus, Users } from 'lucide-react';
import { analysisApi } from '../api/client';
import { SentimentDistribution, SentimentBar } from '../components/charts';

interface CommentatorStats {
  commentator: string;
  transcript_count: number;
  players_analyzed: number;
  sentiment_distribution: {
    positive: number;
    negative: number;
    neutral: number;
  };
  top_players: Array<{
    id: string;
    name: string;
    mentions: number;
    sentiment: number;
    sentiment_label: string;
  }>;
}

export default function Commentators() {
  const [commentators, setCommentators] = useState<string[]>([]);
  const [selectedCommentator, setSelectedCommentator] = useState<string | null>(null);
  const [stats, setStats] = useState<CommentatorStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [statsLoading, setStatsLoading] = useState(false);

  useEffect(() => {
    analysisApi.getCommentators()
      .then((data) => {
        setCommentators(data);
        if (data.length > 0 && !selectedCommentator) {
          setSelectedCommentator(data[0]);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedCommentator) {
      setStats(null);
      return;
    }

    setStatsLoading(true);
    analysisApi.getCommentatorStats(selectedCommentator)
      .then(setStats)
      .catch(console.error)
      .finally(() => setStatsLoading(false));
  }, [selectedCommentator]);

  const getSentimentIcon = (label: string) => {
    if (label === 'positive') return <TrendingUp className="h-4 w-4 text-green-500" />;
    if (label === 'negative') return <TrendingDown className="h-4 w-4 text-red-500" />;
    return <Minus className="h-4 w-4 text-gray-500" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading commentators...</div>
      </div>
    );
  }

  if (commentators.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Commentator Analysis</h1>
          <p className="text-gray-500">View sentiment patterns by commentator</p>
        </div>
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <Mic className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Commentators Found</h3>
          <p className="text-gray-500 mb-4">
            Upload transcripts with commentator names to see analysis by commentator.
          </p>
          <Link
            to="/upload"
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Upload Transcript
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Commentator Analysis</h1>
          <p className="text-gray-500">View sentiment patterns by commentator</p>
        </div>
        <Mic className="h-8 w-8 text-primary-500" />
      </div>

      {/* Commentator Selection */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Select Commentator</h2>
        <div className="flex flex-wrap gap-2">
          {commentators.map((commentator) => (
            <button
              key={commentator}
              onClick={() => setSelectedCommentator(commentator)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedCommentator === commentator
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {commentator}
            </button>
          ))}
        </div>
      </div>

      {statsLoading && (
        <div className="flex items-center justify-center h-32">
          <div className="text-gray-500">Loading statistics...</div>
        </div>
      )}

      {!statsLoading && stats && (
        <>
          {/* Overview Stats */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
            <div className="bg-white overflow-hidden shadow rounded-lg p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-blue-500 rounded-md p-3">
                  <Mic className="h-6 w-6 text-white" />
                </div>
                <div className="ml-5">
                  <p className="text-sm font-medium text-gray-500">Transcripts</p>
                  <p className="text-2xl font-semibold text-gray-900">{stats.transcript_count}</p>
                </div>
              </div>
            </div>
            <div className="bg-white overflow-hidden shadow rounded-lg p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-purple-500 rounded-md p-3">
                  <Users className="h-6 w-6 text-white" />
                </div>
                <div className="ml-5">
                  <p className="text-sm font-medium text-gray-500">Players Analyzed</p>
                  <p className="text-2xl font-semibold text-gray-900">{stats.players_analyzed}</p>
                </div>
              </div>
            </div>
            <div className="bg-white overflow-hidden shadow rounded-lg p-5">
              <p className="text-sm font-medium text-gray-500 mb-2">Sentiment Distribution</p>
              <SentimentDistribution
                positive={stats.sentiment_distribution.positive}
                negative={stats.sentiment_distribution.negative}
                neutral={stats.sentiment_distribution.neutral}
                showLegend={false}
              />
            </div>
          </div>

          {/* Top Players */}
          {stats.top_players.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Players Mentioned by {stats.commentator}
              </h2>
              <div className="space-y-4">
                {stats.top_players.map((player) => (
                  <div
                    key={player.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center">
                      <Link
                        to={`/players/${player.id}`}
                        className="font-medium text-primary-600 hover:underline"
                      >
                        {player.name}
                      </Link>
                      <span className="ml-3 text-sm text-gray-500">
                        {player.mentions} mentions
                      </span>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="w-32">
                        <SentimentBar score={player.sentiment} height={8} showLabel={false} />
                      </div>
                      <div className="flex items-center">
                        {getSentimentIcon(player.sentiment_label)}
                        <span className={`ml-1 text-sm font-medium ${
                          player.sentiment_label === 'positive' ? 'text-green-600' :
                          player.sentiment_label === 'negative' ? 'text-red-600' : 'text-gray-600'
                        }`}>
                          {player.sentiment > 0 ? '+' : ''}{player.sentiment.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Bias Summary */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Commentator Bias Summary</h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm font-medium text-gray-500">Overall Tendency</p>
                {(() => {
                  const { positive, negative, neutral } = stats.sentiment_distribution;
                  const total = positive + negative + neutral;
                  if (total === 0) return <p className="text-lg text-gray-600">No data</p>;

                  const positiveRatio = positive / total;
                  const negativeRatio = negative / total;

                  if (positiveRatio > 0.5) {
                    return <p className="text-lg font-semibold text-green-600">Tends Positive</p>;
                  } else if (negativeRatio > 0.5) {
                    return <p className="text-lg font-semibold text-red-600">Tends Negative</p>;
                  }
                  return <p className="text-lg font-semibold text-gray-600">Balanced</p>;
                })()}
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm font-medium text-gray-500">Most Mentioned Player</p>
                {stats.top_players[0] ? (
                  <Link
                    to={`/players/${stats.top_players[0].id}`}
                    className="text-lg font-semibold text-primary-600 hover:underline"
                  >
                    {stats.top_players[0].name}
                  </Link>
                ) : (
                  <p className="text-lg text-gray-600">N/A</p>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
