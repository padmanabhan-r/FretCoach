export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.1"
  }
  public: {
    Tables: {
      fretcoach_sessions_test: {
        Row: {
          avg_ioi_ms: number | null
          avg_pitch_deviation_cents: number | null
          bend_accuracy_ratio: number | null
          bends_attempted: number | null
          created_at: string | null
          dominant_issue: string | null
          duration_sec: number | null
          end_time: string | null
          energy_consistency: number | null
          flow_state_ratio: number | null
          hesitation_events: number | null
          in_scale_ratio: number | null
          legato_ratio: number | null
          notes_detected: number | null
          pitch_stability_score: number | null
          practice_mode: string | null
          rushing_events: number | null
          scales_practiced: string[] | null
          session_id: string
          slides_detected: number | null
          stable_timing_ratio: number | null
          start_time: string
          timing_variance: number | null
          user_id: string | null
          vibrato_detected: boolean | null
          window_end_sec: number | null
          window_start_sec: number | null
          window_type: string | null
        }
        Insert: {
          avg_ioi_ms?: number | null
          avg_pitch_deviation_cents?: number | null
          bend_accuracy_ratio?: number | null
          bends_attempted?: number | null
          created_at?: string | null
          dominant_issue?: string | null
          duration_sec?: number | null
          end_time?: string | null
          energy_consistency?: number | null
          flow_state_ratio?: number | null
          hesitation_events?: number | null
          in_scale_ratio?: number | null
          legato_ratio?: number | null
          notes_detected?: number | null
          pitch_stability_score?: number | null
          practice_mode?: string | null
          rushing_events?: number | null
          scales_practiced?: string[] | null
          session_id: string
          slides_detected?: number | null
          stable_timing_ratio?: number | null
          start_time: string
          timing_variance?: number | null
          user_id?: string | null
          vibrato_detected?: boolean | null
          window_end_sec?: number | null
          window_start_sec?: number | null
          window_type?: string | null
        }
        Update: {
          avg_ioi_ms?: number | null
          avg_pitch_deviation_cents?: number | null
          bend_accuracy_ratio?: number | null
          bends_attempted?: number | null
          created_at?: string | null
          dominant_issue?: string | null
          duration_sec?: number | null
          end_time?: string | null
          energy_consistency?: number | null
          flow_state_ratio?: number | null
          hesitation_events?: number | null
          in_scale_ratio?: number | null
          legato_ratio?: number | null
          notes_detected?: number | null
          pitch_stability_score?: number | null
          practice_mode?: string | null
          rushing_events?: number | null
          scales_practiced?: string[] | null
          session_id?: string
          slides_detected?: number | null
          stable_timing_ratio?: number | null
          start_time?: string
          timing_variance?: number | null
          user_id?: string | null
          vibrato_detected?: boolean | null
          window_end_sec?: number | null
          window_start_sec?: number | null
          window_type?: string | null
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
