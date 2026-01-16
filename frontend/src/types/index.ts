export interface Transcript {
  id: string;
  filename: string;
  original_filename: string;
  content: string;
  game_date: string | null;
  sport: string | null;
  teams: string[] | null;
  commentators: string[] | null;
  source: string | null;
  processed: boolean;
  word_count: string | null;
  uploaded_at: string;
  processed_at: string | null;
}

export interface TranscriptListItem {
  id: string;
  filename: string;
  original_filename: string;
  sport: string | null;
  teams: string[] | null;
  processed: boolean;
  word_count: string | null;
  uploaded_at: string;
}

export interface Player {
  id: string;
  name: string;
  aliases: string[];
  team: string | null;
  sport: string | null;
  position: string | null;
  created_at: string;
  updated_at: string;
}

export interface PlayerListItem {
  id: string;
  name: string;
  team: string | null;
  sport: string | null;
}

export interface AdjectiveDetail {
  word: string;
  count: number;
  sentiment: number | null;
}

export interface PhraseDetail {
  phrase: string;
  count: number;
  context: string | null;
}

export interface ExcerptDetail {
  text: string;
  sentiment: number;
  position: number | null;
}

export interface AnalysisResult {
  id: string;
  transcript_id: string;
  player_id: string;
  sentiment_score: number | null;
  sentiment_label: 'positive' | 'negative' | 'neutral' | null;
  confidence: number | null;
  mention_count: number;
  adjectives: AdjectiveDetail[];
  phrases: PhraseDetail[];
  excerpts: ExcerptDetail[];
  analyzed_at: string;
}

export interface PlayerAnalysisSummary {
  player_id: string;
  player_name: string;
  total_mentions: number;
  average_sentiment: number | null;
  sentiment_label: 'positive' | 'negative' | 'neutral' | null;
  top_adjectives: AdjectiveDetail[];
  top_phrases: PhraseDetail[];
  transcript_count: number;
}

export interface UploadResponse {
  id: string;
  filename: string;
  message: string;
}

// Bias Analysis Types
export interface BiasIndicator {
  category: string;
  description: string;
  score: number;
  weight: number;
  evidence: string[];
}

export interface PlayerBiasScore {
  player_id: string;
  player_name: string;
  bias_score: number;
  bias_level: 'minimal' | 'low' | 'moderate' | 'high' | 'severe';
  confidence: number;
  indicators: BiasIndicator[];
}

export interface PlayerComparisonItem {
  player_id: string;
  player_name: string;
  rank: number;
  bias_score: number;
  bias_level: string;
  sentiment_score: number | null;
  mention_count: number;
}

export interface ComparativeAnalysis {
  fairness_score: number;
  most_favored: string | null;
  least_favored: string | null;
  disparity_score: number;
  players: PlayerComparisonItem[];
}

export interface TranscriptBiasAnalysis {
  transcript_id: string;
  players_analyzed: number;
  comparative_analysis: ComparativeAnalysis | null;
  player_scores: PlayerBiasScore[];
}
