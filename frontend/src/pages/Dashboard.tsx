import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Users, TrendingUp, Upload } from 'lucide-react';
import { transcriptApi, playerApi } from '../api/client';
import type { TranscriptListItem, PlayerListItem } from '../types';

export default function Dashboard() {
  const [transcripts, setTranscripts] = useState<TranscriptListItem[]>([]);
  const [players, setPlayers] = useState<PlayerListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [transcriptData, playerData] = await Promise.all([
          transcriptApi.list(),
          playerApi.list(),
        ]);
        setTranscripts(transcriptData);
        setPlayers(playerData);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const processedCount = transcripts.filter((t) => t.processed).length;

  const stats = [
    {
      name: 'Total Transcripts',
      value: transcripts.length,
      icon: FileText,
      color: 'bg-blue-500',
    },
    {
      name: 'Analyzed',
      value: processedCount,
      icon: TrendingUp,
      color: 'bg-green-500',
    },
    {
      name: 'Players Tracked',
      value: players.length,
      icon: Users,
      color: 'bg-purple-500',
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-gray-600">
          Analyze sports commentary to identify player sentiment and bias patterns.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        {stats.map((stat) => (
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
            to="/transcripts"
            className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
          >
            <FileText className="h-8 w-8 text-primary-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-900">
                View Transcripts
              </p>
              <p className="text-sm text-gray-500">
                Browse and manage uploaded transcripts
              </p>
            </div>
          </Link>
        </div>
      </div>

      {/* Recent Transcripts */}
      {transcripts.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">
              Recent Transcripts
            </h2>
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
    </div>
  );
}
