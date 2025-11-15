"use client";

import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, FileText, Target, Lightbulb, MessageSquare, Play, CheckCircle2 } from "lucide-react";
import { Button } from "../../../components/ui/button";
import { Badge } from "../../../components/ui/badge";
import { Card, CardContent } from "../../../components/ui/card";
import companyData from "../../../../../company-data.json";
import { useState } from "react";
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

export default function CompanyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params?.slug as string;
  const company = data[slug];
  const [selectedInterview, setSelectedInterview] = useState(0);

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

                  <Button className="w-full bg-indigo-100 text-indigo-600 rounded-full px-8 py-6 text-sm font-semibold hover:bg-indigo-200 transition-colors flex items-center justify-center">
                    Start Interview
                    <Play className="ml-2 size-4" />
                  </Button>
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
