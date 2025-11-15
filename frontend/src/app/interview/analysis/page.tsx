"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ArrowLeft, BookOpenCheck, Loader2, MessageSquare, Sparkles } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";

type KeyEvent = {
  timestamp?: string;
  speaker: string;
  message: string;
};

type CoachingFeedback = {
  strengths: string[];
  areas_for_improvement: string[];
  next_practice_focus: string[];
};

type Analysis = {
  case_summary: {
    case_type: string;
    overall_summary: string;
    user_confidence: string;
  };
  key_events: KeyEvent[];
  coaching_feedback: CoachingFeedback;
  action_items: string[];
  sentiment: {
    user: string;
    assistant: string;
  };
  engagement_summary?: {
    summary?: string;
  };
  source_transcript?: string;
};

type BackendAnalysisResponse = {
  conversation_id: string;
  status: "pending" | "ready";
  updated_at: string;
  analysis: (Analysis & { source_transcript?: string }) | null;
};

type AnalysisStatus = {
  conversationId: string;
  status: "pending" | "ready";
  updatedAt: string;
  analysis: Analysis | null;
};

function confidenceScore(confidence: string) {
  const value = confidence.toLowerCase();
  if (value.includes("low")) return 35;
  if (value.includes("high")) return 85;
  return 60;
}

function normalizeResponse(data: BackendAnalysisResponse): AnalysisStatus {
  return {
    conversationId: data.conversation_id,
    status: data.status,
    updatedAt: data.updated_at,
    analysis: data.analysis ?? null,
  };
}

export default function InterviewAnalysisPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center gap-4 text-gray-700">
          <Loader2 className="size-10 animate-spin text-indigo-600" />
          <p>Loading interview analysis…</p>
        </div>
      }
    >
      <AnalysisContent />
    </Suspense>
  );
}

function AnalysisContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const conversationId = searchParams.get("conversationId");

  const [status, setStatus] = useState<AnalysisStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setStatus(null);
    setError(null);
    if (!conversationId) {
      setIsLoading(false);
      return;
    }

    let isCancelled = false;
    let timeout: ReturnType<typeof setTimeout> | null = null;

    const fetchAnalysis = async (withSpinner = false) => {
      if (withSpinner) {
        setIsLoading(true);
      }
      try {
        const response = await fetch(`/api/interview-analysis/${conversationId}`);
        const payload = (await response.json().catch(() => null)) as BackendAnalysisResponse | null;
        if (!response.ok || !payload) {
          const message =
            (payload as unknown as { detail?: string; message?: string })?.detail ??
            (payload as unknown as { message?: string })?.message ??
            "Unable to load analysis.";
          throw new Error(message);
        }

        if (isCancelled) {
          return;
        }

        const normalized = normalizeResponse(payload);
        setStatus(normalized);
        setError(null);

        if (timeout) {
          clearTimeout(timeout);
          timeout = null;
        }

        if (normalized.status === "pending") {
          timeout = setTimeout(() => fetchAnalysis(false), 5000);
        }
      } catch (err) {
        if (!isCancelled) {
          setError(err instanceof Error ? err.message : "Unable to reach analysis service.");
        }
      } finally {
        if (!isCancelled && withSpinner) {
          setIsLoading(false);
        }
      }
    };

    fetchAnalysis(true);

    return () => {
      isCancelled = true;
      if (timeout) {
        clearTimeout(timeout);
      }
    };
  }, [conversationId]);

  const readyAnalysis = status?.status === "ready" ? status.analysis : null;
  const score = useMemo(
    () => (readyAnalysis ? confidenceScore(readyAnalysis.case_summary.user_confidence) : 0),
    [readyAnalysis],
  );

  const showLoader = isLoading && !status;

  const renderContent = () => {
    if (!conversationId) {
      return (
        <Card>
          <CardHeader>
            <CardTitle>No conversation selected</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600">
              Pass a <code className="rounded bg-gray-100 px-1.5 py-0.5 text-sm">conversationId</code> query
              parameter (e.g., <code>/interview/analysis?conversationId=conversation-1234</code>) after a session
              ends to view its analysis report.
            </p>
          </CardContent>
        </Card>
      );
    }

    if (showLoader) {
      return (
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12">
            <Loader2 className="size-10 animate-spin text-indigo-600" />
            <p className="text-gray-700">Fetching interview analysis…</p>
          </CardContent>
        </Card>
      );
    }

    if (error) {
      return (
        <Card>
          <CardHeader>
            <CardTitle>Unable to load analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-red-600">{error}</p>
          </CardContent>
        </Card>
      );
    }

    if (!status) {
      return null;
    }

    if (status.status === "pending") {
      return (
        <Card>
          <CardHeader>
            <CardTitle>Analysis is still running</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-gray-700">
              We&apos;re summarizing your transcript now. This page will refresh automatically once the report is ready.
            </p>
            <p className="text-sm text-gray-500">
              Conversation ID: <span className="font-mono">{status.conversationId}</span>
            </p>
            <p className="text-sm text-gray-500">
              Last update: {new Date(status.updatedAt).toLocaleString()}
            </p>
          </CardContent>
        </Card>
      );
    }

    if (!readyAnalysis) {
      return (
        <Card>
          <CardHeader>
            <CardTitle>No analysis data available</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600">
              The backend returned a completed status without any payload. Please try again or run a new interview.
            </p>
          </CardContent>
        </Card>
      );
    }

    const keyEvents = readyAnalysis.key_events ?? [];
    const strengths = readyAnalysis.coaching_feedback?.strengths ?? [];
    const improvements = readyAnalysis.coaching_feedback?.areas_for_improvement ?? [];
    const nextFocus = readyAnalysis.coaching_feedback?.next_practice_focus ?? [];
    const actionItems = readyAnalysis.action_items ?? [];

    return (
      <>
        {/* Top summary */}
        <Card className="mb-8">
          <CardContent className="p-8">
            <div className="flex gap-8 flex-col lg:flex-row">
              <div className="flex-1">
                <div className="flex items-start gap-4 mb-6">
                  <div className="flex size-12 items-center justify-center rounded-xl bg-indigo-100">
                    <Sparkles className="size-6 text-indigo-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium uppercase tracking-wide text-gray-500 mb-2">
                      {readyAnalysis.case_summary.case_type}
                    </p>
                    <h1 className="text-3xl font-bold text-gray-900">Case Opening Analysis</h1>
                  </div>
                </div>
                <p className="text-base text-gray-700 leading-relaxed">
                  {readyAnalysis.case_summary.overall_summary}
                </p>
              </div>

              <div className="border-l-2 border-gray-200 self-stretch hidden lg:block" />

              <div className="flex flex-col items-center justify-center gap-3 min-w-[160px]">
                <div className="flex items-center justify-center">
                  {(() => {
                    const radius = 36;
                    const circumference = 2 * Math.PI * radius;
                    const offset = circumference * (1 - score / 100);
                    return (
                      <svg width={104} height={104} className="block">
                        <circle
                          cx={52}
                          cy={52}
                          r={radius}
                          stroke="#e5e7eb"
                          strokeWidth={9}
                          fill="none"
                        />
                        <circle
                          cx={52}
                          cy={52}
                          r={radius}
                          stroke="#16a34a"
                          strokeWidth={9}
                          fill="none"
                          strokeLinecap="round"
                          strokeDasharray={circumference}
                          strokeDashoffset={offset}
                          transform="rotate(-90 52 52)"
                        />
                        <text
                          x="50%"
                          y="50%"
                          dominantBaseline="middle"
                          textAnchor="middle"
                          className="text-2xl font-bold fill-slate-900"
                        >
                          {score}
                        </text>
                      </svg>
                    );
                  })()}
                </div>
                <div className="text-center">
                  <p className="text-base font-semibold text-gray-900 capitalize">
                    {readyAnalysis.case_summary.user_confidence} confidence
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main grid */}
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Left: Feedback + conversation */}
          <div className="space-y-8 lg:col-span-2">
            {/* Coach feedback */}
            <Card>
              <CardContent className="p-8">
                <div className="flex items-center gap-4 mb-8">
                  <div className="flex size-12 items-center justify-center rounded-xl bg-indigo-100">
                    <BookOpenCheck className="size-6 text-indigo-600" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900">Coaching Feedback</h2>
                </div>

                <div className="grid gap-8 md:grid-cols-3">
                  <div>
                    <p className="mb-4 text-sm font-semibold uppercase tracking-wide text-emerald-700">
                      Strengths
                    </p>
                    <ul className="space-y-2.5 text-sm text-gray-700 leading-relaxed">
                      {strengths.length ? (
                        strengths.map((item, idx) => (
                          <li key={idx} className="flex gap-2">
                            <span className="text-emerald-600">•</span>
                            <span>{item}</span>
                          </li>
                        ))
                      ) : (
                        <li className="text-gray-500">No strengths captured.</li>
                      )}
                    </ul>
                  </div>
                  <div>
                    <p className="mb-4 text-sm font-semibold uppercase tracking-wide text-amber-700">
                      Improve next
                    </p>
                    <ul className="space-y-2.5 text-sm text-gray-700 leading-relaxed">
                      {improvements.length ? (
                        improvements.map((item, idx) => (
                          <li key={idx} className="flex gap-2">
                            <span className="text-amber-600">•</span>
                            <span>{item}</span>
                          </li>
                        ))
                      ) : (
                        <li className="text-gray-500">Nothing flagged here.</li>
                      )}
                    </ul>
                  </div>
                  <div>
                    <p className="mb-4 text-sm font-semibold uppercase tracking-wide text-sky-700">
                      Next practice focus
                    </p>
                    <ul className="space-y-2.5 text-sm text-gray-700 leading-relaxed">
                      {nextFocus.length ? (
                        nextFocus.map((item, idx) => (
                          <li key={idx} className="flex gap-2">
                            <span className="text-sky-600">•</span>
                            <span>{item}</span>
                          </li>
                        ))
                      ) : (
                        <li className="text-gray-500">No follow-up focus provided.</li>
                      )}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Conversation snippets */}
            <Card className="bg-indigo-50/30">
              <CardContent className="p-8">
                <div className="flex items-center gap-4 mb-8">
                  <div className="flex size-12 items-center justify-center rounded-xl bg-indigo-100">
                    <MessageSquare className="size-6 text-indigo-600" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900">Conversation Highlights</h2>
                </div>

                {keyEvents.length ? (
                  <div className="space-y-6">
                    {keyEvents.map((event, idx) => (
                      <div key={`${event.timestamp ?? idx}-${idx}`}>
                        <div className="text-sm font-medium text-indigo-700 mb-2 capitalize">
                          {event.speaker?.toLowerCase() === "assistant" ? "Coach" : "You"}
                        </div>
                        <blockquote className="text-gray-700 italic leading-relaxed border-l-4 border-indigo-300 pl-6 py-2">
                          {event.message}
                        </blockquote>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-600">No highlights available for this conversation.</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right: sidebar */}
          <div className="space-y-8">
            {/* Action items */}
            <Card className="bg-emerald-50/40">
              <CardContent className="p-8">
                <div className="flex items-center gap-4 mb-8">
                  <div className="flex size-12 items-center justify-center rounded-xl bg-emerald-500/20">
                    <BookOpenCheck className="size-6 text-emerald-700" />
                  </div>
                  <div>
                    <p className="text-sm font-medium uppercase tracking-wide text-emerald-700 mb-1">
                      Next steps
                    </p>
                    <h2 className="text-2xl font-bold text-gray-900">Action Items</h2>
                  </div>
                </div>

                <div className="space-y-4">
                  {actionItems.length ? (
                    actionItems.map((item, idx) => (
                      <div key={idx} className="flex gap-4">
                        <span className="mt-0.5 inline-flex size-6 items-center justify-center rounded-full bg-emerald-100 text-sm font-bold text-emerald-800 shrink-0">
                          {idx + 1}
                        </span>
                        <p className="text-base leading-relaxed text-gray-700">{item}</p>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-600">No action items recorded.</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Sentiment Overview */}
            <Card>
              <CardContent className="p-8 space-y-6">
                <h2 className="text-xl font-bold text-gray-900">Sentiment Overview</h2>
                <div className="space-y-6">
                  <div className="pb-6 border-b border-gray-200">
                    <div className="text-sm text-gray-600 mb-2">Your sentiment</div>
                    <div className="text-base font-semibold text-gray-900 capitalize">
                      {readyAnalysis.sentiment.user}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 mb-2">Coach sentiment</div>
                    <div className="text-base font-semibold text-gray-900 capitalize">
                      {readyAnalysis.sentiment.assistant}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {readyAnalysis.engagement_summary?.summary ? (
              <Card>
                <CardHeader>
                  <CardTitle>Engagement Notes</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700">{readyAnalysis.engagement_summary.summary}</p>
                </CardContent>
              </Card>
            ) : null}

            {readyAnalysis.source_transcript ? (
              <Card>
                <CardHeader>
                  <CardTitle>Transcript</CardTitle>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="outline"
                    onClick={() => window.open(readyAnalysis.source_transcript, "_blank")}
                    className="w-full"
                  >
                    View raw transcript
                  </Button>
                </CardContent>
              </Card>
            ) : null}
          </div>
        </div>
      </>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto max-w-6xl px-4 py-8">
        <Button
          onClick={() => router.push("/")}
          variant="outline"
          className="mb-8"
        >
          <ArrowLeft className="mr-2 size-4" />
          Back to Companies
        </Button>
        {renderContent()}
      </div>
    </div>
  );
}
