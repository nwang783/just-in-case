"use client";

import Link from "next/link";
import { ArrowLeft, BookOpenCheck, MessageSquare, Sparkles } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import mockAnalysis from "../../../../mock-analysis.json";

type KeyEvent = {
  timestamp: string;
  speaker: "assistant" | "user";
  message: string;
};

type Analysis = {
  case_summary: {
    case_type: string;
    overall_summary: string;
    user_confidence: string;
  };
  key_events: KeyEvent[];
  coaching_feedback: {
    strengths: string[];
    areas_for_improvement: string[];
    next_practice_focus: string[];
  };
  action_items: string[];
  sentiment: {
    user: string;
    assistant: string;
  };
};

const analysis = mockAnalysis as Analysis;

function confidenceScore(confidence: string) {
  const value = confidence.toLowerCase();
  if (value.includes("low")) return 35;
  if (value.includes("high")) return 85;
  return 60;
}

const score = confidenceScore(analysis.case_summary.user_confidence);

export default function InterviewAnalysisPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white">
        <div className="container mx-auto max-w-6xl px-4 py-6 flex items-center justify-between">
          <Link
            href="/"
            className="inline-flex items-center text-sm font-medium text-gray-700 hover:text-indigo-700"
          >
            <ArrowLeft className="mr-2 size-4" />
            Back to companies
          </Link>
          <Badge variant="secondary" className="capitalize">
            {analysis.case_summary.case_type}
          </Badge>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto max-w-6xl px-4 py-12">
        {/* Top summary */}
        <Card className="mb-8">
          <CardContent className="p-8">
            <div className="flex gap-8">
              <div className="flex-1">
                <div className="flex items-start gap-4 mb-6">
                  <div className="flex size-12 items-center justify-center rounded-xl bg-indigo-100">
                    <Sparkles className="size-6 text-indigo-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium uppercase tracking-wide text-gray-500 mb-2">
                      {analysis.case_summary.case_type}
                    </p>
                    <h1 className="text-3xl font-bold text-gray-900">
                      Case Opening Analysis
                    </h1>
                  </div>
                </div>
                <p className="text-base text-gray-700 leading-relaxed">
                  {analysis.case_summary.overall_summary}
                </p>
              </div>

              <div className="border-l-2 border-gray-400 self-stretch"></div>

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
                    {analysis.case_summary.user_confidence} confidence
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
                  <h2 className="text-2xl font-bold text-gray-900">
                    Coaching Feedback
                  </h2>
                </div>

                <div className="grid gap-8 md:grid-cols-3">
                  <div>
                    <p className="mb-4 text-sm font-semibold uppercase tracking-wide text-emerald-700">
                      Strengths
                    </p>
                    <ul className="space-y-2.5 text-sm text-gray-700 leading-relaxed">
                      {analysis.coaching_feedback.strengths.map((item, idx) => (
                        <li key={idx} className="flex gap-2">
                          <span className="text-emerald-600">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <p className="mb-4 text-sm font-semibold uppercase tracking-wide text-amber-700">
                      Improve next
                    </p>
                    <ul className="space-y-2.5 text-sm text-gray-700 leading-relaxed">
                      {analysis.coaching_feedback.areas_for_improvement.map((item, idx) => (
                        <li key={idx} className="flex gap-2">
                          <span className="text-amber-600">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <p className="mb-4 text-sm font-semibold uppercase tracking-wide text-sky-700">
                      Next practice focus
                    </p>
                    <ul className="space-y-2.5 text-sm text-gray-700 leading-relaxed">
                      {analysis.coaching_feedback.next_practice_focus.map((item, idx) => (
                        <li key={idx} className="flex gap-2">
                          <span className="text-sky-600">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
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
                  <h2 className="text-2xl font-bold text-gray-900">
                    Conversation Highlights
                  </h2>
                </div>

                <div className="space-y-6">
                  {analysis.key_events.map((event, idx) => (
                    <div key={idx}>
                      <div className="text-sm font-medium text-indigo-700 mb-2 capitalize">
                        {event.speaker === "assistant" ? "Coach" : "You"}
                      </div>
                      <blockquote className="text-gray-700 italic leading-relaxed border-l-4 border-indigo-300 pl-6 py-2">
                        {event.message}
                      </blockquote>
                    </div>
                  ))}
                </div>
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
                    <h2 className="text-2xl font-bold text-gray-900">
                      Action Items
                    </h2>
                  </div>
                </div>

                <div className="space-y-4">
                  {analysis.action_items.map((item, idx) => (
                    <div key={idx} className="flex gap-4">
                      <span className="mt-0.5 inline-flex size-6 items-center justify-center rounded-full bg-emerald-100 text-sm font-bold text-emerald-800 shrink-0">
                        {idx + 1}
                      </span>
                      <p className="text-base leading-relaxed text-gray-700">
                        {item}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Sentiment Overview */}
            <Card>
              <CardContent className="p-8">
                <h2 className="text-xl font-bold mb-6 text-gray-900">Sentiment Overview</h2>
                <div className="space-y-6">
                  <div className="pb-6 border-b border-gray-200">
                    <div className="text-sm text-gray-600 mb-2">Your sentiment</div>
                    <div className="text-base font-semibold text-gray-900 capitalize">
                      {analysis.sentiment.user}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 mb-2">Coach sentiment</div>
                    <div className="text-base font-semibold text-gray-900 capitalize">
                      {analysis.sentiment.assistant}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
