import { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Check, X } from 'lucide-react';
import type { ChartData } from '@/lib/api';

interface PerformanceChartProps {
  chartData: ChartData;
  onSavePlan?: (planId: string) => Promise<void>;
  onDismissPlan?: () => void;
}

const COLORS = {
  pitch_accuracy: '#8884d8',
  scale_conformity: '#82ca9d',
  timing_stability: '#ffc658',
  primary: 'hsl(var(--primary))',
};

export function PerformanceChart({ chartData, onSavePlan, onDismissPlan }: PerformanceChartProps) {
  if (chartData.type === 'performance_trend') {
    return <TrendChart data={chartData.data} metric={chartData.metric} />;
  }

  if (chartData.type === 'comparison') {
    return <ComparisonChart data={chartData.data} />;
  }

  if (chartData.type === 'practice_plan') {
    return (
      <PracticePlanCard
        data={chartData.data}
        planId={chartData.plan_id}
        onSave={onSavePlan}
        onDismiss={onDismissPlan}
      />
    );
  }

  return null;
}

function TrendChart({ data, metric }: { data: any[]; metric?: string }) {
  const showAll = metric === 'all' || !metric;

  return (
    <Card className="w-full mt-4 bg-card/50 border-primary/20">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">Performance Trend</CardTitle>
        <CardDescription className="text-xs">
          Your metrics over the last {data.length} sessions
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 10 }}
              className="text-muted-foreground"
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 10 }}
              className="text-muted-foreground"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
              }}
            />
            <Legend wrapperStyle={{ fontSize: '10px' }} />
            {(showAll || metric === 'pitch_accuracy') && (
              <Line
                type="monotone"
                dataKey="pitch_accuracy"
                stroke={COLORS.pitch_accuracy}
                strokeWidth={2}
                dot={{ r: 3 }}
                name="Pitch"
              />
            )}
            {(showAll || metric === 'scale_conformity') && (
              <Line
                type="monotone"
                dataKey="scale_conformity"
                stroke={COLORS.scale_conformity}
                strokeWidth={2}
                dot={{ r: 3 }}
                name="Scale"
              />
            )}
            {(showAll || metric === 'timing_stability') && (
              <Line
                type="monotone"
                dataKey="timing_stability"
                stroke={COLORS.timing_stability}
                strokeWidth={2}
                dot={{ r: 3 }}
                name="Timing"
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

function ComparisonChart({ data }: { data: { latest: any; average: any } }) {
  const chartData = [
    {
      metric: 'Pitch',
      Latest: data.latest.pitch,
      Average: data.average.pitch,
    },
    {
      metric: 'Scale',
      Latest: data.latest.scale,
      Average: data.average.scale,
    },
    {
      metric: 'Timing',
      Latest: data.latest.timing,
      Average: data.average.timing,
    },
  ];

  const radarData = [
    { subject: 'Pitch', Latest: data.latest.pitch, Average: data.average.pitch },
    { subject: 'Scale', Latest: data.latest.scale, Average: data.average.scale },
    { subject: 'Timing', Latest: data.latest.timing, Average: data.average.timing },
  ];

  return (
    <Card className="w-full mt-4 bg-card/50 border-primary/20">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">Latest vs Average</CardTitle>
        <CardDescription className="text-xs">
          Comparing your most recent session to your overall average
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          {/* Bar Chart */}
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="metric" tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                }}
              />
              <Bar dataKey="Latest" fill={COLORS.pitch_accuracy} />
              <Bar dataKey="Average" fill={COLORS.scale_conformity} />
            </BarChart>
          </ResponsiveContainer>

          {/* Radar Chart */}
          <ResponsiveContainer width="100%" height={180}>
            <RadarChart data={radarData}>
              <PolarGrid className="stroke-muted" />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10 }} />
              <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 8 }} />
              <Radar
                name="Latest"
                dataKey="Latest"
                stroke={COLORS.pitch_accuracy}
                fill={COLORS.pitch_accuracy}
                fillOpacity={0.3}
              />
              <Radar
                name="Average"
                dataKey="Average"
                stroke={COLORS.scale_conformity}
                fill={COLORS.scale_conformity}
                fillOpacity={0.3}
              />
              <Legend wrapperStyle={{ fontSize: '10px' }} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

interface PracticePlanCardProps {
  data: any;
  planId?: string;
  onSave?: (planId: string) => Promise<void>;
  onDismiss?: () => void;
}

function PracticePlanCard({ data, planId, onSave, onDismiss }: PracticePlanCardProps) {
  const [saveState, setSaveState] = useState<'idle' | 'saving' | 'saved' | 'dismissed'>('idle');

  const handleSave = async () => {
    if (!planId || !onSave) return;
    setSaveState('saving');
    try {
      await onSave(planId);
      setSaveState('saved');
    } catch (error) {
      setSaveState('idle');
    }
  };

  const handleDismiss = () => {
    setSaveState('dismissed');
    onDismiss?.();
  };

  return (
    <Card className="w-full mt-4 bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <span className="text-lg">🎯</span>
          Practice Plan
          {saveState === 'saved' && (
            <span className="ml-auto text-xs text-green-600 flex items-center gap-1">
              <Check className="h-3 w-3" /> Saved
            </span>
          )}
        </CardTitle>
        <CardDescription className="text-xs">
          Personalized recommendation based on your data
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex justify-between items-center p-2 rounded bg-background/50">
          <span className="text-xs text-muted-foreground">Focus Area</span>
          <span className="text-sm font-medium">{data.focus_area}</span>
        </div>
        <div className="flex justify-between items-center p-2 rounded bg-background/50">
          <span className="text-xs text-muted-foreground">Current Score</span>
          <span className="text-sm font-medium">{data.current_score}%</span>
        </div>
        <div className="flex justify-between items-center p-2 rounded bg-background/50">
          <span className="text-xs text-muted-foreground">Suggested Scale</span>
          <span className="text-sm font-medium">
            {data.suggested_scale}
            {data.suggested_scale_type && ` (${data.suggested_scale_type})`}
          </span>
        </div>
        <div className="flex justify-between items-center p-2 rounded bg-background/50">
          <span className="text-xs text-muted-foreground">Session Duration</span>
          <span className="text-sm font-medium">{data.session_target}</span>
        </div>
        {data.exercises && (
          <div className="pt-2 border-t border-border">
            <span className="text-xs text-muted-foreground block mb-2">Exercises:</span>
            <ul className="space-y-1">
              {data.exercises.map((exercise: string, i: number) => (
                <li key={i} className="text-xs flex items-start gap-2">
                  <span className="text-primary">•</span>
                  {exercise}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Save/Dismiss buttons */}
        {planId && saveState === 'idle' && (
          <div className="pt-3 border-t border-border flex gap-2">
            <Button
              size="sm"
              onClick={handleSave}
              className="flex-1"
            >
              <Check className="h-4 w-4 mr-1" />
              Save Plan
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={handleDismiss}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        )}

        {saveState === 'saving' && (
          <div className="pt-3 border-t border-border text-center text-xs text-muted-foreground">
            Saving...
          </div>
        )}

        {saveState === 'dismissed' && (
          <div className="pt-3 border-t border-border text-center text-xs text-muted-foreground">
            Plan dismissed
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default PerformanceChart;
