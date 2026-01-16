import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Users, TrendingUp, Upload, BarChart3 } from 'lucide-react';
import { transcriptApi, analysisApi } from '../api/client';
import { SentimentDistribution, WordFrequencyChart, SentimentBar } from '../components/charts';
import type { TranscriptListItem } from '../types';

interface DashboardStats {
  totals: {
    transcripts: number;
    analyzed: number;
    players: number;
    total_analyses: number;
  };
  sentiment_distribution: {
    positive: number;
    negative: number;
    neutral: number;
  };
  top_players: Array<{
    id: string;
    name: string;
    mentions: number;
    sentiment_score: number;
    sentiment_label: string;
  }>;
  top_adjectives: Array<{
    word: string;
    count: number;
    sentiment: string;
  }>;
}

export default function Dashboard() {
  const [transcripts, setTranscripts] = useState<TranscriptListItem[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [transcriptData, dashboardStats] = await Promise.all([
          transcriptApi.list(),
          analysisApi.getDashboardStats().catch(() => null),
        ]);
        setTranscripts(transcriptData);
        setStats(dashboardStats);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const statCards = [
    {
      name: 'Total Transcripts',
      value: stats?.totals.transcripts ?? transcripts.length,
      icon: FileText,
      color: 'bg-blue-500',
    },
    {
      name: 'Analyzed',
      value: stats?.totals.analyzed ?? transcripts.filter((t) => t.processed).length,
      icon: TrendingUp,
      color: 'bg-green-500',
    },
    {
      name: 'Players Tracked',
      value: stats?.totals.players ?? 0,
      icon: Users,
      color: 'bg-purple-500',
    },
    {
      name: 'Total Analyses',
      value: stats?.totals.total_analyses ?? 0,
      icon: BarChart3,
      color: 'bg-orange-500',
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  const hasAnalysisData = stats && stats.totals.total_analyses > 0;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-gray-600">
          Analyze sports commentary to identify player sentiment and bias patterns.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <div
            key={stat.name}
            className="bg-white overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className={`flex-shrink-0 ${stat.color} rounded-md p-3`}>
                  <stat.icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {stat.name}
                    </dt>
                    <dd className="text-2xl font-semibold text-gray-900">
                      {stat.value}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Analysis Overview - Only show if we have analysis data */}
      {hasAnalysisData && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Sentiment Distribution */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Overall Sentiment Distribution
            </h2>
            <SentimentDistribution
              positive={stats.sentiment_distribution.positive}
              negative={stats.sentiment_distribution.negative}
              neutral={stats.sentiment_distribution.neutral}
            />
          </div>

          {/* Top Adjectives */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Most Used Adjectives
            </h2>
            <WordFrequencyChart
              adjectives={stats.top_adjectives}
              maxItems={8}
              title=""
            />
          </div>
        </div>
      )}

      {/* Top Players - Only show if we have analysis data */}
      {hasAnalysisData && stats.top_players.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Most Mentioned Players
          </h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
            {stats.top_players.map((player) => (
              <Link
                key={player.id}
                to={`/players/${player.id}`}
                className="block p-4 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center mb-2">
                  <div className="h-10 w-10 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-primary-700 font-bold">
                      {player.name.charAt(0)}
                    </span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {player.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {player.mentions} mentions
                    </p>
                  </div>
                </div>
                <SentimentBar score={player.sentiment_score} height={6} showLabel={false} />
                <div className="mt-1 flex justify-center">
                  <span
                    className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                      player.sentiment_label === 'positive'
                        ? 'bg-green-100 text-green-800'
                        : player.sentiment_label === 'negative'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {player.sentiment_label}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Link
            to="/upload"
            className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
          >
            <Upload className="h-8 w-8 text-primary-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-900">
                Upload Transcript
              </p>
              <p className="text-sm text-gray-500">
                Add a new commentary transcript for analysis
              </p>
            </div>
          </Link>
          <Link
            to="/players"
            className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
          >
            <Users className="h-8 w-8 text-primary-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-900">
                View Players
              </p>
              <p className="text-sm text-gray-500">
                Browse analyzed players and their sentiment profiles
              </p>
            </div>
          </Link>
        </div>
      </div>

      {/* Recent Transcripts */}
      {transcripts.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-lg font-medium text-gray-900">
              Recent Transcripts
            </h2>
            <Link
              to="/transcripts"
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              View all
            </Link>
          </div>
          <ul className="divide-y divide-gray-200">
            {transcripts.slice(0, 5).map((transcript) => (
              <li key={transcript.id}>
                <Link
                  to={`/transcripts/${transcript.id}`}
                  className="block px-6 py-4 hover:bg-gray-50"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {transcript.original_filename}
                      </p>
                      <p className="text-sm text-gray-500">
                        {transcript.sport || 'No sport specified'} -{' '}
                        {transcript.word_count || '0'} words
                      </p>
                    </div>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        transcript.processed
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {transcript.processed ? 'Analyzed' : 'Pending'}
                    </span>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Empty State */}
      {transcripts.length === 0 && (
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No transcripts</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by uploading a commentary transcript.
          </p>
          <div className="mt-6">
            <Link
              to="/upload"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              <Upload className="-ml-1 mr-2 h-5 w-5" />
              Upload Transcript
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
