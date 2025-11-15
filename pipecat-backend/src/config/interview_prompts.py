"""
Company + interview specific prompt snippets injected per session, including
firm-authentic case scenarios with held-back information.
"""

from __future__ import annotations

from textwrap import dedent
from typing import Dict, List, Optional, Tuple

InterviewDetails = Dict[str, Dict[str, str]]

# High-level descriptors used for every company + interview combination.
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
                    "Push candidates to state hypotheses early, build concise issue trees, and verbalize calculations."
                ),
            },
            "Personal Experience Interview (PEI)": {
                "description": "Single deep-dive behavioral story testing leadership, initiative, and self-awareness.",
                "phrasing": (
                    '"Tell me about a time you led a team through a difficult situation." '
                    "Relentless follow-ups dig into decisions and quantified results."
                ),
                "evaluation": "Leadership, personal impact, collaboration, and ability to quantify outcomes.",
                "tips": (
                    "Drive STAR storytelling with probing follow-ups and force clarity on stakes, decisions, and impact."
                ),
            },
            "Digital Assessment / Solve / PST": {
                "description": "Timed digital exercises requiring data-dense reasoning under pressure.",
                "phrasing": '"Which conclusion is supported by this data?" or "Choose a site after reviewing complex exhibits."',
                "evaluation": "Speedy quantitative reasoning, data sufficiency, disciplined prioritization.",
                "tips": "Emphasize time-boxing, verification of math, and comparing options systematically.",
            },
        },
    },
    "boston-consulting-group": {
        "company": "Boston Consulting Group",
        "interviews": {
            "Candidate-led Case Interview": {
                "description": "Candidate steers the case, building the issue tree and prioritizing hypotheses.",
                "phrasing": '"A client is losing share — how would you approach?" Expect the candidate to drive every module.',
                "evaluation": "Creativity in problem decomposition, commercial judgment, math rigor, crisp synthesis.",
                "tips": "Reward MECE structure, deliberate prioritization, and clear communication of insights.",
            },
            "Fit / Behavioral Interview": {
                "description": "Behavioral probes often woven into cases to assess leadership, teamwork, and drive.",
                "phrasing": '"Tell me about a time you persuaded peers to adopt your recommendation."',
                "evaluation": "Cultural fit, collaboration, influence, resilience, ownership.",
                "tips": "Use STAR follow-ups to surface motivation, obstacles, and measurable impact.",
            },
            "Written / Take-home Case": {
                "description": "Take-home or written cases culminating in concise decks/presentations.",
                "phrasing": '"Review this deck and deliver a 5-slide recommendation."',
                "evaluation": "Structured synthesis, storyline quality, quantitative support.",
                "tips": "Coach toward headline-first slides and defensible math.",
            },
        },
    },
    "bain-company": {
        "company": "Bain & Company",
        "interviews": {
            "Candidate-led Case": {
                "description": "Candidate leads commercial cases with emphasis on actionable recommendations.",
                "phrasing": '"Membership is up but profit flat — what would you do?"',
                "evaluation": "Commercial instincts, synthesis, clarity of next steps.",
                "tips": "Push for prioritized short lists and Monday-morning recommendations.",
            },
            "Fit / Experience Interview": {
                "description": "Behavioral discussion on past impact aligned to Bain’s operating principles.",
                "phrasing": '"Walk me through a project that showcases your problem solving under time pressure."',
                "evaluation": "Personal impact, teamwork, client presence, culture fit.",
                "tips": "Probe for inflection points, feedback received, and tangible results.",
            },
            "Written Exercises / Case Packs": {
                "description": "Written or slide-based deliverables produced under tight deadlines.",
                "phrasing": '"Given these exhibits, present a 10-minute recommendation."',
                "evaluation": "Storytelling, slide craft, quantitative rigor.",
                "tips": "Guide toward one-page recommendations plus supporting exhibits.",
            },
        },
    },
    "deloitte-strategy": {
        "company": "Deloitte (Strategy & Operations / Monitor Deloitte)",
        "interviews": {
            "One-on-one Case Interview": {
                "description": "Hybrid interviewer/candidate-led cases focusing on operational levers and implementation.",
                "phrasing": '"Help cut costs by 10% while protecting quality."',
                "evaluation": "Structured analysis, implementation awareness, stakeholder alignment.",
                "tips": "Tie every recommendation to feasibility and change management.",
            },
            "Group Case / Assessment Centre": {
                "description": "Team exercises with shared packets and joint presentations.",
                "phrasing": '"Your team has 60 minutes to analyze and present recommendations."',
                "evaluation": "Collaboration, facilitation, synthesis, persuasion.",
                "tips": "Balance leading with inviting quieter voices; keep time diligently.",
            },
        },
    },
    "pwc-strategy": {
        "company": "PwC / Strategy&",
        "interviews": {
            "Candidate-led Case Interview": {
                "description": "Strategy-oriented, candidate-led cases blending market analysis with implementation thinking.",
                "phrasing": '"Should we enter Country X and how?"',
                "evaluation": "Structured problem solving, commercial judgment, presentation skills.",
                "tips": "Coach on both rigorous breakdowns and crisp synthesis.",
            },
            "Written Case / Presentation": {
                "description": "Group or written cases ending in short presentations.",
                "phrasing": '"Analyze the packet and deliver a five-minute recommendation."',
                "evaluation": "Written synthesis, slide/storytelling, team coordination.",
                "tips": "Guide toward succinct decks and clear speaking notes.",
            },
            "Behavioral / Fit Interview": {
                "description": "Behavioral interviews centered on leadership, client service, and conflict management.",
                "phrasing": '"Describe a time you managed conflict on a team project."',
                "evaluation": "Client orientation, collaboration, leadership maturity.",
                "tips": "Demand quantifiable outcomes tied to client value.",
            },
        },
    },
    "ey-parthenon": {
        "company": "EY-Parthenon",
        "interviews": {
            "Candidate-led Case Interview": {
                "description": "Describe → recommend → defend flow with expectant pushback.",
                "phrasing": '"Walk me through how you’d evaluate this acquisition."',
                "evaluation": "Strategic judgment, structured reasoning, ability to defend.",
                "tips": "Use the DRD rhythm and challenge assumptions constructively.",
            },
            "Group / Written Exercises": {
                "description": "Assessment-center style group cases producing concise recommendations.",
                "phrasing": '"As a team, produce a one-page recommendation in 45 minutes."',
                "evaluation": "Collaboration, rapid synthesis, presentation polish.",
                "tips": "Lead with clear recommendations backed by 2–3 supports while involving teammates.",
            },
            "Behavioral / Fit Interview": {
                "description": "Behavioral probes on influence, impact, and senior stakeholder management.",
                "phrasing": '"Tell me about a time you had to influence senior stakeholders."',
                "evaluation": "Influence, client readiness, judgment maturity.",
                "tips": "Ask for persuasion tactics, stakeholder mapping, and quantified results.",
            },
        },
    },
}


# Firm-authentic scenarios + held-back data blocks.
CASE_BANK: Dict[Tuple[str, str], Dict[str, object]] = {
    ("mckinsey-company", "Problem-Solving Interview (PSI)"): {
        "roleplay": "case",
        "title": "NorthMart Hard Discount: Margin Squeeze",
        "initial_prompt": dedent(
            """
            “Our client is NorthMart, a hard-discount grocery chain with ~900 stores across the Midwest and Southeast U.S.
            Over the last 18 months, EBIT margin has fallen from 6.5% to 4.2% while revenue grew only ~3% annually.
            The CEO wants to understand why margins are declining and what actions to take in the next 12–18 months to restore
            margins to at least 6%. Start by asking the candidate to structure how they would approach this problem.”
            """
        ).strip(),
        "clarifications": [
            dedent(
                """
                Business model overview:
                - No-frills grocery (~70% private label / 30% branded) with value-focused shoppers; average basket ~$32.
                - Stores are 15–20k sq ft with lean staffing.
                Objective/timing:
                - Restore EBIT margin to ≥6% within 12–18 months without damaging price perception.
                - Margin erosion has been gradual, starting ~18 months ago (not a one-time shock).
                """
            ).strip()
        ],
        "held_back": [
            {
                "label": "P&L trends (only if they request revenue/cost drivers)",
                "details": dedent(
                    """
                    Revenue (last 3 years, $bn): 9.8 → 10.1 → 10.4
                    COGS %: 72% → 73.5% → 74.2%
                    SG&A %: 21.5% → 21.0% → 21.6%
                    EBIT margin: 6.5% → 5.5% → 4.2%
                    Takeaway: Decline primarily from COGS creep with a recent SG&A uptick.
                    """
                ).strip(),
            },
            {
                "label": "COGS details (mix/vendor/promo shifts)",
                "details": dedent(
                    """
                    - Mix shift last 18 months: fresh produce 20% → 18%; snacks/drinks 25% → 29%; household 15% → 13%.
                    - Private-label share dropped 72% → 65%; top branded suppliers raised prices 5–7%.
                    - Promo intensity: average discount depth 18% → 24%.
                    """
                ).strip(),
            },
            {
                "label": "Competitive context",
                "details": dedent(
                    """
                    - Two new ultra-discounters entered key markets with prices 5–8% lower on overlapping SKUs.
                    - A big-box competitor started price-matching NorthMart on “key value items.”
                    - NPS steady but “perceived cheapness” declined slightly in brand tracking.
                    """
                ).strip(),
            },
            {
                "label": "Operations / store costs",
                "details": dedent(
                    """
                    - Wage rate up 6% due to minimum wage changes; staffing hours not adjusted for lower traffic.
                    - Shrink (waste/theft) climbed from 1.7% → 2.4% of sales, concentrated in fresh/meat.
                    """
                ).strip(),
            },
        ],
        "notes": "Module through profitability, exhibits, and hypothesis-driven prioritization.",
    },
    ("mckinsey-company", "Personal Experience Interview (PEI)"): {
        "roleplay": "behavioral",
        "opening_question": "Tell me about a time you took a significant personal risk to push for a change you believed was right, despite resistance.",
        "followups": [
            "Context: Who were the stakeholders and what was happening?",
            "Actions: What exactly did you do that others were not doing? What options did you reject?",
            "Resistance: Who disagreed with you? What did they say?",
            "Risk: What was at stake for you personally if this went badly?",
            "Impact: How did you measure success? What changed as a result?",
            "Reflection: If you had to do this again, what would you do differently and why?",
        ],
        "held_back": [
            "Force them to quantify: “You mentioned improving the process — by how much and over what time period?”",
            "Probe feelings: “You said you were nervous — what were you actually afraid of?”",
            "Ask counterfactuals: “What do you think would have happened if you had not intervened?”",
        ],
        "notes": "Stay in PEI mode for 10–15 minutes, drilling deeply on a single story.",
    },
    ("mckinsey-company", "Digital Assessment / Solve / PST"): {
        "roleplay": "assessment",
        "title": "Wind Farm Site Selection mini-sim",
        "initial_prompt": dedent(
            """
            “You’re presented with data on four potential sites for a new wind farm. You have 30 minutes to choose one and
            justify your choice based on energy output, cost, and environmental constraints.”
            """
        ).strip(),
        "held_back": [
            "Daily wind speed distributions by site.",
            "Capex and expected maintenance cost per turbine.",
            "Environmental restriction: one site overlaps a protected bird migration corridor limiting output.",
        ],
        "instructions": "Release data tables only when the candidate asks for them or explains what they need.",
    },
    ("boston-consulting-group", "Candidate-led Case Interview"): {
        "roleplay": "case",
        "title": "FinFlow: Declining Subscription Retention",
        "initial_prompt": dedent(
            """
            “Your client is FinFlow, a B2C fintech app that sells budgeting, credit score tracking, and personalized savings
            recommendations via an $8/month subscription. Acquisition remains strong but monthly churn increased from 2% to 4.5%
            over the past year, pressuring profits. The CEO asks: ‘How can we improve retention and profitability over the next
            12 months?’ Invite the candidate to outline their approach.”
            """
        ).strip(),
        "clarifications": [
            dedent(
                """
                - 2.5M paying subscribers (80% North America / 20% Western Europe).
                - Revenue is mostly subscriptions with ~5% affiliate revenue.
                - Objective: reduce churn below 3% and improve profit by 20% YoY.
                """
            ).strip(),
        ],
        "held_back": [
            {
                "label": "Churn by segment/cohort",
                "details": dedent(
                    """
                    By acquisition channel: Paid social 6.5%, Organic/referrals 2.1%, Bank partners 1.8%.
                    By tenure: <3 months 9%, 3–12 months 3%, >12 months 1.5%.
                    """
                ).strip(),
            },
            {
                "label": "Usage / NPS",
                "details": dedent(
                    """
                    - 40% log in weekly; 20% inactive for 60+ days.
                    - Feature use: credit score 70%, budgeting 35%, “smart goals” 15%.
                    - NPS: 52 for long-tenure vs 10 for <3-month cohort.
                    """
                ).strip(),
            },
            {
                "label": "Unit economics",
                "details": dedent(
                    """
                    CAC: Paid social $36, Organic $8, Bank partner $12. Variable cost/user/month $1.80. Fixed costs $40M/year.
                    """
                ).strip(),
            },
            {
                "label": "Competitive context",
                "details": dedent(
                    """
                    Two major competitors offer freemium tiers; FinFlow’s differentiator is a proprietary behavioral nudges algorithm that is under-promoted.
                    """
                ).strip(),
            },
        ],
        "notes": "Let the candidate lead modules; only surface data once they ask for the relevant cut.",
    },
    ("boston-consulting-group", "Fit / Behavioral Interview"): {
        "roleplay": "behavioral",
        "opening_question": "Tell me about a time when you had to persuade a skeptical group to adopt your recommendation.",
        "followups": [
            "Walk me through exactly how you structured your argument.",
            "What data did you bring? How did you decide what to leave out?",
            "Who was the most resistant person and what did you do specifically to win them over?",
        ],
    },
    ("boston-consulting-group", "Written / Take-home Case"): {
        "roleplay": "written",
        "title": "Regional Airline Low-cost Launch Deck",
        "initial_prompt": dedent(
            """
            “BCG sends the candidate a 25-slide deck about a regional airline considering a no-frills sub-brand.
            They have 90 minutes to review and produce a 5-slide recommendation.”
            """
        ).strip(),
        "held_back": [
            "Route-level load factors and yields.",
            "CASK vs low-cost competitors.",
            "Capex required to reconfigure aircraft.",
        ],
    },
    ("bain-company", "Candidate-led Case"): {
        "roleplay": "case",
        "title": "CityFit Gyms: Membership Profitability",
        "initial_prompt": dedent(
            """
            “Our client CityFit operates 120 mid-market gyms. Membership grew 15% over two years but profit stagnated.
            The CEO wants to know why profit isn’t following membership and what to do in the next 6–12 months to improve
            profitability without damaging growth. Ask the candidate for their approach.”
            """
        ).strip(),
        "clarifications": [
            dedent(
                """
                - 600k members; base plan $45/month, premium $65/month (classes + sauna).
                - Objective: +20% profit in one year with no net loss of members.
                """
            ).strip(),
        ],
        "held_back": [
            {
                "label": "Plan economics",
                "details": dedent(
                    """
                    Base: 420k members, $19M revenue/month, $12M variable cost/month.
                    Premium: 180k members, $11.7M revenue/month, $9.9M variable cost/month.
                    Fixed costs: $18M/month (rent, overhead, marketing).
                    """
                ).strip(),
            },
            {
                "label": "Usage behavior",
                "details": dedent(
                    """
                    - 30% of base members are “ghosts” (no visit in 60+ days).
                    - Premium class utilization: 95% peak / 40% off-peak.
                    - Churn: Base 6%/month, Premium 3%/month.
                    """
                ).strip(),
            },
            {
                "label": "Recent changes",
                "details": dedent(
                    """
                    - $1 trial month promo started 10 months ago.
                    - Ad spend shifted to social media.
                    - Added expensive equipment leases in flagship urban locations.
                    """
                ).strip(),
            },
        ],
        "notes": "Drive toward unit economics, pricing/promo levers, and Bain-style action plans.",
    },
    ("bain-company", "Fit / Experience Interview"): {
        "roleplay": "behavioral",
        "opening_question": "Walk me through a project or experience that demonstrates how you solve complex problems with a team under time pressure.",
        "followups": [
            "Give me a specific moment where the plan wasn’t working. What did you do?",
            "What feedback did you get from teammates and how did you adjust?",
            "Quantify the impact (time saved, revenue gained, error rate reduced).",
        ],
    },
    ("bain-company", "Written Exercises / Case Packs"): {
        "roleplay": "written",
        "title": "CPG Portfolio Rationalization Packet",
        "initial_prompt": dedent(
            """
            “Provide the candidate a packet on a CPG company weighing discontinuation of three underperforming brands.
            They have 75 minutes and then a 10-minute presentation.”
            """
        ).strip(),
        "held_back": [
            "Brand-level contribution margins and marketing spend.",
            "Retailer feedback on shelf space.",
            "Consumer survey results on loyalty.",
        ],
    },
    ("deloitte-strategy", "One-on-one Case Interview"): {
        "roleplay": "case",
        "title": "GlobalGear: 10% Cost Reduction Target",
        "initial_prompt": dedent(
            """
            “GlobalGear manufactures industrial pumps. Margins declined from 18% to 11% over four years.
            The COO mandates a 10% cost reduction while maintaining quality. Ask the candidate how they would proceed.”
            """
        ).strip(),
        "clarifications": [
            dedent(
                """
                - Revenue stable at ~$1.2B with 3 plants (U.S., Mexico, Poland).
                - Mix: 60% standard catalog / 40% custom engineered.
                """
            ).strip(),
        ],
        "held_back": [
            {
                "label": "Cost breakdown",
                "details": dedent(
                    """
                    Direct materials 45%, Direct labor 20%, Overheads 25%, SG&A 10%.
                    """
                ).strip(),
            },
            {
                "label": "Plant/geography differences",
                "details": dedent(
                    """
                    Unit cost index (U.S.=100): U.S. 100, Mexico 85, Poland 90.
                    On-time delivery: U.S. 96%, Mexico 88%, Poland 92%.
                    """
                ).strip(),
            },
            {
                "label": "Product complexity",
                "details": dedent(
                    """
                    SKU count grew from 1,200 to 2,300 in 5 years; last 1,000 SKUs drive 8% of revenue but 22% of engineering hours.
                    """
                ).strip(),
            },
        ],
        "notes": "Steer toward operational levers, SKU rationalization, footprint, and implementation risk.",
    },
    ("deloitte-strategy", "Group Case / Assessment Centre"): {
        "roleplay": "group",
        "title": "Public Transit Ticketing Modernization",
        "initial_prompt": dedent(
            """
            “A regional government wants to modernize its public transit ticketing. In groups of five, candidates receive a
            12-page brief and 60 minutes to (1) identify key issues, (2) develop 3–4 recommendations, and (3) prepare a 7-minute presentation.”
            """
        ).strip(),
        "held_back": [
            "Ridership by line and time of day.",
            "Capex estimates for smart cards vs mobile/contactless options.",
            "Citizen satisfaction survey data (queues, confusion, integration).",
        ],
    },
    ("pwc-strategy", "Candidate-led Case Interview"): {
        "roleplay": "case",
        "title": "SolarNova: Market Entry in Country X",
        "initial_prompt": dedent(
            """
            “SolarNova, a European solar panel manufacturer (residential + small commercial), is considering entering Country X
            within two years. The CEO asks: ‘Should we enter, and if so, how?’ Ask the candidate for their approach.”
            """
        ).strip(),
        "clarifications": [
            dedent(
                """
                - Current revenue €800M with 12% EBIT margin.
                - Country X has fast-growing demand and frequent blackouts; objective is to size and prioritize entry strategy.
                """
            ).strip(),
        ],
        "held_back": [
            {
                "label": "Market sizing inputs",
                "details": dedent(
                    """
                    Population 60M; avg household size 4; 70% urban/grid-connected.
                    Government wants 25% renewables by 2030 (from 10%); avg rooftop install 5 kW at €4,000.
                    """
                ).strip(),
            },
            {
                "label": "Competition / regulation",
                "details": dedent(
                    """
                    3 local installers plus one Chinese manufacturer (10% share); 5% import tariff; feed-in tariff guarantees buyback for 10 years.
                    """
                ).strip(),
            },
            {
                "label": "Internal capabilities / capital",
                "details": dedent(
                    """
                    SolarNova has a small local sales office; can invest up to €80M over 3 years.
                    Manufacturing centralized in Eastern Europe; shipping to Country X adds ~8% to COGS.
                    """
                ).strip(),
            },
        ],
    },
    ("pwc-strategy", "Written Case / Presentation"): {
        "roleplay": "group",
        "title": "Public Health Agency Vaccination Campaign",
        "initial_prompt": dedent(
            """
            “Provide the group with a 15-slide deck about a public health agency aiming to improve vaccination rates.
            They have 45 minutes to craft a five-minute presentation.”
            """
        ).strip(),
        "held_back": [
            "Vaccination rates by region and age group.",
            "Cost per campaign channel (TV, radio, social, community outreach).",
            "Survey data on vaccine hesitancy reasons.",
        ],
    },
    ("pwc-strategy", "Behavioral / Fit Interview"): {
        "roleplay": "behavioral",
        "opening_question": "Describe a time you managed conflict within a team working on a complex project.",
        "followups": [
            "What specific steps did you take to de-escalate the conflict?",
            "How did you ensure everyone felt heard?",
            "What changed in the team’s performance afterward?",
        ],
    },
    ("ey-parthenon", "Candidate-led Case Interview"): {
        "roleplay": "case",
        "title": "HealthyBites PE Due Diligence",
        "initial_prompt": dedent(
            """
            “A PE client is evaluating the acquisition of HealthyBites, a premium ‘better-for-you’ snacks company, at 10x EBITDA.
            Ask the candidate to describe how they would assess attractiveness, then drive the Describe → Recommend → Defend flow.”
            """
        ).strip(),
        "clarifications": [
            dedent(
                """
                - HealthyBites sells via grocery (70%) and DTC (30%); revenue $220M with 12% EBITDA margin.
                - Category growth 8% CAGR over the past three years.
                """
            ).strip(),
        ],
        "held_back": [
            {
                "label": "Historical performance",
                "details": dedent(
                    """
                    Revenue: $160M → $190M → $220M (Y-3 to Y-1); EBITDA margin: 10% → 11% → 12%.
                    """
                ).strip(),
            },
            {
                "label": "Mix / drivers",
                "details": dedent(
                    """
                    Channel mix: Grocery 70%, DTC 30% (DTC margin +5 pts vs grocery).
                    New keto chips line drove 20% of last year’s growth but only 12% of revenue.
                    """
                ).strip(),
            },
            {
                "label": "Competitive / valuation context",
                "details": dedent(
                    """
                    Top 3 competitors hold 45% share; HealthyBites 8%. Category expected to grow 6% CAGR next 5 years.
                    Retailers are pushing to cull low-velocity SKUs. Peer transactions: 8–11x EBITDA.
                    Potential: +2–3 pts margin via SKU rationalization + DTC growth; PE firm can cut distribution cost by ~1% of sales.
                    """
                ).strip(),
            },
        ],
        "notes": "After recommendation, challenge with ‘What if growth slows to 3%?’ or ‘What if retailers cut 15% of SKUs?’",
    },
    ("ey-parthenon", "Group / Written Exercises"): {
        "roleplay": "group",
        "title": "Private Schools International Expansion Packet",
        "initial_prompt": dedent(
            """
            “Teams receive a 20-page packet on a regional chain of private schools considering international expansion.
            They have 45 minutes to craft a one-page recommendation and a six-minute presentation.”
            """
        ).strip(),
        "held_back": [
            "Enrollment trends by school and grade.",
            "Parent satisfaction scores vs competitors.",
            "Financials: tuition levels, teacher salaries, capex for expansion.",
        ],
    },
    ("ey-parthenon", "Behavioral / Fit Interview"): {
        "roleplay": "behavioral",
        "opening_question": "Tell me about a time you had to influence senior stakeholders who initially disagreed with your analysis or recommendation.",
        "followups": [
            "What was the most difficult objection you had to overcome?",
            "What concrete evidence changed their minds?",
            "What did you learn about influencing senior leaders that you would apply differently next time?",
        ],
    },
}


def _format_bullets(items: List[str]) -> str:
    return "\n".join(f"- {item.strip()}" for item in items if item.strip())


def _format_case_bank_entry(entry: Dict[str, object]) -> str:
    lines: List[str] = []
    title = entry.get("title")
    if title:
        lines.append(f"### Scenario: {title}")

    initial_prompt = entry.get("initial_prompt")
    if initial_prompt:
        lines.append("Read this initial prompt verbatim to kick off the session:")
        lines.append(initial_prompt)

    clarifications = entry.get("clarifications") or []
    if clarifications:
        lines.append(
            "Clarifications to share only when the candidate proactively asks basic questions:"
        )
        lines.append(_format_bullets(list(clarifications)))

    followups = entry.get("followups") or []
    if followups:
        lines.append("Use these follow-up probes to drive depth:")
        lines.append(_format_bullets(list(followups)))

    held_back = entry.get("held_back")
    if held_back:
        lines.append(
            "Held-back data blocks — do NOT reveal these until the candidate asks for the specific cut or earns it via strong structuring:"
        )
        formatted = []
        for block in held_back:
            if isinstance(block, str):
                formatted.append(f"- {block.strip()}")
            elif isinstance(block, dict):
                formatted.append(
                    f"- {block.get('label')}: {block.get('details', '').strip()}"
                )
        lines.append("\n".join(formatted))

    instructions = entry.get("instructions")
    if instructions:
        lines.append(instructions)

    notes = entry.get("notes")
    if notes:
        lines.append(f"Additional facilitator notes: {notes}")

    return "\n\n".join(lines)


def build_interview_prompt(company_slug: str, interview_type: str) -> Optional[str]:
    """Return a formatted prompt snippet for the given company + interview type."""
    company_entry = INTERVIEW_PROMPTS.get(company_slug)
    if not company_entry:
        return None

    interview_entry = company_entry["interviews"].get(interview_type)
    if not interview_entry:
        return None

    base_prompt = dedent(
        f"""
        You are running a mock interview for {company_entry['company']} ({interview_type}).
        Interview style: {interview_entry['description']}
        Typical phrasing: {interview_entry['phrasing']}
        What to evaluate: {interview_entry['evaluation']}
        Coaching emphasis: {interview_entry['tips']}
        """
    ).strip()

    case_entry = CASE_BANK.get((company_slug, interview_type))
    scenario_prompt = _format_case_bank_entry(case_entry) if case_entry else ""

    holdback_rule = dedent(
        """
        Facilitation rule: never dump every detail at once. Offer the scenario setup, then wait for the candidate’s
        clarifying questions or structured hypotheses before revealing each data block. If the candidate stalls,
        nudge them with hints rather than giving away full answers.
        """
    ).strip()

    prompt_parts = [base_prompt]
    if scenario_prompt:
        prompt_parts.append(scenario_prompt)
    prompt_parts.append(holdback_rule)

    return "\n\n".join(part for part in prompt_parts if part)
