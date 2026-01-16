import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload as UploadIcon, FileText, X } from 'lucide-react';
import { transcriptApi } from '../api/client';

type UploadMode = 'file' | 'text';

export default function Upload() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<UploadMode>('file');
  const [file, setFile] = useState<File | null>(null);
  const [textContent, setTextContent] = useState('');
  const [title, setTitle] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Metadata
  const [gameDate, setGameDate] = useState('');
  const [sport, setSport] = useState('');
  const [teams, setTeams] = useState('');
  const [commentators, setCommentators] = useState('');
  const [source, setSource] = useState('');

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      validateAndSetFile(droppedFile);
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile: File) => {
    const allowedExtensions = ['txt', 'srt', 'vtt', 'json'];
    const extension = selectedFile.name.split('.').pop()?.toLowerCase();

    if (!extension || !allowedExtensions.includes(extension)) {
      setError(`Invalid file type. Allowed: ${allowedExtensions.join(', ')}`);
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File too large. Maximum size: 10MB');
      return;
    }

    setFile(selectedFile);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setUploading(true);

    const metadata = {
      game_date: gameDate || undefined,
      sport: sport || undefined,
      teams: teams || undefined,
      commentators: commentators || undefined,
      source: source || undefined,
    };

    try {
      if (mode === 'file' && file) {
        await transcriptApi.upload(file, metadata);
      } else if (mode === 'text' && textContent.trim()) {
        await transcriptApi.uploadText(
          textContent,
          title || 'Untitled Transcript',
          metadata
        );
      } else {
        setError('Please provide a file or text content');
        setUploading(false);
        return;
      }

      navigate('/transcripts');
    } catch (err) {
      console.error('Upload failed:', err);
      setError('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload Transcript</h1>
        <p className="mt-1 text-gray-600">
          Upload a commentary transcript file or paste text directly.
        </p>
      </div>

      {/* Mode Toggle */}
      <div className="bg-white shadow rounded-lg p-1 inline-flex">
        <button
          type="button"
          onClick={() => setMode('file')}
          className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
            mode === 'file'
              ? 'bg-primary-100 text-primary-700'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Upload File
        </button>
        <button
          type="button"
          onClick={() => setMode('text')}
          className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
            mode === 'text'
              ? 'bg-primary-100 text-primary-700'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Paste Text
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* File Upload */}
        {mode === 'file' && (
          <div
            className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {file ? (
              <div className="flex items-center justify-center space-x-4">
                <FileText className="h-10 w-10 text-primary-500" />
                <div className="text-left">
                  <p className="font-medium text-gray-900">{file.name}</p>
                  <p className="text-sm text-gray-500">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setFile(null)}
                  className="p-1 text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            ) : (
              <>
                <UploadIcon className="mx-auto h-12 w-12 text-gray-400" />
                <p className="mt-2 text-sm text-gray-600">
                  Drag and drop your file here, or{' '}
                  <label className="text-primary-600 hover:text-primary-500 cursor-pointer">
                    browse
                    <input
                      type="file"
                      className="sr-only"
                      accept=".txt,.srt,.vtt,.json"
                      onChange={handleFileChange}
                    />
                  </label>
                </p>
                <p className="mt-1 text-xs text-gray-500">
                  TXT, SRT, VTT, or JSON up to 10MB
                </p>
              </>
            )}
          </div>
        )}

        {/* Text Input */}
        {mode === 'text' && (
          <div className="space-y-4">
            <div>
              <label
                htmlFor="title"
                className="block text-sm font-medium text-gray-700"
              >
                Title
              </label>
              <input
                type="text"
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter a title for this transcript"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              />
            </div>
            <div>
              <label
                htmlFor="content"
                className="block text-sm font-medium text-gray-700"
              >
                Content
              </label>
              <textarea
                id="content"
                rows={10}
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                placeholder="Paste your commentary transcript here..."
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              />
            </div>
          </div>
        )}

        {/* Metadata */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Metadata (Optional)
          </h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label
                htmlFor="gameDate"
                className="block text-sm font-medium text-gray-700"
              >
                Game Date
              </label>
              <input
                type="date"
                id="gameDate"
                value={gameDate}
                onChange={(e) => setGameDate(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              />
            </div>
            <div>
              <label
                htmlFor="sport"
                className="block text-sm font-medium text-gray-700"
              >
                Sport
              </label>
              <input
                type="text"
                id="sport"
                value={sport}
                onChange={(e) => setSport(e.target.value)}
                placeholder="e.g., Football, Basketball"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              />
            </div>
            <div>
              <label
                htmlFor="teams"
                className="block text-sm font-medium text-gray-700"
              >
                Teams
              </label>
              <input
                type="text"
                id="teams"
                value={teams}
                onChange={(e) => setTeams(e.target.value)}
                placeholder="e.g., Lakers, Celtics (comma-separated)"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              />
            </div>
            <div>
              <label
                htmlFor="commentators"
                className="block text-sm font-medium text-gray-700"
              >
                Commentators
              </label>
              <input
                type="text"
                id="commentators"
                value={commentators}
                onChange={(e) => setCommentators(e.target.value)}
                placeholder="e.g., John Smith, Jane Doe (comma-separated)"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              />
            </div>
            <div className="sm:col-span-2">
              <label
                htmlFor="source"
                className="block text-sm font-medium text-gray-700"
              >
                Source
              </label>
              <input
                type="text"
                id="source"
                value={source}
                onChange={(e) => setSource(e.target.value)}
                placeholder="e.g., ESPN, NBC Sports"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              />
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Submit */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate('/transcripts')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={uploading || (mode === 'file' && !file) || (mode === 'text' && !textContent.trim())}
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? 'Uploading...' : 'Upload Transcript'}
          </button>
        </div>
      </form>
    </div>
  );
}
