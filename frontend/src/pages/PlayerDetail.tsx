import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { playerApi, analysisApi } from '../api/client';
import type { Player, PlayerAnalysisSummary } from '../types';

export default function PlayerDetail() {
  const { id } = useParams<{ id: string }>();
  const [player, setPlayer] = useState<Player | null>(null);
  const [summary, setSummary] = useState<PlayerAnalysisSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;

    async function fetchData() {
      try {
        const [playerData, summaryData] = await Promise.all([
          playerApi.get(id!),
          analysisApi.getPlayerSummary(id!).catch(() => null),
        ]);
        setPlayer(playerData);
        setSummary(summaryData);
      } catch (error) {
        console.error('Failed to fetch player:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (!player) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Player not found</p>
        <Link to="/players" className="text-primary-600 hover:underline mt-2 inline-block">
          Back to players
        </Link>
      </div>
    );
  }

  const SentimentIcon = summary?.sentiment_label === 'positive'
    ? TrendingUp
    : summary?.sentiment_label === 'negative'
    ? TrendingDown
    : Minus;

  const sentimentColor = summary?.sentiment_label === 'positive'
    ? 'text-green-500'
    : summary?.sentiment_label === 'negative'
    ? 'text-red-500'
    : 'text-gray-500';

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link to="/players" className="p-2 rounded-md hover:bg-gray-100">
          <ArrowLeft className="h-5 w-5 text-gray-500" />
        </Link>
        <div className="flex items-center">
          <div className="h-16 w-16 bg-primary-100 rounded-full flex items-center justify-center">
            <span className="text-primary-700 font-bold text-2xl">
              {player.name.charAt(0)}
            </span>
          </div>
          <div className="ml-4">
            <h1 className="text-2xl font-bold text-gray-900">{player.name}</h1>
            <p className="text-gray-500">
              {player.team || 'No team'} - {player.position || 'No position'}
            </p>
          </div>
        </div>
      </div>

      {/* Player Info */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Player Info</h2>
        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <dt className="text-sm font-medium text-gray-500">Sport</dt>
            <dd className="text-sm text-gray-900">{player.sport || '-'}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Team</dt>
            <dd className="text-sm text-gray-900">{player.team || '-'}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Position</dt>
            <dd className="text-sm text-gray-900">{player.position || '-'}</dd>
          </div>
          {player.aliases && player.aliases.length > 0 && (
            <div className="sm:col-span-3">
              <dt className="text-sm font-medium text-gray-500">Aliases</dt>
              <dd className="text-sm text-gray-900">{player.aliases.join(', ')}</dd>
            </div>
          )}
        </dl>
      </div>

      {/* Analysis Summary */}
      {summary && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Analysis Summary
          </h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-900">
                {summary.total_mentions}
              </div>
              <div className="text-sm text-gray-500">Total Mentions</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-900">
                {summary.transcript_count}
              </div>
              <div className="text-sm text-gray-500">Transcripts</div>
            </div>
            <div className="text-center">
              <div className={`flex items-center justify-center ${sentimentColor}`}>
                <SentimentIcon className="h-8 w-8" />
                <span className="ml-2 text-2xl font-bold">
                  {summary.average_sentiment?.toFixed(2) || 'N/A'}
                </span>
              </div>
              <div className="text-sm text-gray-500">Avg. Sentiment</div>
            </div>
            <div className="text-center">
              <span
                className={`px-3 py-1 text-sm font-medium rounded-full ${
                  summary.sentiment_label === 'positive'
                    ? 'bg-green-100 text-green-800'
                    : summary.sentiment_label === 'negative'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {summary.sentiment_label || 'Unknown'}
              </span>
              <div className="text-sm text-gray-500 mt-2">Overall Sentiment</div>
            </div>
          </div>
        </div>
      )}

      {/* Top Adjectives */}
      {summary && summary.top_adjectives.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Most Used Adjectives
          </h2>
          <div className="flex flex-wrap gap-2">
            {summary.top_adjectives.map((adj, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
              >
                {adj.word} ({adj.count})
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
