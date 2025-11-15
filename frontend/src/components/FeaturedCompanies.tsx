import { Card, CardContent } from "./ui/card";
import { Button } from "./ui/button";
import { ArrowRight, FileText, Users, Brain } from "lucide-react";
import { Badge } from "./ui/badge";
import Link from "next/link";
import Image from "next/image";

type InterviewType = {
  type: string;
  format: string;
  keyFocus: string;
  tip: string;
};

type Company = {
  name: string;
  logo: string;
  color: string;
  logoBg?: string;
  difficulty: "Advanced" | "Intermediate";
  popular: boolean;
  interviewCount: number;
  interviews: InterviewType[];
};

const featuredCompanies: Company[] = [
  {
    name: "McKinsey & Company",
    logo: "/logos/mckinsey.svg",
    color: "bg-blue-600",
    difficulty: "Advanced",
    popular: true,
    interviewCount: 3,
    interviews: [
      {
        type: "PSI",
        format: "Interviewer-led",
        keyFocus: "Hypothesis-driven thinking, mental math, data interpretation",
        tip: "State clear hypothesis early, verbalize assumptions",
      },
      {
        type: "PEI",
        format: "Deep behavioral",
        keyFocus: "Leadership, personal impact, quantifiable results",
        tip: "Prepare 3-4 STAR stories with measurable outcomes",
      },
      {
        type: "Solve/PST",
        format: "Digital assessment",
        keyFocus: "Data interpretation under time pressure",
        tip: "Practice official PST PDFs, timeboxed drills",
      },
    ],
  },
  {
    name: "Boston Consulting Group",
    logo: "/logos/bcg.svg",
    color: "bg-green-600",
    difficulty: "Advanced",
    popular: true,
    interviewCount: 2,
    interviews: [
      {
        type: "Case",
        format: "Candidate-led",
        keyFocus: "Creative problem decomposition, commercial judgment",
        tip: "Lead with framework/issue tree, present concise recommendations",
      },
      {
        type: "Fit",
        format: "Behavioral",
        keyFocus: "Cultural fit, collaboration, influence",
        tip: "Use STAR with concrete metrics",
      },
    ],
  },
  {
    name: "Bain & Company",
    logo: "/logos/bc.svg",
    color: "bg-red-600",
    difficulty: "Advanced",
    popular: true,
    interviewCount: 2,
    interviews: [
      {
        type: "Case",
        format: "Candidate-led",
        keyFocus: "Practical commercial instincts, actionable recommendations",
        tip: "Focus on implementation – close with clear action plan",
      },
      {
        type: "Experience",
        format: "Behavioral",
        keyFocus: "Personal impact, teamwork, client presence",
        tip: "Show both problem solving and client-facing behavior",
      },
    ],
  },
  {
    name: "Deloitte Strategy",
    logo: "/logos/deloitte.jpeg",
    color: "bg-gray-800",
    logoBg: "#000",
    difficulty: "Intermediate",
    popular: false,
    interviewCount: 2,
    interviews: [
      {
        type: "Case",
        format: "Mixed format",
        keyFocus: "Structured analysis, implementation practicality",
        tip: "Clarify scope early, tie recommendations to implementation",
      },
      {
        type: "Group",
        format: "Team-based",
        keyFocus: "Teamwork, facilitation, synthesis",
        tip: "Speak early, structure team's approach, lead and listen",
      },
    ],
  },
  {
    name: "PwC Strategy&",
    logo: "/logos/pwc.svg",
    color: "bg-amber-700",
    difficulty: "Advanced",
    popular: false,
    interviewCount: 3,
    interviews: [
      {
        type: "Case",
        format: "Candidate-led",
        keyFocus: "Structured problem solving, commercial thinking",
        tip: "Practice both case breakdowns and written/group presentation exercises",
      },
      {
        type: "Written",
        format: "Presentation",
        keyFocus: "Written synthesis, slide/storytelling",
        tip: "Practice succinct slide decks and presenting with clarity under time pressure",
      },
      {
        type: "Fit",
        format: "Behavioral",
        keyFocus: "Leadership, client service, consulting drive",
        tip: "Have STAR examples with quantifiable results tied to client outcomes",
      },
    ],
  },
  {
    name: "EY-Parthenon",
    logo: "/logos/ey.jpeg",
    color: "bg-indigo-600",
    logoBg: "#161822",
    difficulty: "Advanced",
    popular: false,
    interviewCount: 3,
    interviews: [
      {
        type: "Case",
        format: "Candidate-led",
        keyFocus: "Strategic judgment, structuring, defending recommendations",
        tip: "Use describe-recommend-defend structure; be ready to defend assumptions",
      },
      {
        type: "Group",
        format: "Assessment center",
        keyFocus: "Collaboration, synthesis, presentation polish",
        tip: "Lead with clear recommendation, back with 2-3 succinct points",
      },
      {
        type: "Fit",
        format: "Behavioral",
        keyFocus: "Influence, client readiness, maturity of judgment",
        tip: "Prepare examples emphasizing persuasion and measurable outcomes",
      },
    ],
  },
];

export function FeaturedCompanies() {
  return (
    <section className="bg-white" id="companies">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-6xl mx-auto">
          {featuredCompanies.map((company) => (
            <Card key={company.name} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div
                      className="border border-gray-200 size-20 rounded-lg flex items-center justify-center shrink-0 p-2"
                      style={{ backgroundColor: company.logoBg || '#fff' }}
                    >
                      <Image
                        src={company.logo}
                        alt={`${company.name} logo`}
                        width={80}
                        height={80}
                        className="object-contain"
                      />
                    </div>
                    <div>
                      <h3 className="text-xl mb-1">{company.name}</h3>
                      <Badge variant={company.difficulty === "Advanced" ? "default" : "secondary"} className="rounded-full">
                        {company.difficulty}
                      </Badge>
                    </div>
                  </div>
                  {company.popular && (
                    <Badge className="bg-amber-100 text-amber-700 hover:bg-amber-100 rounded-full">
                      Most Popular
                    </Badge>
                  )}
                </div>

                <div className="mb-6 py-4 border-y border-gray-100">
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="flex items-center justify-center mb-2">
                        <FileText className="size-4 text-gray-400 mr-1" />
                        <span className="text-gray-500 text-sm">Types</span>
                        <span className="text-indigo-600 text-sm ml-1">({company.interviewCount})</span>
                      </div>
                      <div className="flex gap-1 justify-center flex-wrap">
                        {company.interviews.map((interview, idx) => (
                          <Badge key={idx} variant="secondary" className="text-xs rounded-full">
                            {interview.type}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div className="text-center border-x border-gray-100">
                      <div className="flex items-center justify-center mb-1">
                        <Users className="size-4 text-gray-400 mr-1" />
                        <span className="text-gray-500 text-sm">Rounds</span>
                      </div>
                      <p className="text-2xl text-indigo-600">{company.interviewCount * 2}</p>
                    </div>
                    <div className="text-center">
                      <div className="flex items-center justify-center mb-1">
                        <Brain className="size-4 text-gray-400 mr-1" />
                        <span className="text-gray-500 text-sm">Format</span>
                      </div>
                      <p className="text-xs text-indigo-600 leading-none mt-1">{company.interviews[0].format}</p>
                    </div>
                  </div>
                </div>

                <Link href={`/company/${company.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')}`} className="w-full">
                  <Button className="w-full rounded-full" variant="outline">
                    Details
                    <ArrowRight className="ml-2 size-4" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}