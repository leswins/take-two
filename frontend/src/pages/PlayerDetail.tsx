import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, TrendingUp, TrendingDown, Minus, MessageSquare, FileText, Quote, AlertTriangle } from 'lucide-react';
import { playerApi, analysisApi } from '../api/client';
import { SentimentBar, WordFrequencyChart, SentimentTimeline, WordCloud } from '../components/charts';
import type { Player, PlayerAnalysisSummary, AnalysisResult } from '../types';

interface TimelineData {
  position: number;
  sentiment: number;
  text: string;
}

export default function PlayerDetail() {
  const { id } = useParams<{ id: string }>();
  const [player, setPlayer] = useState<Player | null>(null);
  const [summary, setSummary] = useState<PlayerAnalysisSummary | null>(null);
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);
  const [timelineData, setTimelineData] = useState<TimelineData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;

    async function fetchData() {
      try {
        const [playerData, summaryData, analysesData, timeline] = await Promise.all([
          playerApi.get(id!),
          analysisApi.getPlayerSummary(id!).catch(() => null),
          analysisApi.getForPlayer(id!).catch(() => []),
          analysisApi.getPlayerTimeline(id!).catch(() => []),
        ]);
        setPlayer(playerData);
        setSummary(summaryData);
        setAnalyses(analysesData);
        setTimelineData(timeline);
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
      {/* Header */}
      <div className="flex items-center justify-between">
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
        {summary?.sentiment_label && (
          <span
            className={`inline-flex items-center px-3 py-1 text-sm font-medium rounded-full ${
              summary.sentiment_label === 'positive'
                ? 'bg-green-100 text-green-800'
                : summary.sentiment_label === 'negative'
                ? 'bg-red-100 text-red-800'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            <SentimentIcon className="h-4 w-4 mr-1" />
            {summary.sentiment_label}
          </span>
        )}
      </div>

      {/* Stats Cards */}
      {summary && (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-4">
          <div className="bg-white overflow-hidden shadow rounded-lg p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-500 rounded-md p-3">
                <MessageSquare className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Total Mentions</p>
                <p className="text-2xl font-semibold text-gray-900">{summary.total_mentions}</p>
              </div>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-purple-500 rounded-md p-3">
                <FileText className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Transcripts</p>
                <p className="text-2xl font-semibold text-gray-900">{summary.transcript_count}</p>
              </div>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg p-5">
            <div className="flex items-center">
              <div className={`flex-shrink-0 rounded-md p-3 ${
                summary.sentiment_label === 'positive' ? 'bg-green-500' :
                summary.sentiment_label === 'negative' ? 'bg-red-500' : 'bg-gray-500'
              }`}>
                <SentimentIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Avg Sentiment</p>
                <p className={`text-2xl font-semibold ${sentimentColor}`}>
                  {summary.average_sentiment !== null
                    ? (summary.average_sentiment > 0 ? '+' : '') + summary.average_sentiment.toFixed(2)
                    : 'N/A'}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-orange-500 rounded-md p-3">
                <TrendingUp className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Unique Adjectives</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {summary.top_adjectives?.length || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sentiment Visualization */}
      {summary && summary.average_sentiment !== null && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Sentiment Analysis</h2>
          <div className="max-w-xl">
            <SentimentBar score={summary.average_sentiment} height={12} />
          </div>
          <p className="mt-4 text-sm text-gray-600">
            Based on {summary.total_mentions} mentions across {summary.transcript_count} transcripts,
            {player.name} is spoken about with a{' '}
            <span className={`font-medium ${sentimentColor}`}>
              {summary.sentiment_label}
            </span>{' '}
            tone overall.
          </p>
        </div>
      )}

      {/* Sentiment Timeline */}
      {timelineData.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <SentimentTimeline
            data={timelineData}
            title="Sentiment Over Time"
            showArea={true}
            height={250}
          />
          <p className="mt-3 text-xs text-gray-500">
            Shows how sentiment toward {player?.name} changes throughout commentary mentions.
            Positive values indicate favorable commentary, negative values indicate critical commentary.
          </p>
        </div>
      )}

      {/* Word Cloud */}
      {summary && summary.top_adjectives && summary.top_adjectives.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <WordCloud
            words={summary.top_adjectives.map(adj => ({
              word: adj.word,
              count: adj.count,
              sentiment: typeof adj.sentiment === 'number'
                ? (adj.sentiment > 0 ? 'positive' : adj.sentiment < 0 ? 'negative' : 'neutral')
                : 'neutral',
            }))}
            maxWords={25}
            title="Word Cloud - Descriptive Language"
          />
        </div>
      )}

      {/* Adjective Analysis */}
      {summary && summary.top_adjectives && summary.top_adjectives.length > 0 && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Word Frequency Chart */}
          <div className="bg-white shadow rounded-lg p-6">
            <WordFrequencyChart
              adjectives={summary.top_adjectives.map((adj) => ({
                word: adj.word,
                count: adj.count,
                sentiment: typeof adj.sentiment === 'number'
                  ? (adj.sentiment > 0 ? 'positive' : adj.sentiment < 0 ? 'negative' : 'neutral')
                  : 'neutral',
              }))}
              maxItems={10}
              title="Most Used Adjectives"
            />
          </div>

          {/* Adjective Tags */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-sm font-medium text-gray-700 mb-3">All Adjectives</h3>
            <div className="flex flex-wrap gap-2">
              {summary.top_adjectives.map((adj, index) => (
                <span
                  key={index}
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    typeof adj.sentiment === 'number'
                      ? adj.sentiment > 0
                        ? 'bg-green-100 text-green-800'
                        : adj.sentiment < 0
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  {adj.word}
                  <span className="ml-1 opacity-60">({adj.count})</span>
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Phrase Analysis */}
      {summary && summary.top_phrases && summary.top_phrases.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Quote className="h-5 w-5 text-purple-500 mr-2" />
            <h2 className="text-lg font-medium text-gray-900">Common Phrases</h2>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Frequently used phrases and expressions when describing {player.name}:
          </p>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {summary.top_phrases.map((phrase, index) => (
              <div
                key={index}
                className="p-3 bg-purple-50 rounded-lg border border-purple-100"
              >
                <p className="text-sm font-medium text-purple-900">
                  "{phrase.phrase}"
                </p>
                <div className="mt-1 flex items-center justify-between text-xs text-purple-600">
                  <span>Used {phrase.count} times</span>
                  {phrase.context && (
                    <span className="text-gray-500 truncate max-w-[200px]">
                      e.g., "{phrase.context}"
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bias Indicator */}
      {summary && summary.average_sentiment !== null && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center mb-4">
            <AlertTriangle className="h-5 w-5 text-amber-500 mr-2" />
            <h2 className="text-lg font-medium text-gray-900">Commentary Bias Analysis</h2>
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm font-medium text-gray-500">Sentiment Skew</p>
              <p className={`text-xl font-semibold ${
                Math.abs(summary.average_sentiment) > 0.3 ? 'text-amber-600' :
                Math.abs(summary.average_sentiment) > 0.1 ? 'text-blue-600' : 'text-green-600'
              }`}>
                {Math.abs(summary.average_sentiment) > 0.3 ? 'Strong' :
                 Math.abs(summary.average_sentiment) > 0.1 ? 'Moderate' : 'Minimal'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {summary.average_sentiment > 0.3 ? 'Strong positive bias detected' :
                 summary.average_sentiment < -0.3 ? 'Strong negative bias detected' :
                 summary.average_sentiment > 0.1 ? 'Slight positive leaning' :
                 summary.average_sentiment < -0.1 ? 'Slight negative leaning' :
                 'Balanced coverage'}
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm font-medium text-gray-500">Coverage Volume</p>
              <p className={`text-xl font-semibold ${
                summary.total_mentions > 50 ? 'text-purple-600' :
                summary.total_mentions > 20 ? 'text-blue-600' : 'text-gray-600'
              }`}>
                {summary.total_mentions > 50 ? 'High' :
                 summary.total_mentions > 20 ? 'Moderate' : 'Low'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {summary.total_mentions} mentions across {summary.transcript_count} transcripts
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm font-medium text-gray-500">Language Diversity</p>
              <p className={`text-xl font-semibold ${
                (summary.top_adjectives?.length || 0) > 8 ? 'text-green-600' :
                (summary.top_adjectives?.length || 0) > 4 ? 'text-blue-600' : 'text-amber-600'
              }`}>
                {(summary.top_adjectives?.length || 0) > 8 ? 'Rich' :
                 (summary.top_adjectives?.length || 0) > 4 ? 'Moderate' : 'Limited'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {summary.top_adjectives?.length || 0} unique descriptive words used
              </p>
            </div>
          </div>
        </div>
      )}

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

      {/* Excerpts / Sample Mentions */}
      {analyses.length > 0 && analyses.some((a) => a.excerpts && a.excerpts.length > 0) && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Sample Mentions</h2>
          <div className="space-y-4">
            {analyses
              .flatMap((a) => a.excerpts || [])
              .slice(0, 5)
              .map((excerpt, index) => (
                <div
                  key={index}
                  className="p-4 bg-gray-50 rounded-lg border-l-4"
                  style={{
                    borderLeftColor:
                      excerpt.sentiment > 0.1
                        ? '#22c55e'
                        : excerpt.sentiment < -0.1
                        ? '#ef4444'
                        : '#9ca3af',
                  }}
                >
                  <p className="text-sm text-gray-700 italic">"{excerpt.text}"</p>
                  <p className="mt-1 text-xs text-gray-500">
                    Sentiment: {excerpt.sentiment > 0 ? '+' : ''}{excerpt.sentiment.toFixed(2)}
                  </p>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!summary && (
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <MessageSquare className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No analysis data</h3>
          <p className="mt-1 text-sm text-gray-500">
            This player hasn't been mentioned in any analyzed transcripts yet.
          </p>
          <div className="mt-6">
            <Link
              to="/transcripts"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              Analyze Transcripts
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
