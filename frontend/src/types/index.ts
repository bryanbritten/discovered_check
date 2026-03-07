export interface User {
  id: number;
  username: string;
  lichess_id: string;
  lichess_username: string;
  avatar_url: string | null;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export type UserColor = "white" | "black";
export type UserResult = "win" | "loss" | "draw";
export type TimeControlCategory =
  | "ultrabullet"
  | "bullet"
  | "blitz"
  | "rapid"
  | "classical"
  | "correspondence"
  | "unknown";
export type TacticType = "fork" | "pin" | "skewer";
export type TimeCategory = "instant" | "quick" | "normal" | "considered" | "long_think";

export interface Game {
  id: string;
  source: "lichess" | "pgn_import";
  lichess_game_id: string | null;
  white_username: string;
  black_username: string;
  user_color: UserColor;
  user_rating: number | null;
  opponent_rating: number | null;
  result: "white" | "black" | "draw";
  user_result: UserResult;
  termination: string;
  time_control: string;
  time_control_category: TimeControlCategory;
  opening_name: string;
  opening_eco: string;
  played_at: string;
  analysis_complete: boolean;
}

export interface Move {
  ply: number;
  move_number: number;
  color: UserColor;
  san: string;
  uci: string;
  fen_before: string;
  fen_after: string;
  clock_time_remaining: number | null;
  time_spent: number | null;
}

export interface GameDetail extends Game {
  pgn: string;
  moves: Move[];
}

// Analytics types

export interface ColorStats {
  total: number;
  wins: number;
  losses: number;
  draws: number;
  win_rate: number;
}

export interface TimeControlBreakdown {
  category: TimeControlCategory;
  total: number;
  wins: number;
  losses: number;
  draws: number;
  win_rate: number;
}

export interface MonthlyTrend {
  month: string;
  total: number;
  wins: number;
  win_rate: number;
}

export interface OpeningPerformance {
  opening_name: string;
  opening_eco: string;
  total: number;
  wins: number;
  losses: number;
  draws: number;
}

export interface OverviewStats {
  total_games: number;
  wins: number;
  losses: number;
  draws: number;
  win_rate: number;
  as_white: ColorStats;
  as_black: ColorStats;
  by_time_control: TimeControlBreakdown[];
  by_termination: { termination: string; count: number }[];
  monthly_trend: MonthlyTrend[];
  top_openings: OpeningPerformance[];
}

export interface TacticTarget {
  square: string;
  piece: string;
  role?: string;
}

export interface TacticsOpportunity {
  id: number;
  game_id: string;
  lichess_game_id: string | null;
  played_at: string;
  tactic_type: TacticType;
  missed: boolean;
  best_move_uci: string;
  played_move_uci: string;
  attacking_piece: string;
  attacking_square: string;
  targets: TacticTarget[];
  fen: string;
  description: string;
  move_number: number;
  move_color: UserColor;
}

export interface TacticsSummary {
  total: number;
  missed_total: number;
  forks: number;
  pins: number;
  skewers: number;
  forks_missed: number;
  pins_missed: number;
  skewers_missed: number;
}

export interface TacticsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: TacticsOpportunity[];
  summary: TacticsSummary;
}

export interface TimeControlTimeStats {
  category: TimeControlCategory;
  avg_time_per_move: number | null;
  move_count: number;
}

export interface TimeCategoryCount {
  category: TimeCategory;
  count: number;
}

export interface WinRateSummary {
  total: number;
  wins: number;
  win_rate: number;
}

export interface TimeByResult {
  result: UserResult;
  avg_time_per_move: number | null;
  move_count: number;
}

export interface TimeAnalysis {
  overall: {
    avg_time_per_move: number | null;
    total_moves_analyzed: number;
  };
  by_time_control: TimeControlTimeStats[];
  time_category_distribution: TimeCategoryCount[];
  long_think_correlation: {
    games_with_long_think: WinRateSummary;
    games_without_long_think: WinRateSummary;
  };
  time_by_result: TimeByResult[];
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface LichessSync {
  status: "idle" | "syncing" | "failed";
  games_synced: number;
  last_synced_at: string | null;
  started_at: string | null;
  error_message: string;
}

export interface PGNImport {
  id: number;
  filename: string;
  status: "pending" | "processing" | "complete" | "failed";
  total_games: number | null;
  processed_games: number;
  failed_games: number;
  error_message: string;
  created_at: string;
  completed_at: string | null;
}
