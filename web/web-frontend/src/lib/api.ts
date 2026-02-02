/**
 * API client for FretCoach Hub
 * Handles communication with the serverless API routes
 */

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';


export interface Session {
  session_id: string;
  user_id: string;
  start_timestamp: string;
  end_timestamp: string | null;
  pitch_accuracy: number | null;
  scale_conformity: number | null;
  timing_stability: number | null;
  scale_chosen: string;
  scale_type: string;
  sensitivity: number;
  strictness: number;
  total_notes_played: number;
  correct_notes_played: number;
  bad_notes_played: number;
  total_inscale_notes: number | null;
  duration_seconds: number | null;
  ambient_light_option: boolean;
}

export interface SessionAggregates {
  total_sessions: number;
  total_practice_time: number;
  avg_pitch_accuracy: number;
  avg_scale_conformity: number;
  avg_timing_stability: number;
  total_notes: number;
  total_correct: number;
  scales_practiced: string[];
}

export interface DateRange {
  start: string | null;
  end: string | null;
}

export interface SessionsResponse {
  success: boolean;
  sessions: Session[];
  aggregates: SessionAggregates | null;
  dateRange?: DateRange;
  error?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  chartData?: ChartData | null;
}

export interface ChartData {
  type: 'performance_trend' | 'comparison' | 'practice_plan';
  data: any;
  metric?: string;
  plan_id?: string;  // For practice plans
}

export interface ChatResponse {
  success: boolean;
  message: {
    role: 'assistant';
    content: string;
  };
  chartData?: ChartData | null;
  modelUsed?: string;
  sessionContext?: {
    total_sessions: number;
    weakest_area: string;
  };
  error?: string;
}

/**
 * Fetch sessions from the API
 */
export async function fetchSessions(
  userId: string = 'default_user',
  limit: number = 10,
  includeAggregates: boolean = true,
  startDate?: string,
  endDate?: string
): Promise<SessionsResponse> {
  try {
    const params = new URLSearchParams({
      user_id: userId,
      limit: limit.toString(),
      include_aggregates: includeAggregates.toString(),
    });

    if (startDate) {
      params.append('start_date', startDate);
    }
    if (endDate) {
      params.append('end_date', endDate);
    }

    const response = await fetch(`${API_BASE}/sessions?${params}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch sessions:', error);
    return {
      success: false,
      sessions: [],
      aggregates: null,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Send a chat message to the AI Coach
 */
export async function sendChatMessage(
  messages: { role: 'user' | 'assistant'; content: string }[],
  userId: string = 'default_user',
  threadId?: string
): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages,
        user_id: userId,
        thread_id: threadId,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to send chat message:', error);
    return {
      success: false,
      message: {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      },
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Save a practice plan
 */
export async function savePracticePlan(
  planId: string,
  userId: string = 'default_user'
): Promise<{ success: boolean; error?: string }> {
  try {
    const response = await fetch(`${API_BASE}/save-plan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        plan_id: planId,
        user_id: userId,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to save practice plan:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Format duration in seconds to human readable string
 */
export function formatDuration(seconds: number | null): string {
  if (!seconds) return '0 min';
  const mins = Math.floor(seconds / 60);
  if (mins < 60) return `${mins} min`;
  const hours = Math.floor(mins / 60);
  const remainingMins = mins % 60;
  return `${hours}h ${remainingMins}m`;
}

/**
 * Format date string to human readable format
 */
export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Calculate percentage change between two values
 */
export function calculateChange(current: number, previous: number): number {
  if (previous === 0) return current > 0 ? 100 : 0;
  return Math.round(((current - previous) / previous) * 100);
}