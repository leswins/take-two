import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, TrendingUp, TrendingDown, Minus, MessageSquare } from 'lucide-react';
import { playerApi, analysisApi } from '../api/client';
import { SentimentBar } from '../components/charts';
import type { PlayerListItem, PlayerAnalysisSummary } from '../types';

interface PlayerWithSummary extends PlayerListItem {
  summary?: PlayerAnalysisSummary;
}

export default function Players() {
  const [players, setPlayers] = useState<PlayerWithSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPlayers();
  }, []);

  async function fetchPlayers() {
    try {
      const data = await playerApi.list();

      // Fetch summaries for each player in parallel
      const playersWithSummaries = await Promise.all(
        data.map(async (player) => {
          try {
            const summary = await analysisApi.getPlayerSummary(player.id);
            return { ...player, summary };
          } catch {
            return player;
          }
        })
      );

      // Sort by total mentions (most mentioned first)
      playersWithSummaries.sort((a, b) => {
        const aMentions = a.summary?.total_mentions || 0;
        const bMentions = b.summary?.total_mentions || 0;
        return bMentions - aMentions;
      });

      setPlayers(playersWithSummaries);
    } catch (error) {
      console.error('Failed to fetch players:', error);
    } finally {
      setLoading(false);
    }
  }

  const getSentimentIcon = (label?: string | null) => {
    switch (label) {
      case 'positive':
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'negative':
        return <TrendingDown className="h-4 w-4 text-red-500" />;
      default:
        return <Minus className="h-4 w-4 text-gray-400" />;
    }
  };

  const getSentimentBadgeColor = (label?: string | null) => {
    switch (label) {
      case 'positive':
        return 'bg-green-100 text-green-800';
      case 'negative':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Players</h1>
        <p className="mt-1 text-gray-600">
          View players detected from commentary transcripts with sentiment analysis.
        </p>
      </div>

      {players.length === 0 ? (
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <Users className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No players</h3>
          <p className="mt-1 text-sm text-gray-500">
            Players will appear here after analyzing transcripts.
          </p>
          <div className="mt-6">
            <Link
              to="/upload"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              Upload Transcript
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {players.map((player) => (
            <Link
              key={player.id}
              to={`/players/${player.id}`}
              className="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="h-12 w-12 bg-primary-100 rounded-full flex items-center justify-center">
                      <span className="text-primary-700 font-semibold text-lg">
                        {player.name.charAt(0)}
                      </span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      {player.name}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {player.team || 'No team'} - {player.sport || 'No sport'}
                    </p>
                  </div>
                </div>
                {player.summary?.sentiment_label && (
                  <span
                    className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${getSentimentBadgeColor(
                      player.summary.sentiment_label
                    )}`}
                  >
                    {getSentimentIcon(player.summary.sentiment_label)}
                    <span className="ml-1 capitalize">
                      {player.summary.sentiment_label}
                    </span>
                  </span>
                )}
              </div>

              {/* Stats row */}
              {player.summary && player.summary.total_mentions > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
                    <div className="flex items-center">
                      <MessageSquare className="h-4 w-4 mr-1" />
                      <span>{player.summary.total_mentions} mentions</span>
                    </div>
                    <span>{player.summary.transcript_count} transcripts</span>
                  </div>

                  {/* Sentiment bar */}
                  {player.summary.average_sentiment !== null && (
                    <SentimentBar
                      score={player.summary.average_sentiment}
                      height={6}
                      showLabel={false}
                    />
                  )}

                  {/* Top adjectives preview */}
                  {player.summary.top_adjectives &&
                    player.summary.top_adjectives.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {player.summary.top_adjectives.slice(0, 3).map((adj, i) => (
                          <span
                            key={i}
                            className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded"
                          >
                            {adj.word}
                          </span>
                        ))}
                        {player.summary.top_adjectives.length > 3 && (
                          <span className="px-2 py-0.5 text-xs text-gray-400">
                            +{player.summary.top_adjectives.length - 3} more
                          </span>
                        )}
                      </div>
                    )}

                  {/* Top phrases preview */}
                  {player.summary.top_phrases &&
                    player.summary.top_phrases.length > 0 && (
                      <div className="mt-2">
                        <span className="text-xs text-purple-600 italic">
                          "{player.summary.top_phrases[0].phrase}"
                          {player.summary.top_phrases.length > 1 && (
                            <span className="text-gray-400 not-italic ml-1">
                              +{player.summary.top_phrases.length - 1} phrases
                            </span>
                          )}
                        </span>
                      </div>
                    )}
                </div>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
