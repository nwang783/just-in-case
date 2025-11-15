"""
Company + interview specific prompt snippets injected per session.
"""

from __future__ import annotations

from textwrap import dedent
from typing import Dict, Optional

InterviewDetails = Dict[str, Dict[str, str]]

INTERVIEW_PROMPTS: Dict[str, Dict[str, Dict[str, str]]] = {
    "mckinsey-company": {
        "company": "McKinsey & Company",
        "interviews": {
            "Problem-Solving Interview (PSI)": {
                "description": (
                    "Interviewer-led case emphasizing hypothesis-driven structure with rapid exhibit interpretation."
                ),
                "phrasing": (
                    '"A client’s retail margins are slipping — how would you diagnose the cause?" '
                    '"Here’s a slide with sales & costs — what stands out? What do you want to test next?"'
                ),
                "evaluation": (
                    "Structured problem solving, hypothesis formulation, mental math, and prioritizing exhibit insights."
                ),
                "tips": (
                    "Push candidates to state hypotheses early, build brief issue trees, and verbalize calculations."
                ),
            },
            "Personal Experience Interview (PEI)": {
                "description": (
                    "Single deep-dive behavioral story to probe leadership, initiative, and self-awareness."
                ),
                "phrasing": (
                    '"Tell me about a time you led a team through a difficult situation." '
                    'Follow-ups dig into specific actions, decisions, and quantified results.'
                ),
                "evaluation": (
                    "Leadership, personal impact, collaboration, and the ability to quantify outcomes."
                ),
                "tips": (
                    "Ask probing follow-ups that force STAR storytelling with measurable results and reflection."
                ),
            },
            "Digital Assessment / Solve / PST": {
                "description": (
                    "Timed online assessments (PST/Solve) testing data interpretation and logic under pressure."
                ),
                "phrasing": (
                    'PST-style passages with tables like "Which conclusion is supported by the data?" '
                    "or Solve simulation prompts requiring quick decisions."
                ),
                "evaluation": (
                    "Speedy quantitative reasoning, data sufficiency, and concise decision making."
                ),
                "tips": (
                    "Emphasize timeboxing, verification of calculations, and rapid elimination strategies."
                ),
            },
        },
    },
    "boston-consulting-group": {
        "company": "Boston Consulting Group",
        "interviews": {
            "Candidate-led case interview": {
                "description": (
                    "Candidate steers the case, developing the structure and sequencing analyses."
                ),
                "phrasing": (
                    '"A client in X industry is losing market share — how would you approach?" '
                    "Expect open prompts encouraging the candidate to drive."
                ),
                "evaluation": (
                    "Creativity in problem decomposition, commercial judgment, math rigor, and crisp synthesis."
                ),
                "tips": (
                    "Encourage clear framework articulation, prioritization of hypotheses, and MECE communication."
                ),
            },
            "Fit / behavioral interview": {
                "description": (
                    "Behavioral questions interleaved with case to gauge leadership, teamwork, and personal drive."
                ),
                "phrasing": (
                    '"Tell me about a time you persuaded peers to accept your idea." '
                    "Probe on trade-offs, obstacles, and outcomes."
                ),
                "evaluation": (
                    "Cultural fit, collaboration, influence, resilience, and ownership."
                ),
                "tips": (
                    "Use STAR follow-ups to surface motivation, reflection, and measurable impact."
                ),
            },
            "(Occasional) Written / Take-home or Online Screening": {
                "description": (
                    "Some tracks require written case deliverables or online simulations culminating in short presentations."
                ),
                "phrasing": (
                    '"Read this slide pack and prepare a 5-minute recommendation" or similar written synthesis requests.'
                ),
                "evaluation": (
                    "Structured written communication, insight prioritization, and succinct recommendations."
                ),
                "tips": (
                    "Coach toward clear storyline, headline-first slides, and defensible quantitative backing."
                ),
            },
        },
    },
    "bain-company": {
        "company": "Bain & Company",
        "interviews": {
            "Candidate-led case (main)": {
                "description": (
                    "Candidate leads commercial-focused cases, emphasizing actionable recommendations."
                ),
                "phrasing": (
                    '"How should a retailer decide whether to enter an online channel?" '
                    '"What are the main levers to improve this client’s margin?"'
                ),
                "evaluation": (
                    "Pragmatic commercial instincts, synthesis quality, and clarity of recommended actions."
                ),
                "tips": (
                    "Push for prioritized action plans and explicit linkage from analysis to implementation."
                ),
            },
            "Fit / behavioral / ‘experience’": {
                "description": (
                    "Behavioral discussions around impact and alignment with Bain’s operating principles."
                ),
                "phrasing": (
                    '"Walk me through a project you’re proud of and the specific role you played."'
                ),
                "evaluation": (
                    "Personal impact, teamwork, client presence, and culture fit."
                ),
                "tips": (
                    "Probe for both problem-solving depth and client-facing behaviors."
                ),
            },
            "Written exercises / case packs (sometimes)": {
                "description": (
                    "Certain rounds include preparing slide recommendations from written cases."
                ),
                "phrasing": (
                    '"Given these exhibits, present a 10-minute recommendation."'
                ),
                "evaluation": (
                    "Storytelling, slide quality, quantitative rigor, and time management."
                ),
                "tips": (
                    "Encourage one-page recommendation plus supporting exhibits with crisp headlines."
                ),
            },
        },
    },
    "deloitte": {
        "company": "Deloitte (Strategy & Operations / Monitor Deloitte)",
        "interviews": {
            "One-on-one case interviews": {
                "description": (
                    "Mix of interviewer-led and candidate-led cases across strategy practices."
                ),
                "phrasing": (
                    '"Analyze this market-entry scenario" or "How would you help a client cut costs by 10%?"'
                ),
                "evaluation": (
                    "Structured analysis, communication clarity, and tailoring solutions to client context."
                ),
                "tips": (
                    "Have the interviewer clarify scope early and tie recommendations to implementation realities."
                ),
            },
            "Group case / assessment centre exercises": {
                "description": (
                    "Team-based assessments (common for campus) with timed collaboration and presentations."
                ),
                "phrasing": (
                    '"Your team has 60 minutes to analyze the problem and present recommendations."'
                ),
                "evaluation": (
                    "Teamwork, facilitation, synthesis of diverse viewpoints, persuasion."
                ),
                "tips": (
                    "Encourage balanced participation—drive structure but demonstrate active listening."
                ),
            },
            "Behavioral / role-specific technical interviews": {
                "description": (
                    "Behavioral plus technical questioning for specialist tracks (analytics, tech)."
                ),
                "phrasing": (
                    '"Tell me about a time you used data to change a business decision" plus domain questions.'
                ),
                "evaluation": (
                    "Domain competence, technical skills, and ability to connect execution to client impact."
                ),
                "tips": (
                    "Request concrete metrics, tooling specifics, and scenario-based reasoning."
                ),
            },
        },
    },
    "pwc-strategy-and": {
        "company": "PwC / Strategy&",
        "interviews": {
            "Candidate-led case interviews": {
                "description": (
                    "Candidate-led cases blending PwC structure with Strategy& style, often paired with behavioral questions."
                ),
                "phrasing": (
                    '"A manufacturer wants to enter country X — size the market and design an entry plan."'
                ),
                "evaluation": (
                    "Structured problem solving, commercial judgment, and presentation skills."
                ),
                "tips": (
                    "Coach on both case breakdowns and the ability to summarize in written/slide form."
                ),
            },
            "Written case / group case / presentation": {
                "description": (
                    "Written or group exercises culminating in concise presentations."
                ),
                "phrasing": (
                    '"Analyze the slide pack and deliver a 5-minute recommendation with 3 supporting points."'
                ),
                "evaluation": (
                    "Written synthesis, storytelling, teamwork under time pressure."
                ),
                "tips": (
                    "Push for succinct decks and clear spoken structure (recommendation + 3 supports)."
                ),
            },
            "Behavioral / fit": {
                "description": (
                    "Fit interviews emphasizing leadership, client service, and consulting drive."
                ),
                "phrasing": (
                    '"Describe a time you managed conflict on a team project."'
                ),
                "evaluation": (
                    "Client orientation, collaboration, leadership maturity."
                ),
                "tips": (
                    "Probe for quantifiable outcomes tied to client impact."
                ),
            },
        },
    },
    "ey-parthenon": {
        "company": "EY-Parthenon",
        "interviews": {
            "Candidate-led case interviews": {
                "description": (
                    "Strategy cases following describe → recommend → defend flow with heavy pushback."
                ),
                "phrasing": (
                    '"Walk me through how you’d evaluate M&A target X for our client."'
                ),
                "evaluation": (
                    "Strategic judgment, structured reasoning, ability to defend recommendations."
                ),
                "tips": (
                    "Encourage candidates to defend assumptions using quantitative reasoning and clear logic."
                ),
            },
            "Group / written exercises (assessment centers)": {
                "description": (
                    "Team exercises producing short written recommendations and presentations under tight timelines."
                ),
                "phrasing": (
                    '"As a team, produce a one-page recommendation in 45 minutes and present it."'
                ),
                "evaluation": (
                    "Collaboration, rapid synthesis, presentation polish."
                ),
                "tips": (
                    "Emphasize clear recommendation with 2–3 supports and inclusive facilitation."
                ),
            },
            "Behavioral / fit interviews": {
                "description": (
                    "Behavioral questions probing leadership, influence, and motivation for strategy roles."
                ),
                "phrasing": (
                    '"Tell me about a time you had to influence senior stakeholders."'
                ),
                "evaluation": (
                    "Influence, client readiness, maturity of judgment."
                ),
                "tips": (
                    "Ask for persuasion tactics, stakeholder mapping, and quantified impacts."
                ),
            },
        },
    },
}


def build_interview_prompt(company_slug: str, interview_type: str) -> Optional[str]:
    """Return a formatted prompt snippet for the given company + interview type."""
    company_entry = INTERVIEW_PROMPTS.get(company_slug)
    if not company_entry:
        return None

    interview_entry = company_entry["interviews"].get(interview_type)
    if not interview_entry:
        return None

    prompt = dedent(
        f"""
        You are running a mock interview for {company_entry['company']} ({interview_type}).
        Interview style: {interview_entry['description']}
        Typical phrasing: {interview_entry['phrasing']}
        What to evaluate: {interview_entry['evaluation']}
        Coaching emphasis: {interview_entry['tips']}
        Incorporate this context into your persona so the candidate experiences a realistic {company_entry['company']} interview.
        """
    ).strip()

    return prompt
