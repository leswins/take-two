import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, BarChart3, Scale } from 'lucide-react';
import { playerApi, analysisApi } from '../api/client';
import { PlayerComparisonChart, SentimentHeatMap, SentimentDistribution } from '../components/charts';
import type { PlayerListItem } from '../types';

interface ComparisonData {
  id: string;
  name: string;
  sentiment: number;
  mentions: number;
  positivePercent: number;
  negativePercent: number;
  transcriptCount: number;
}

export default function Compare() {
  const [players, setPlayers] = useState<PlayerListItem[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [comparisonData, setComparisonData] = useState<ComparisonData[]>([]);
  const [biasComparison, setBiasComparison] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [chartType, setChartType] = useState<'bar' | 'radar'>('bar');
  const [metric, setMetric] = useState<'sentiment' | 'mentions'>('sentiment');

  useEffect(() => {
    playerApi.list().then(setPlayers).catch(console.error);
  }, []);

  useEffect(() => {
    if (selectedIds.length < 2) {
      setComparisonData([]);
      setBiasComparison(null);
      return;
    }

    setLoading(true);
    Promise.all([
      analysisApi.getPlayerComparisonData(selectedIds),
      analysisApi.compareBias(selectedIds).catch(() => null),
    ])
      .then(([comparison, bias]) => {
        setComparisonData(comparison);
        setBiasComparison(bias);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedIds]);

  const togglePlayer = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    );
  };

  const heatMapData = comparisonData.map((player) => ({
    rowLabel: player.name,
    cells: [
      { label: 'Sentiment', value: player.sentiment, count: player.mentions },
      { label: 'Positive %', value: (player.positivePercent / 100) * 2 - 1 },
      { label: 'Coverage', value: Math.min(player.mentions / 50, 1) * 2 - 1 },
    ],
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Compare Players</h1>
          <p className="text-gray-500">Select players to compare sentiment analysis</p>
        </div>
        <div className="flex items-center space-x-4">
          <Users className="h-8 w-8 text-primary-500" />
        </div>
      </div>

      {/* Player Selection */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          Select Players ({selectedIds.length} selected)
        </h2>
        <div className="flex flex-wrap gap-2">
          {players.map((player) => (
            <button
              key={player.id}
              onClick={() => togglePlayer(player.id)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedIds.includes(player.id)
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {player.name}
            </button>
          ))}
        </div>
        {players.length === 0 && (
          <p className="text-gray-500 text-sm">
            No players found. <Link to="/transcripts" className="text-primary-600 hover:underline">Analyze some transcripts</Link> first.
          </p>
        )}
      </div>

      {selectedIds.length < 2 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <Scale className="h-12 w-12 text-blue-400 mx-auto mb-3" />
          <p className="text-blue-700">Select at least 2 players to compare</p>
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center h-32">
          <div className="text-gray-500">Loading comparison data...</div>
        </div>
      )}

      {!loading && comparisonData.length >= 2 && (
        <>
          {/* Chart Type Controls */}
          <div className="bg-white shadow rounded-lg p-4">
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-gray-700">Chart Type:</span>
                <select
                  value={chartType}
                  onChange={(e) => setChartType(e.target.value as 'bar' | 'radar')}
                  className="rounded-md border-gray-300 shadow-sm text-sm"
                >
                  <option value="bar">Bar Chart</option>
                  <option value="radar">Radar Chart</option>
                </select>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-gray-700">Metric:</span>
                <select
                  value={metric}
                  onChange={(e) => setMetric(e.target.value as 'sentiment' | 'mentions')}
                  className="rounded-md border-gray-300 shadow-sm text-sm"
                >
                  <option value="sentiment">Sentiment</option>
                  <option value="mentions">Mentions</option>
                </select>
              </div>
            </div>
          </div>

          {/* Comparison Chart */}
          <div className="bg-white shadow rounded-lg p-6">
            <PlayerComparisonChart
              players={comparisonData}
              title={`Player Comparison - ${metric === 'sentiment' ? 'Sentiment Score' : 'Total Mentions'}`}
              chartType={chartType}
              metric={metric}
              height={Math.max(200, comparisonData.length * 50)}
            />
          </div>

          {/* Heat Map */}
          <div className="bg-white shadow rounded-lg p-6">
            <SentimentHeatMap
              data={heatMapData}
              title="Sentiment Heat Map"
              columnLabels={['Sentiment', 'Positive %', 'Coverage']}
            />
          </div>

          {/* Bias Comparison */}
          {biasComparison && !biasComparison.error && (
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center mb-4">
                <Scale className="h-5 w-5 text-amber-500 mr-2" />
                <h2 className="text-lg font-medium text-gray-900">Fairness Analysis</h2>
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-4 mb-6">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm font-medium text-gray-500">Fairness Score</p>
                  <p className={`text-2xl font-bold ${
                    biasComparison.fairness_score > 0.7 ? 'text-green-600' :
                    biasComparison.fairness_score > 0.4 ? 'text-amber-600' : 'text-red-600'
                  }`}>
                    {(biasComparison.fairness_score * 100).toFixed(0)}%
                  </p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm font-medium text-gray-500">Disparity Score</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {biasComparison.disparity_score.toFixed(2)}
                  </p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-sm font-medium text-gray-500">Most Favored</p>
                  <p className="text-lg font-semibold text-green-700">
                    {biasComparison.most_favored || 'N/A'}
                  </p>
                </div>
                <div className="p-4 bg-red-50 rounded-lg">
                  <p className="text-sm font-medium text-gray-500">Least Favored</p>
                  <p className="text-lg font-semibold text-red-700">
                    {biasComparison.least_favored || 'N/A'}
                  </p>
                </div>
              </div>

              {/* Player Rankings */}
              <h3 className="text-sm font-medium text-gray-700 mb-3">Player Rankings</h3>
              <div className="space-y-2">
                {biasComparison.player_rankings?.map((player: any, index: number) => (
                  <div
                    key={player.player_name}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center">
                      <span className="w-8 h-8 flex items-center justify-center rounded-full bg-primary-100 text-primary-700 font-bold text-sm mr-3">
                        {player.rank}
                      </span>
                      <span className="font-medium text-gray-900">{player.player_name}</span>
                    </div>
                    <div className="flex items-center space-x-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        player.bias_level === 'minimal' ? 'bg-green-100 text-green-700' :
                        player.bias_level === 'low' ? 'bg-blue-100 text-blue-700' :
                        player.bias_level === 'moderate' ? 'bg-amber-100 text-amber-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {player.bias_level}
                      </span>
                      <span className="text-sm text-gray-500">
                        Score: {player.bias_score.toFixed(3)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Summary Stats */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Summary Statistics</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Player</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sentiment</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mentions</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Positive %</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Transcripts</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {comparisonData.map((player) => (
                    <tr key={player.id}>
                      <td className="px-4 py-3">
                        <Link to={`/players/${player.id}`} className="font-medium text-primary-600 hover:underline">
                          {player.name}
                        </Link>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`font-medium ${
                          player.sentiment > 0.1 ? 'text-green-600' :
                          player.sentiment < -0.1 ? 'text-red-600' : 'text-gray-600'
                        }`}>
                          {player.sentiment > 0 ? '+' : ''}{player.sentiment.toFixed(3)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-900">{player.mentions}</td>
                      <td className="px-4 py-3 text-gray-900">{player.positivePercent.toFixed(1)}%</td>
                      <td className="px-4 py-3 text-gray-900">{player.transcriptCount}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
