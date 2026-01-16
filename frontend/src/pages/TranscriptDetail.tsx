import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Play, Calendar, Users, Tag } from 'lucide-react';
import { transcriptApi, analysisApi } from '../api/client';
import type { Transcript, AnalysisResult } from '../types';

export default function TranscriptDetail() {
  const { id } = useParams<{ id: string }>();
  const [transcript, setTranscript] = useState<Transcript | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;

    async function fetchData() {
      try {
        const [transcriptData, analysisData] = await Promise.all([
          transcriptApi.get(id!),
          analysisApi.getForTranscript(id!).catch(() => []),
        ]);
        setTranscript(transcriptData);
        setAnalysis(analysisData);
      } catch (error) {
        console.error('Failed to fetch transcript:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [id]);

  async function handleAnalyze() {
    if (!id) return;
    try {
      await transcriptApi.analyze(id);
      alert('Analysis queued successfully');
    } catch (error) {
      console.error('Failed to trigger analysis:', error);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (!transcript) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Transcript not found</p>
        <Link to="/transcripts" className="text-primary-600 hover:underline mt-2 inline-block">
          Back to transcripts
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/transcripts"
            className="p-2 rounded-md hover:bg-gray-100"
          >
            <ArrowLeft className="h-5 w-5 text-gray-500" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {transcript.original_filename}
            </h1>
            <p className="text-gray-500">
              {transcript.word_count} words
            </p>
          </div>
        </div>
        <button
          onClick={handleAnalyze}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
        >
          <Play className="h-4 w-4 mr-2" />
          Analyze
        </button>
      </div>

      {/* Metadata */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Details</h2>
        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {transcript.game_date && (
            <div className="flex items-start">
              <Calendar className="h-5 w-5 text-gray-400 mr-2" />
              <div>
                <dt className="text-sm font-medium text-gray-500">Game Date</dt>
                <dd className="text-sm text-gray-900">{transcript.game_date}</dd>
              </div>
            </div>
          )}
          {transcript.sport && (
            <div className="flex items-start">
              <Tag className="h-5 w-5 text-gray-400 mr-2" />
              <div>
                <dt className="text-sm font-medium text-gray-500">Sport</dt>
                <dd className="text-sm text-gray-900">{transcript.sport}</dd>
              </div>
            </div>
          )}
          {transcript.teams && transcript.teams.length > 0 && (
            <div className="flex items-start">
              <Users className="h-5 w-5 text-gray-400 mr-2" />
              <div>
                <dt className="text-sm font-medium text-gray-500">Teams</dt>
                <dd className="text-sm text-gray-900">{transcript.teams.join(' vs ')}</dd>
              </div>
            </div>
          )}
          {transcript.commentators && transcript.commentators.length > 0 && (
            <div className="flex items-start">
              <Users className="h-5 w-5 text-gray-400 mr-2" />
              <div>
                <dt className="text-sm font-medium text-gray-500">Commentators</dt>
                <dd className="text-sm text-gray-900">{transcript.commentators.join(', ')}</dd>
              </div>
            </div>
          )}
        </dl>
      </div>

      {/* Analysis Results */}
      {analysis.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Analysis Results</h2>
          <div className="space-y-4">
            {analysis.map((result) => (
              <div key={result.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium">Player: {result.player_id}</p>
                    <p className="text-sm text-gray-500">
                      Mentions: {result.mention_count}
                    </p>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded-full ${
                      result.sentiment_label === 'positive'
                        ? 'bg-green-100 text-green-800'
                        : result.sentiment_label === 'negative'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {result.sentiment_label || 'N/A'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Transcript Content */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Content</h2>
        <div className="prose max-w-none">
          <pre className="whitespace-pre-wrap text-sm text-gray-700 bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
            {transcript.content}
          </pre>
        </div>
      </div>
    </div>
  );
}
