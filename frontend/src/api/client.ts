import axios from 'axios';
import type {
  Transcript,
  TranscriptListItem,
  Player,
  PlayerListItem,
  AnalysisResult,
  PlayerAnalysisSummary,
  UploadResponse,
  TranscriptBiasAnalysis,
  ComparativeAnalysis,
} from '../types';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Transcript API
export const transcriptApi = {
  list: async (params?: { sport?: string; processed?: boolean }) => {
    const response = await api.get<TranscriptListItem[]>('/transcripts', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await api.get<Transcript>(`/transcripts/${id}`);
    return response.data;
  },

  upload: async (file: File, metadata?: {
    game_date?: string;
    sport?: string;
    teams?: string;
    commentators?: string;
    source?: string;
  }) => {
    const formData = new FormData();
    formData.append('file', file);
    if (metadata?.game_date) formData.append('game_date', metadata.game_date);
    if (metadata?.sport) formData.append('sport', metadata.sport);
    if (metadata?.teams) formData.append('teams', metadata.teams);
    if (metadata?.commentators) formData.append('commentators', metadata.commentators);
    if (metadata?.source) formData.append('source', metadata.source);

    const response = await api.post<UploadResponse>('/transcripts/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  uploadText: async (content: string, title: string, metadata?: {
    game_date?: string;
    sport?: string;
    teams?: string;
    commentators?: string;
    source?: string;
  }) => {
    const formData = new FormData();
    formData.append('content', content);
    formData.append('title', title);
    if (metadata?.game_date) formData.append('game_date', metadata.game_date);
    if (metadata?.sport) formData.append('sport', metadata.sport);
    if (metadata?.teams) formData.append('teams', metadata.teams);
    if (metadata?.commentators) formData.append('commentators', metadata.commentators);
    if (metadata?.source) formData.append('source', metadata.source);

    const response = await api.post<UploadResponse>('/transcripts/text', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  delete: async (id: string) => {
    await api.delete(`/transcripts/${id}`);
  },

  analyze: async (id: string) => {
    const response = await api.post(`/transcripts/${id}/analyze`);
    return response.data;
  },
};

// Player API
export const playerApi = {
  list: async (params?: { sport?: string; team?: string }) => {
    const response = await api.get<PlayerListItem[]>('/players', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await api.get<Player>(`/players/${id}`);
    return response.data;
  },

  create: async (player: Omit<Player, 'id' | 'created_at' | 'updated_at'>) => {
    const response = await api.post<Player>('/players', player);
    return response.data;
  },

  update: async (id: string, data: Partial<Player>) => {
    const response = await api.put<Player>(`/players/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    await api.delete(`/players/${id}`);
  },
};

// Analysis API
export const analysisApi = {
  getForPlayer: async (playerId: string) => {
    const response = await api.get<AnalysisResult[]>(`/analysis/player/${playerId}`);
    return response.data;
  },

  getPlayerSummary: async (playerId: string) => {
    const response = await api.get<PlayerAnalysisSummary>(`/analysis/player/${playerId}/summary`);
    return response.data;
  },

  getForTranscript: async (transcriptId: string) => {
    const response = await api.get<AnalysisResult[]>(`/analysis/transcript/${transcriptId}`);
    return response.data;
  },

  compare: async (playerIds: string[]) => {
    const response = await api.get('/analysis/compare', {
      params: { player_ids: playerIds.join(',') },
    });
    return response.data;
  },

  getDashboardStats: async () => {
    const response = await api.get<{
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
    }>('/analysis/dashboard/stats');
    return response.data;
  },

  getTranscriptBias: async (transcriptId: string) => {
    const response = await api.get<TranscriptBiasAnalysis>(`/analysis/transcript/${transcriptId}/bias`);
    return response.data;
  },

  compareBias: async (playerIds: string[]) => {
    const response = await api.get<{
      fairness_score: number;
      most_favored: string | null;
      least_favored: string | null;
      disparity_score: number;
      player_rankings: Array<{
        player_name: string;
        rank: number;
        bias_score: number;
        bias_level: string;
        confidence: number;
      }>;
    }>('/analysis/compare/bias', {
      params: { player_ids: playerIds.join(',') },
    });
    return response.data;
  },
};

export default api;
