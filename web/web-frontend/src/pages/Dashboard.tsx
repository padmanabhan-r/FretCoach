import { useState, useEffect, useRef, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Clock,
  Music2,
  Target,
  CalendarIcon,
  BarChart3,
  AlertCircle,
  Zap,
  Guitar,
  Send,
  Brain,
  Sparkles,
  RefreshCw,
  Maximize2,
  Minimize2,
} from "lucide-react";
import { Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { format, subDays } from "date-fns";
import { useSessions, type DateRangeFilter } from "@/hooks/useSessions";
import { sendChatMessage, savePracticePlan, formatDuration, formatDate, type ChatMessage, type ChartData } from "@/lib/api";
import { PerformanceChart } from "@/components/charts/PerformanceChart";
import type { DateRange } from "react-day-picker";

// Initial welcome message for the AI Coach
const initialMessages: ChatMessage[] = [
  {
    id: "1",
    role: "assistant",
    content: "Hi! I'm your AI practice coach. I can help you analyze your performance, suggest exercises, and answer questions about your practice sessions. Try asking me:\n\n• \"Show me my progress\"\n• \"What should I practice today?\"\n• \"How am I doing compared to average?\"\n\nHow can I help you today?",
  }
];

const Dashboard = () => {
  // Default to last 7 days
  const [dateRange, setDateRange] = useState<DateRange | undefined>(() => ({
    from: subDays(new Date(), 7),
    to: new Date(),
  }));

  // Convert date range to API format
  const dateRangeFilter = useMemo<DateRangeFilter | undefined>(() => {
    if (!dateRange?.from) return undefined;
    return {
      startDate: format(dateRange.from, 'yyyy-MM-dd'),
      endDate: dateRange.to ? format(dateRange.to, 'yyyy-MM-dd') : format(new Date(), 'yyyy-MM-dd'),
    };
  }, [dateRange]);

  const { data, isLoading, error, refetch, isFetching } = useSessions('default_user', 6, dateRangeFilter);
  const [selectedSessionIndex, setSelectedSessionIndex] = useState(0);
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [inputMessage, setInputMessage] = useState("");
  const [isAiTyping, setIsAiTyping] = useState(false);
  const [currentModel, setCurrentModel] = useState<string>("");
  const [isAiCoachExpanded, setIsAiCoachExpanded] = useState(false);
  const [threadId] = useState(() => `thread-${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sessions = data?.sessions || [];
  const aggregates = data?.aggregates;
  const selectedSession = sessions[selectedSessionIndex];

  // Format date range display
  const dateRangeLabel = useMemo(() => {
    if (!dateRange?.from) return "Select dates";
    if (!dateRange.to) return format(dateRange.from, "MMM d, yyyy");
    return `${format(dateRange.from, "MMM d")} - ${format(dateRange.to, "MMM d, yyyy")}`;
  }, [dateRange]);

  // Scroll to bottom of chat when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isAiTyping) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: inputMessage,
    };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setIsAiTyping(true);

    try {
      // Build message history for the API
      const messageHistory = [...messages, userMessage].map(m => ({
        role: m.role,
        content: m.content,
      }));

      const response = await sendChatMessage(messageHistory, 'default_user', threadId);

      // Track which model was used
      if (response.modelUsed) {
        setCurrentModel(response.modelUsed);
      }

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.message.content,
        chartData: response.chartData,
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsAiTyping(false);
    }
  };

  const handleSavePlan = async (planId: string) => {
    const result = await savePracticePlan(planId, 'default_user');
    if (!result.success) {
      throw new Error(result.error || 'Failed to save plan');
    }
  };

  // Calculate trend indicators
  const calculateTrend = (metric: 'pitch_accuracy' | 'scale_conformity' | 'timing_stability') => {
    if (sessions.length < 2) return { value: 0, isUp: true };
    const recent = sessions.slice(0, 3).reduce((sum, s) => sum + (s[metric] || 0), 0) / Math.min(3, sessions.length);
    const older = sessions.slice(3, 6).reduce((sum, s) => sum + (s[metric] || 0), 0) / Math.min(3, sessions.slice(3, 6).length);
    if (older === 0) return { value: 0, isUp: true };
    const change = Math.round((recent - older) * 100);
    return { value: Math.abs(change), isUp: change >= 0 };
  };

  const pitchTrend = calculateTrend('pitch_accuracy');
  const timingTrend = calculateTrend('timing_stability');
  const scaleTrend = calculateTrend('scale_conformity');

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Failed to load data</h2>
            <p className="text-muted-foreground mb-4">
              Please check your connection and try again.
            </p>
            <Button onClick={() => refetch()}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50">
        <div className="container px-4 md:px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link to="/">
                <Button variant="ghost" size="icon">
                  <ArrowLeft className="h-5 w-5" />
                </Button>
              </Link>
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-lg bg-primary/10">
                  <Guitar className="h-6 w-6 text-primary" />
                </div>
                <h1 className="text-xl font-bold">FretCoach Dashboard</h1>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="outline" onClick={() => refetch()}>
                <RefreshCw className={`h-4 w-4 mr-2 ${isFetching ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <div className="flex items-center gap-3 pl-4 border-l border-border">
                <div className="text-right hidden sm:block">
                  <p className="text-sm font-medium">Default User</p>
                  <p className="text-xs text-muted-foreground">
                    FretCoach Premium
                  </p>
                </div>
                <Avatar className="h-10 w-10 border-2 border-primary/20">
                  <AvatarImage src="" alt="FretCoach User" />
                  <AvatarFallback className="bg-primary/10 text-primary">
                    <Guitar className="h-5 w-5" />
                  </AvatarFallback>
                </Avatar>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="container px-4 md:px-6 py-3">
        {/* Performance Summary Header */}
        <div className="flex items-center justify-between mb-2">
          <div>
            <h2 className="text-lg font-semibold">Your Performance</h2>
            <p className="text-xs text-muted-foreground">Average metrics for selected period</p>
          </div>
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" size="sm" className="h-8 text-xs gap-2">
                <CalendarIcon className="h-3 w-3" />
                {dateRangeLabel}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="end">
              <Calendar
                mode="range"
                selected={dateRange}
                onSelect={setDateRange}
                numberOfMonths={2}
                disabled={(date) => date > new Date()}
              />
              <div className="flex gap-2 p-3 border-t">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 text-xs"
                  onClick={() => setDateRange({ from: subDays(new Date(), 7), to: new Date() })}
                >
                  Last 7 days
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 text-xs"
                  onClick={() => setDateRange({ from: subDays(new Date(), 30), to: new Date() })}
                >
                  Last 30 days
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 text-xs"
                  onClick={() => setDateRange(undefined)}
                >
                  All time
                </Button>
              </div>
            </PopoverContent>
          </Popover>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
          <Card className="bg-card border-border/50">
            <CardHeader className="pb-1 pt-3">
              <div className="flex items-center justify-between">
                <Music2 className="h-5 w-5 text-primary" />
                {isLoading ? (
                  <Skeleton className="h-4 w-8" />
                ) : (
                  <span className={`text-xs font-medium flex items-center gap-1 ${pitchTrend.isUp ? 'text-green-500' : 'text-red-500'}`}>
                    {pitchTrend.isUp ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                    {pitchTrend.value}%
                  </span>
                )}
              </div>
            </CardHeader>
            <CardContent className="pb-3">
              {isLoading ? (
                <Skeleton className="h-6 w-12" />
              ) : (
                <CardTitle className="text-xl md:text-2xl font-bold">
                  {Math.round((aggregates?.avg_pitch_accuracy || 0) * 100)}%
                </CardTitle>
              )}
              <p className="text-xs text-muted-foreground">Pitch Accuracy</p>
            </CardContent>
          </Card>

          <Card className="bg-card border-border/50">
            <CardHeader className="pb-1 pt-3">
              <div className="flex items-center justify-between">
                <Clock className="h-5 w-5 text-primary" />
                {isLoading ? (
                  <Skeleton className="h-4 w-8" />
                ) : (
                  <span className={`text-xs font-medium flex items-center gap-1 ${timingTrend.isUp ? 'text-green-500' : 'text-red-500'}`}>
                    {timingTrend.isUp ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                    {timingTrend.value}%
                  </span>
                )}
              </div>
            </CardHeader>
            <CardContent className="pb-3">
              {isLoading ? (
                <Skeleton className="h-6 w-12" />
              ) : (
                <CardTitle className="text-xl md:text-2xl font-bold">
                  {Math.round((aggregates?.avg_timing_stability || 0) * 100)}%
                </CardTitle>
              )}
              <p className="text-xs text-muted-foreground">Timing Stability</p>
            </CardContent>
          </Card>

          <Card className="bg-card border-border/50">
            <CardHeader className="pb-1 pt-3">
              <div className="flex items-center justify-between">
                <Target className="h-5 w-5 text-primary" />
                {isLoading ? (
                  <Skeleton className="h-4 w-8" />
                ) : (
                  <span className={`text-xs font-medium flex items-center gap-1 ${scaleTrend.isUp ? 'text-green-500' : 'text-red-500'}`}>
                    {scaleTrend.isUp ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                    {scaleTrend.value}%
                  </span>
                )}
              </div>
            </CardHeader>
            <CardContent className="pb-3">
              {isLoading ? (
                <Skeleton className="h-6 w-12" />
              ) : (
                <CardTitle className="text-xl md:text-2xl font-bold">
                  {Math.round((aggregates?.avg_scale_conformity || 0) * 100)}%
                </CardTitle>
              )}
              <p className="text-xs text-muted-foreground">Scale Conformity</p>
            </CardContent>
          </Card>

          <Card className="bg-card border-border/50">
            <CardHeader className="pb-1 pt-3">
              <div className="flex items-center justify-between">
                <Sparkles className="h-5 w-5 text-primary" />
                {isLoading ? (
                  <Skeleton className="h-4 w-8" />
                ) : (
                  <span className="text-xs font-medium flex items-center gap-1 text-primary">
                    Overall
                  </span>
                )}
              </div>
            </CardHeader>
            <CardContent className="pb-3">
              {isLoading ? (
                <Skeleton className="h-6 w-12" />
              ) : (
                <CardTitle className="text-xl md:text-2xl font-bold">
                  {Math.round(((aggregates?.avg_pitch_accuracy || 0) + (aggregates?.avg_scale_conformity || 0) + (aggregates?.avg_timing_stability || 0)) / 3 * 100)}%
                </CardTitle>
              )}
              <p className="text-xs text-muted-foreground">Performance</p>
            </CardContent>
          </Card>

          <Card className="bg-card border-border/50">
            <CardHeader className="pb-1 pt-3">
              <div className="flex items-center justify-between">
                <TrendingUp className="h-5 w-5 text-primary" />
                {isLoading ? (
                  <Skeleton className="h-4 w-8" />
                ) : (
                  <span className="text-xs text-primary font-medium">
                    {formatDuration(aggregates?.total_practice_time || 0)}
                  </span>
                )}
              </div>
            </CardHeader>
            <CardContent className="pb-3">
              {isLoading ? (
                <Skeleton className="h-6 w-12" />
              ) : (
                <CardTitle className="text-xl md:text-2xl font-bold">
                  {aggregates?.total_sessions || 0}
                </CardTitle>
              )}
              <p className="text-xs text-muted-foreground">Total Sessions</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content: Session info on left, AI Coach on right (wider) */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
          {/* Left: Sessions & Details (narrower - 2 cols) */}
          <div className="lg:col-span-2 space-y-4">
            {/* Session List */}
            <Card className="bg-card border-border/50">
              <CardHeader className="pb-2 py-3">
                <CardTitle className="text-sm flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-primary" />
                  Recent Sessions
                </CardTitle>
              </CardHeader>
              <CardContent className="p-2 pt-0">
                <ScrollArea className="h-[180px]">
                  <div className="space-y-1 pr-2">
                    {isLoading ? (
                      Array.from({ length: 3 }).map((_, i) => (
                        <Skeleton key={i} className="h-12 w-full" />
                      ))
                    ) : sessions.length === 0 ? (
                      <div className="text-center py-4 text-muted-foreground">
                        <Music2 className="h-5 w-5 mx-auto mb-1 opacity-50" />
                        <p className="text-xs">No sessions yet</p>
                      </div>
                    ) : (
                      sessions.map((session, index) => (
                        <button
                          key={session.session_id}
                          onClick={() => setSelectedSessionIndex(index)}
                          className={`w-full p-2 rounded-md border text-left transition-all text-xs ${
                            selectedSessionIndex === index
                              ? "border-primary bg-primary/5"
                              : "border-border hover:border-primary/50"
                          }`}
                        >
                          <div className="flex items-center justify-between gap-2">
                            <span className="font-medium text-xs">{formatDate(session.start_timestamp)}</span>
                            <span className="text-[10px] text-muted-foreground">{session.scale_chosen} {session.scale_type}</span>
                            <span className="text-[10px] text-muted-foreground">{formatDuration(session.duration_seconds)}</span>
                            <span className="text-xs text-primary font-medium whitespace-nowrap">
                              {Math.round((((session.pitch_accuracy || 0) + (session.scale_conformity || 0) + (session.timing_stability || 0)) / 3) * 100)}%
                            </span>
                          </div>
                        </button>
                      ))
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Session Details */}
            <Card className="bg-card border-border/50">
              <CardHeader className="pb-2 py-3">
                <CardTitle className="text-sm">Session Details</CardTitle>
                  <CardDescription className="text-xs">
                  {selectedSession ? (
                    <>{formatDate(selectedSession.start_timestamp)} • {selectedSession.scale_chosen} {selectedSession.scale_type}</>
                  ) : "Select a session"}
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0 pb-3">
                {isLoading ? (
                  <Skeleton className="h-32 w-full" />
                ) : !selectedSession ? (
                  <div className="text-center py-6 text-muted-foreground">
                    <BarChart3 className="h-6 w-6 mx-auto mb-2 opacity-50" />
                    <p className="text-xs">Select a session</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {/* Performance Metrics */}
                    <div className="grid grid-cols-4 gap-2">
                      <div className="p-2 rounded-lg bg-card border border-border text-center">
                        <p className="text-lg font-bold text-primary">{Math.round((selectedSession.pitch_accuracy || 0) * 100)}%</p>
                        <p className="text-[10px] text-muted-foreground">Pitch</p>
                      </div>
                      <div className="p-2 rounded-lg bg-card border border-border text-center">
                        <p className="text-lg font-bold text-primary">{Math.round((selectedSession.scale_conformity || 0) * 100)}%</p>
                        <p className="text-[10px] text-muted-foreground">Scale</p>
                      </div>
                      <div className="p-2 rounded-lg bg-card border border-border text-center">
                        <p className="text-lg font-bold text-primary">{Math.round((selectedSession.timing_stability || 0) * 100)}%</p>
                        <p className="text-[10px] text-muted-foreground">Timing</p>
                      </div>
                      <div className="p-2 rounded-lg bg-primary/10 border border-primary text-center">
                        <p className="text-lg font-bold text-primary">{Math.round((((selectedSession.pitch_accuracy || 0) + (selectedSession.scale_conformity || 0) + (selectedSession.timing_stability || 0)) / 3) * 100)}%</p>
                        <p className="text-[10px] text-muted-foreground">Overall</p>
                      </div>
                    </div>
                    {/* Note Counts */}
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div className="p-2 rounded bg-green-500/10 border border-green-500/30">
                        <p className="text-sm font-bold text-green-500">{selectedSession.correct_notes_played}</p>
                        <p className="text-[10px] text-muted-foreground">Correct</p>
                      </div>
                      <div className="p-2 rounded bg-red-500/10 border border-red-500/30">
                        <p className="text-sm font-bold text-red-500">{selectedSession.bad_notes_played}</p>
                        <p className="text-[10px] text-muted-foreground">Wrong</p>
                      </div>
                      <div className="p-2 rounded bg-accent/50">
                        <p className="text-sm font-bold">{selectedSession.total_notes_played}</p>
                        <p className="text-[10px] text-muted-foreground">Total</p>
                      </div>
                    </div>
                    {/* Practice Parameters */}
                    <div>
                      <p className="text-[10px] text-muted-foreground mb-1">Practice Parameters Used</p>
                      <div className="flex gap-2 text-[10px]">
                        <span className="px-2 py-1 rounded bg-muted">
                          Strictness: {Math.round(selectedSession.strictness * 100)}%
                        </span>
                        <span className="px-2 py-1 rounded bg-muted">
                          Sensitivity: {Math.round(selectedSession.sensitivity * 100)}%
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right: AI Coach (wider - 3 cols) */}
          <div className="lg:col-span-3">
            <Card className="bg-card border-border/50">
            <CardHeader className="pb-2 py-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Brain className="h-4 w-4 text-primary" />
                  AI Practice Coach
                </CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsAiCoachExpanded(!isAiCoachExpanded)}
                  className="h-7 w-7 p-0"
                >
                  {isAiCoachExpanded ? (
                    <Minimize2 className="h-4 w-4" />
                  ) : (
                    <Maximize2 className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className={`flex flex-col ${isAiCoachExpanded ? 'h-[600px]' : 'h-[420px]'}`}>
                {/* Messages */}
                <ScrollArea className="flex-1 pr-4 mb-4">
                  <div className="space-y-4">
                    {messages.map((message) => (
                      <div key={message.id}>
                        <div
                          className={`flex gap-3 ${
                            message.role === "user" ? "justify-end" : "justify-start"
                          }`}
                        >
                          {message.role === "assistant" && (
                            <Avatar className="h-8 w-8 border-2 border-primary/20">
                              <AvatarFallback className="bg-primary/10 text-primary">
                                <Sparkles className="h-4 w-4" />
                              </AvatarFallback>
                            </Avatar>
                          )}
                          <div
                            className={`rounded-lg px-4 py-2 max-w-[80%] ${
                              message.role === "user"
                                ? "bg-primary text-primary-foreground"
                                : "bg-muted"
                            }`}
                          >
                            <div className="text-sm prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-ul:my-1 prose-li:my-0 prose-table:my-2 prose-th:border prose-th:p-2 prose-td:border prose-td:p-2">
                              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                            </div>
                          </div>
                          {message.role === "user" && (
                            <Avatar className="h-8 w-8 border-2 border-primary/20">
                              <AvatarFallback className="bg-primary/10 text-primary">
                                <Guitar className="h-4 w-4" />
                              </AvatarFallback>
                            </Avatar>
                          )}
                        </div>
                        {/* Render chart if present */}
                        {message.chartData && (
                          <div className="ml-11 mr-11">
                            <PerformanceChart
                              chartData={message.chartData}
                              onSavePlan={handleSavePlan}
                            />
                          </div>
                        )}
                      </div>
                    ))}
                    {isAiTyping && (
                      <div className="flex gap-3 justify-start">
                        <Avatar className="h-8 w-8 border-2 border-primary/20">
                          <AvatarFallback className="bg-primary/10 text-primary">
                            <Sparkles className="h-4 w-4" />
                          </AvatarFallback>
                        </Avatar>
                        <div className="rounded-lg px-4 py-2 bg-muted">
                          <div className="flex items-center gap-2">
                            <div className="flex gap-1">
                              <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                              <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                              <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
                            </div>
                            <span className="text-xs text-muted-foreground">
                              {currentModel ? `Using ${currentModel}` : 'Thinking...'}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                </ScrollArea>

                {/* Input */}
                <div className="flex gap-2">
                  <Input
                    placeholder="Ask me anything about your practice..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    disabled={isAiTyping}
                    className="flex-1"
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || isAiTyping}
                    className="gap-2"
                  >
                    <Send className="h-4 w-4" />
                    Send
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
          </div>
        </div>

        {/* Expanded AI Coach Overlay */}
        {isAiCoachExpanded && (
          <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
            <Card className="w-full max-w-6xl h-[90vh] bg-card border-border/50">
              <CardHeader className="pb-2 py-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Brain className="h-5 w-5 text-primary" />
                    AI Practice Coach
                  </CardTitle>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsAiCoachExpanded(false)}
                    className="h-8 w-8 p-0"
                  >
                    <Minimize2 className="h-5 w-5" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="pt-0 h-[calc(90vh-5rem)]">
                <div className="flex flex-col h-full">
                  {/* Messages */}
                  <ScrollArea className="flex-1 pr-4 mb-4">
                    <div className="space-y-4">
                      {messages.map((message) => (
                        <div key={message.id}>
                          <div
                            className={`flex gap-3 ${
                              message.role === "user" ? "justify-end" : "justify-start"
                            }`}
                          >
                            {message.role === "assistant" && (
                              <Avatar className="h-8 w-8 border-2 border-primary/20">
                                <AvatarFallback className="bg-primary/10 text-primary">
                                  <Sparkles className="h-4 w-4" />
                                </AvatarFallback>
                              </Avatar>
                            )}
                            <div
                              className={`rounded-lg px-4 py-2 max-w-[80%] ${
                                message.role === "user"
                                  ? "bg-primary text-primary-foreground"
                                  : "bg-muted"
                              }`}
                            >
                              <ReactMarkdown
                                className="text-sm prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-ul:my-1 prose-li:my-0 prose-table:my-2 prose-th:border prose-th:p-2 prose-td:border prose-td:p-2"
                                remarkPlugins={[remarkGfm]}
                              >
                                {message.content}
                              </ReactMarkdown>
                              {message.chartData && (
                                <div className="mt-4">
                                  <PerformanceChart
                                    chartData={message.chartData}
                                    onSavePlan={handleSavePlan}
                                  />
                                </div>
                              )}
                            </div>
                            {message.role === "user" && (
                              <Avatar className="h-8 w-8 border-2 border-primary/20">
                                <AvatarFallback className="bg-primary/10 text-primary">
                                  <Guitar className="h-4 w-4" />
                                </AvatarFallback>
                              </Avatar>
                            )}
                          </div>
                        </div>
                      ))}
                      {isAiTyping && (
                        <div className="flex gap-3 justify-start">
                          <Avatar className="h-8 w-8 border-2 border-primary/20">
                            <AvatarFallback className="bg-primary/10 text-primary">
                              <Sparkles className="h-4 w-4" />
                            </AvatarFallback>
                          </Avatar>
                          <div className="bg-muted rounded-lg px-4 py-2">
                            <div className="flex items-center gap-2">
                              <div className="flex gap-1">
                                <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
                              </div>
                              <span className="text-xs text-muted-foreground">
                                {currentModel ? `Using ${currentModel}` : 'Thinking...'}
                              </span>
                            </div>
                          </div>
                        </div>
                      )}
                      <div ref={messagesEndRef} />
                    </div>
                  </ScrollArea>

                  {/* Input */}
                  <div className="flex gap-2">
                    <Input
                      placeholder="Ask me anything about your practice..."
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault();
                          handleSendMessage();
                        }
                      }}
                      disabled={isAiTyping}
                      className="flex-1"
                    />
                    <Button
                      onClick={handleSendMessage}
                      disabled={!inputMessage.trim() || isAiTyping}
                      className="gap-2"
                    >
                      <Send className="h-4 w-4" />
                      Send
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
