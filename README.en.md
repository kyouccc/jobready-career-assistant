# JobReady · End-to-End Job Application Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Validate Skill](https://github.com/kyoucc/jobready-career-assistant/actions/workflows/validate.yml/badge.svg)](https://github.com/kyoucc/jobready-career-assistant/actions/workflows/validate.yml)
[![WorkBuddy Skill](https://img.shields.io/badge/WorkBuddy-Skill-blue.svg)](https://www.workbuddy.cn)

**English** | [简体中文](README.md)

---

> **Language note:** This skill is written in Chinese and targets the Chinese campus-recruiting
> market (校招 / 实习). The methodology documents, question banks, scripts and examples are all in
> Chinese, because that is the language of the target market and of the actual interviews.
> This English README exists so the project is discoverable and the design is reviewable by an
> international audience — not as a translated deliverable.

## What it is

A WorkBuddy skill package for **campus recruiting, internships, and first-job onboarding**.
Rather than a loose collection of prompts, it decomposes how HR and recruiters actually screen
candidates into executable workflows, scoring rubrics, and ready-to-use templates.

Covers 7 capabilities, 8 methodology documents, 3 fill-in output skeletons, and 2 executable scripts.

## Problems it solves

| Real pain point | What this skill does |
|---|---|
| Resume reads like a job description — all "responsible for X", no outcomes | STAR rewrite formula + guided quantification, with the reason for each edit annotated |
| You can't tell what the JD actually wants | Hidden-requirement inference table — reads work intensity and team state from wording |
| You finish an interview unsure what went wrong | 10-point rubric across 5 weighted dimensions, pinpointing which sentence cost you points |
| You compare offers by monthly salary alone | 7-dimension comparison + **effective hourly rate** (overtime and housing fund included) |
| You don't know what's negotiable or how to open | Three-stage negotiation scripts, plus which items are negotiable vs. standardized |
| The salary data you find is years old | Mandatory live retrieval; every figure carries source, date, and sample scope |

## Capabilities

| # | Capability | Deliverable |
|---|---|---|
| 1 | **Resume optimization** | Overall assessment + fully rewritten resume + enhancement suggestions |
| 2 | **JD analysis** | Hard requirements / hidden soft requirements / salary & cost-of-living / gap analysis / predicted interview questions |
| 3 | **Interview simulation** | 5 high-frequency questions + per-question 10-point scoring + model answers + review report |
| 4 | **Application documents** | Cover letter, thank-you note, offer acceptance, decline letter, inquiry email, internship certificate |
| 5 | **Offer comparison & negotiation** | 7-dimension table + computed totals + three-stage negotiation scripts |
| 6 | **Industry & salary reference** | Standard / SP / SSP tiers + dual promotion tracks + career-switch risk |
| 7 | **Newcomer guide** | Onboarding checklist, probation pitfalls, weekly report template, upward communication scripts |

## Installation

### Option 1: One-line installer (recommended)

**macOS / Linux / Git Bash**

```bash
git clone https://github.com/kyoucc/jobready-career-assistant.git
cd jobready-career-assistant
bash install.sh
```

**Windows PowerShell**

```powershell
git clone https://github.com/kyoucc/jobready-career-assistant.git
cd jobready-career-assistant
powershell -ExecutionPolicy Bypass -File install.ps1
```

### Option 2: Manual

```bash
git clone https://github.com/kyoucc/jobready-career-assistant.git \
  ~/.workbuddy-ai/skills/jobready-career-assistant
```

The repository root **is** the skill root, so cloning directly into the skills directory works
with no extra steps.

## Usage

Trigger it in natural language — no commands to memorize:

```
Help me rewrite my resume — I'm applying for a computer-vision algorithm internship.
```

```
Break down this JD and tell me whether I qualify: <paste JD>
```

```
Run a mock technical interview for a CV algorithm internship, focusing on my projects.
```

**Full-pipeline mode:** ask it to walk you through
`JD analysis → resume rewrite → application documents → mock interview → review → offer comparison → negotiation → onboarding prep`.

## Scripts

### `scripts/offer_calc.py` — total-compensation calculator

Upgrades offer comparison from "monthly salary" to "annual cash + housing fund + effective hourly rate".
Pure standard library, no third-party dependencies, Python 3.8+.

```bash
python scripts/offer_calc.py --demo                         # see sample input and output
python scripts/offer_calc.py offers.json                    # run with your own JSON
python scripts/offer_calc.py offers.json --format markdown   # emit a Markdown table
```

Outputs: annual cash (**guaranteed vs. floating** split), annual equity value, two-sided housing
fund, monthly net cash, monthly disposable balance, annual working hours, **effective hourly rate**,
and first-year probation loss. It also raises risk flags — e.g. "year-end bonus not in contract,
counted as floating", "housing fund base differs from salary", "weekly hours above statutory standard".

> Social insurance and income tax are estimated as flat rates, not progressive brackets.
> Results are for side-by-side comparison, not a precise take-home figure.

### `scripts/validate_skill.py` — format validator

Self-contained, does not depend on WorkBuddy's bundled scripts, runs in any environment:

```bash
python scripts/validate_skill.py .
```

## Repository layout

```
jobready-career-assistant/
├── SKILL.md                          # Entry point: role, hard rules, capability routing table
├── references/                       # Methodology (loaded on demand)
│   ├── 01-resume-optimization.md
│   ├── 02-jd-analysis.md
│   ├── 03-interview-simulation.md
│   ├── 04-job-documents.md
│   ├── 05-offer-negotiation.md
│   ├── 06-salary-benchmark.md
│   ├── 07-newcomer-guide.md
│   └── 08-tech-interview-bank.md
├── assets/                           # Fill-in output skeletons
├── examples/                         # Complete sample outputs (fictional personas)
├── scripts/
│   ├── offer_calc.py
│   └── validate_skill.py
├── install.sh / install.ps1
└── .github/workflows/validate.yml
```

## Design principles

These three rules are what separate this from a prompt collection, and every output must obey them:

**1. Never fabricate user data.**
Resume rewriting may restructure phrasing; it may not invent facts. When you haven't supplied
quantified data, it emits `【待确认：具体数值】` placeholders plus a question list, rather than
inventing a plausible-looking number — fabricated figures collapse under interview follow-ups.

**2. Salary and market data must be retrieved live.**
Salary figures in training data go stale, and reciting them is misleading. Every salary output
carries source, collection date, and sample scope. When offline, it says so and provides search
keywords and information channels instead of guessing.

**3. Deliverable first, explanation second.**
Copy-paste-ready content (the rewritten resume, scripts, full document text) comes first;
methodology notes come after.

## Examples

Three complete samples live in `examples/`, all using fictional personas. Excerpt from
`03-interview-review.md`:

> **Overall score: 6.8 / 10 → Grade: B**
>
> Your **debugging instinct already exceeds candidates at the same level** (9/10 on question 5).
> Every weakness traces back to one thing — **articulating the rationale behind technical choices**.
> That isn't a knowledge problem, it's a preparation-method problem.

## FAQ

**Is this for experienced hires?**
It targets campus recruiting, internships, and early career. Resume rewriting, offer comparison
and negotiation, and workplace communication transfer well; interview simulation and JD analysis
would need deeper seniority-specific question banks.

**How accurate is the salary data?**
Not guaranteed accurate — guaranteed *sourced, dated, and scoped*. Campus salaries vary widely with
background, interview performance, and that year's headcount. Data is for building an expectation
range, not a promise.

**Do the examples contain real people?**
No. "Li Siyuan" and "Xingye Tech" and all associated figures are fictional demonstration data.

## Contributing

Contributions of question banks, negotiation scripts, and industry data are welcome.
Run before submitting:

```bash
python scripts/validate_skill.py .
python scripts/offer_calc.py --demo > /dev/null
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

[MIT](LICENSE)
