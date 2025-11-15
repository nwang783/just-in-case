"use client";

import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, FileText, Target, Lightbulb, MessageSquare, Play, CheckCircle2 } from "lucide-react";
import { Button } from "../../../components/ui/button";
import { Badge } from "../../../components/ui/badge";
import { Card, CardContent } from "../../../components/ui/card";
import companyData from "../../../../../company-data.json";
import { useCallback, useEffect, useMemo, useState } from "react";
import Image from "next/image";

type InterviewType = {
  type: string;
  format: string;
  keyFocus: string;
  tip: string;
  description?: string;
  evaluation?: string;
  examplePrompts?: string;
};

type Company = {
  name: string;
  logo: string;
  color: string;
  logoBg?: string;
  difficulty: "Advanced" | "Intermediate";
  interviews: InterviewType[];
};

type CompanyDataMap = {
  [key: string]: Company;
};

const data = companyData as CompanyDataMap;

type InterviewSession = {
  sessionId: string;
  companySlug: string;
  interviewType: string;
  roomUrl: string;
  roomName?: string;
  expiresAt?: number | null;
  status: string;
  lastError?: string | null;
  createdAt?: string;
  updatedAt?: string;
  conversationId?: string | null;
  transcriptPath?: string | null;
  analysisPath?: string | null;
};

const SESSION_STATUS_LABELS: Record<string, string> = {
  room_created: "Room ready — join the link below when you're set.",
  bot_starting: "Summoning the AI interviewer...",
  bot_running: "AI interviewer is live in the room.",
  bot_stopping: "Wrapping up the session...",
  bot_completed: "Session completed.",
  bot_error: "Something went wrong starting the AI. Try again.",
};

const STATUS_STYLES: Record<string, string> = {
  room_created: "bg-indigo-100 text-indigo-700",
  bot_starting: "bg-amber-100 text-amber-700",
  bot_running: "bg-emerald-100 text-emerald-700",
  bot_stopping: "bg-amber-100 text-amber-700",
  bot_completed: "bg-gray-200 text-gray-700",
  bot_error: "bg-red-100 text-red-700",
};

async function parseJsonSafe<T>(response: Response): Promise<T | null> {
  try {
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export default function CompanyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params?.slug as string;
  const company = data[slug];
  const [selectedInterview, setSelectedInterview] = useState(0);
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [isCreatingSession, setIsCreatingSession] = useState(false);
  const [isStartingBot, setIsStartingBot] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const selectedInterviewData = company?.interviews[selectedInterview];

  useEffect(() => {
    // Reset flow when the user switches companies or interview types
    setSession(null);
    setErrorMessage(null);
    setIsCreatingSession(false);
    setIsStartingBot(false);
  }, [slug, selectedInterview]);

  const fetchSessionStatus = useCallback(async () => {
    if (!session?.sessionId) return;
    try {
      const response = await fetch(`/api/interview-sessions/${session.sessionId}/status`, {
        cache: "no-store",
      });
      if (!response.ok) return;
      const data = await parseJsonSafe<InterviewSession>(response);
      if (!data) return;
      setSession((prev) => (prev ? { ...prev, ...data } : data));
    } catch (err) {
      console.error("Failed to refresh session status", err);
    }
  }, [session?.sessionId]);

  useEffect(() => {
    if (!session?.sessionId) return;
    const pollableStatuses = ["bot_starting", "bot_running", "bot_stopping"];
    if (!pollableStatuses.includes(session.status)) return;

    const poll = () => {
      void fetchSessionStatus();
    };

    poll();
    const intervalId = setInterval(poll, 4000);
    return () => clearInterval(intervalId);
  }, [session?.sessionId, session?.status, fetchSessionStatus]);

  const handleCreateSession = useCallback(async () => {
    if (!company || !selectedInterviewData) return;
    setIsCreatingSession(true);
    setErrorMessage(null);
    try {
      const response = await fetch("/api/interview-sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          companySlug: slug,
          interviewType: selectedInterviewData.type,
        }),
      });
      const data = await parseJsonSafe<InterviewSession>(response);
      if (!response.ok) {
        throw new Error(
          (data as unknown as { detail?: string; message?: string })?.detail ??
            (data as unknown as { message?: string })?.message ??
            "Unable to start interview.",
        );
      }
      if (!data) {
        throw new Error("Unexpected response from server while starting the interview.");
      }
      setSession(data);
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Unable to start interview.");
    } finally {
      setIsCreatingSession(false);
    }
  }, [company, selectedInterviewData, slug]);

  const handleStartBot = useCallback(async () => {
    if (!session) return;
    setIsStartingBot(true);
    setErrorMessage(null);
    try {
      const response = await fetch(`/api/interview-sessions/${session.sessionId}/start`, {
        method: "POST",
      });
      const data = await parseJsonSafe<InterviewSession>(response);
      if (!response.ok) {
        throw new Error(
          (data as unknown as { detail?: string; message?: string })?.detail ??
            (data as unknown as { message?: string })?.message ??
            "Unable to bring the AI into the room.",
        );
      }
      if (!data) {
        throw new Error("Unexpected response from server while starting the AI.");
      }
      setSession((prev) => (prev ? { ...prev, ...data } : data));
    } catch (err) {
      setErrorMessage(
        err instanceof Error ? err.message : "Unable to bring the AI into the room. Try again.",
      );
    } finally {
      setIsStartingBot(false);
    }
  }, [session]);

  const statusDescription = session ? SESSION_STATUS_LABELS[session.status] ?? "Updating session..." : null;
  const statusBadgeStyle = session ? STATUS_STYLES[session.status] ?? "bg-gray-200 text-gray-700" : "";
  const expiresAtText = useMemo(() => {
    if (!session?.expiresAt) return null;
    return new Date(session.expiresAt * 1000).toLocaleString();
  }, [session?.expiresAt]);
  const canStartBot = session?.status === "room_created";
  const canViewAnalysis = Boolean(session?.conversationId);
  const analysisHref = session?.conversationId
    ? `/interview/analysis?conversationId=${encodeURIComponent(session.conversationId)}`
    : null;

  if (!company) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl mb-4">Company not found</h1>
          <Button onClick={() => router.push("/")} variant="outline" className="rounded-full">
            <ArrowLeft className="mr-2 size-4" />
            Back to Home
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Section */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-8">
          <Button
            onClick={() => router.push("/")}
            variant="outline"
            className="mb-8"
          >
            <ArrowLeft className="mr-2 size-4" />
            Back to Companies
          </Button>

          <div className="max-w-6xl mx-auto">
            <div className="flex items-center gap-6 mb-6">
              <div
                className="border border-gray-200 size-28 rounded-lg flex items-center justify-center shrink-0 p-3"
                style={{ backgroundColor: company.logoBg || '#fff' }}
              >
                <Image
                  src={company.logo}
                  alt={`${company.name} logo`}
                  width={112}
                  height={112}
                  className="object-contain"
                />
              </div>
              <div>
                <h1 className="text-5xl font-bold mb-3 text-gray-900">{company.name}</h1>
                <div className="flex items-center gap-3">
                  <Badge variant={company.difficulty === "Advanced" ? "default" : "secondary"}>
                    {company.difficulty}
                  </Badge>
                  <span className="text-gray-600">
                    {company.interviews.length} Interview Type{company.interviews.length > 1 ? 's' : ''}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content Section */}
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto">
          {/* Interview Type Tabs */}
          <div className="border-b border-gray-200 mb-12">
            <div className="flex gap-1 overflow-x-auto">
              {company.interviews.map((interview, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedInterview(idx)}
                  className={`px-6 py-3 whitespace-nowrap font-medium transition-all border-b-2 ${
                    selectedInterview === idx
                      ? 'border-indigo-600 text-indigo-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                  }`}
                >
                  {interview.type}
                </button>
              ))}
            </div>
          </div>

          {/* Interview Details */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Content - 2 columns */}
            <div className="lg:col-span-2 space-y-8">
              {/* Overview Card */}
              <Card>
                <CardContent className="p-8">
                  <div className="flex items-start gap-4 mb-6">
                    <div className="bg-indigo-100 size-12 rounded-lg flex items-center justify-center shrink-0">
                      <FileText className="size-6 text-indigo-600" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 mb-2">{company.interviews[selectedInterview].type}</h2>
                      <Badge variant="secondary">
                        {company.interviews[selectedInterview].format}
                      </Badge>
                    </div>
                  </div>

                  {company.interviews[selectedInterview].description && (
                    <p className="text-gray-700 leading-relaxed mb-8">
                      {company.interviews[selectedInterview].description}
                    </p>
                  )}

                  <Button
                    onClick={handleCreateSession}
                    disabled={isCreatingSession}
                    className="w-full bg-indigo-100 text-indigo-600 rounded-full px-8 py-6 text-sm font-semibold hover:bg-indigo-200 transition-colors flex items-center justify-center disabled:opacity-70"
                  >
                    {isCreatingSession ? "Preparing your room..." : "Start Interview"}
                    <Play className="ml-2 size-4" />
                  </Button>

                  {errorMessage && (
                    <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                      {errorMessage}
                    </div>
                  )}

                  {session && (
                    <div className="mt-6 space-y-4 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
                      <div>
                        <p className="text-sm font-semibold text-gray-900">Your private Daily room</p>
                        <p className="mt-1 break-all text-sm text-gray-600">{session.roomUrl}</p>
                        <div className="mt-4 flex flex-wrap gap-3">
                          <Button variant="outline" asChild className="rounded-full">
                            <a href={session.roomUrl} target="_blank" rel="noreferrer">
                              Open Daily Room
                            </a>
                          </Button>
                          <Button
                            onClick={handleStartBot}
                            disabled={!canStartBot || isStartingBot}
                            className="rounded-full"
                          >
                            {isStartingBot ? "Waiting for the AI..." : "I'm in the room – bring the AI"}
                          </Button>
                        </div>
                      </div>

                      <div className="flex items-start gap-3 rounded-2xl bg-gray-50 p-4">
                        <div className={`rounded-full p-2 ${statusBadgeStyle}`}>
                          <CheckCircle2 className="size-5" />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-gray-900">Status</p>
                          <p className="text-sm text-gray-600">{statusDescription}</p>
                        </div>
                      </div>

                      {session.lastError && (
                        <p className="text-sm text-red-600">Last error: {session.lastError}</p>
                      )}

                      {expiresAtText && (
                        <p className="text-xs text-gray-500">Room expires at {expiresAtText}</p>
                      )}

                      {canViewAnalysis && (
                        <div className="rounded-2xl border border-indigo-100 bg-indigo-50 p-4 space-y-3">
                          <div>
                            <p className="text-sm font-semibold text-gray-900">Session analysis ready</p>
                            <p className="text-sm text-gray-600">
                              Review coaching insights from this run. We&apos;ll auto-refresh that page until the
                              report finishes rendering.
                            </p>
                          </div>
                          <div className="flex flex-wrap gap-3">
                            <Button
                              className="rounded-full"
                              onClick={() => analysisHref && router.push(analysisHref)}
                            >
                              View Interview Analysis
                            </Button>
                            <p className="text-xs text-gray-500">
                              Conversation ID: <span className="font-mono">{session.conversationId}</span>
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Example Prompts */}
              {company.interviews[selectedInterview].examplePrompts && (
                <Card className="bg-indigo-50/30">
                  <CardContent className="p-8">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="bg-indigo-100 size-10 rounded-lg flex items-center justify-center">
                        <MessageSquare className="size-5 text-indigo-600" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900">Example Interview Prompts</h3>
                    </div>
                    <blockquote className="text-gray-700 italic border-l-4 border-indigo-300 pl-6 py-2">
                      {company.interviews[selectedInterview].examplePrompts}
                    </blockquote>
                  </CardContent>
                </Card>
              )}

              {/* What They Evaluate */}
              {company.interviews[selectedInterview].evaluation && (
                <Card className="bg-blue-50/30">
                  <CardContent className="p-8">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="bg-blue-100 size-10 rounded-lg flex items-center justify-center">
                        <Target className="size-5 text-blue-600" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900">What Interviewers Evaluate</h3>
                    </div>
                    <p className="text-gray-700 leading-relaxed">
                      {company.interviews[selectedInterview].evaluation}
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Sidebar - 1 column */}
            <div className="space-y-8">
              {/* Practical Tip */}
              {company.interviews[selectedInterview].tip && (
                <Card className="bg-amber-50/40">
                  <CardContent className="p-8">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="bg-amber-500/20 size-10 rounded-lg flex items-center justify-center">
                        <Lightbulb className="size-5 text-amber-700" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900">Pro Tip</h3>
                    </div>
                    <p className="text-gray-700 leading-relaxed">
                      {company.interviews[selectedInterview].tip}
                    </p>
                  </CardContent>
                </Card>
              )}

              {/* Quick Stats */}
              <Card>
                <CardContent className="p-8">
                  <h3 className="font-semibold mb-6 text-gray-900">Interview Overview</h3>
                  <div className="space-y-4">
                    <div className="py-3 border-b border-gray-100">
                      <div className="text-sm text-gray-600 mb-2">Format</div>
                      <div className="text-sm font-medium text-gray-900">
                        {company.interviews[selectedInterview].format}
                      </div>
                    </div>
                    <div className="flex justify-between items-center py-3 border-b border-gray-100">
                      <span className="text-sm text-gray-600">Difficulty</span>
                      <Badge variant={company.difficulty === "Advanced" ? "default" : "secondary"}>
                        {company.difficulty}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center py-3">
                      <span className="text-sm text-gray-600">Total Types</span>
                      <span className="text-sm font-medium text-gray-900">
                        {company.interviews.length}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
