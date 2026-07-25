# SECOND-KNOWLEDGE-BRAIN.md — Startup Pitch Deck Builder & Scorer (Idea 57)

Grown weekly by `tools/knowledge_updater.py`. This file is the offline
knowledge base the harness falls back to when live web research is
unavailable, and the cited baseline used even when online.

## Core Concepts & Frameworks
- **Sequoia deck template:** Company purpose → Problem → Solution → Why now → Market size → Competition → Product → Business model → Team → Financials. Narrative arc first; numbers support the story.
- **Guy Kawasaki 10/20/30:** 10 slides, 20 minutes, 30pt font — clarity & focus; every slide must survive a 20-second skim.
- **YC essentials:** clear one-liner, real traction, big market, credible team, concrete ask. Traction is the strongest signal.
- **a16z / First Round guidance:** crisp problem framing, credible founder-market fit, repeatable GTM, honest competition.
- **Canonical 11-slide set (scored):** Problem, Solution, Market/TAM, Product, Business model, Traction, GTM, Competition, Team, Financials, Ask.
- **TAM/SAM/SOM:** bottom-up market sizing (#customers × ACV) preferred over top-down "X% of a huge market".
- **Scoring axes:** Persuasion (does it make me want in?), Logic (does the argument hold?), Clarity (is it instantly understandable?).

## Scoring Dimensions (per slide)
| Axis | Weight | Anchor |
|------|--------|--------|
| Persuasion | 40% | investor appeal, proof |
| Logic | 35% | argument validity, defensible numbers |
| Clarity | 25% | comprehension at a glance |

## Per-Slide Rubric Summary
| Slide | Key required elements |
|-------|-----------------------|
| Problem | who suffers; pain/cost; why now; concrete data |
| Solution | one-line value prop; maps to problem; mechanism; differentiation |
| Market/TAM | bottom-up sizing; the math; TAM/SAM/SOM; cited source |
| Product | proof of existence; outcomes (not feature dumps); defensible tech; plain language |
| Business model | revenue model; pricing/ACV; unit economics (CAC/LTV/payback); one-liner |
| Traction | growth trend; revenue (not vanity); retention/NRR; cadence |
| GTM | named channels; CAC/payback; repeatable motion; one-liner |
| Competition | real competitors; comparison axes; how you win; moat |
| Team | founders+roles; founder-market fit; prior outcomes; gap coverage |
| Financials | projection+horizon; assumptions; realistic (no hockey-stick); margin/burn/runway |
| Ask | raise amount; use of funds; milestones; runway |

## Detector Signals (named investor objections)
- **Top-down TAM** (`X% of a $YB market`) → logic penalty; demand bottom-up.
- **Vanity metrics** (signups/visitors/downloads without revenue or retention) → persuasion penalty.
- **Hockey-stick financials** (large ARR within ~2 years, no assumptions) → logic penalty.
- **No moat** → competition logic penalty.
- **Missing canonical slide** → blocker gap + add-slide roadmap item.

## Sector Benchmark Norms (dated 2026 anchors — not investment advice)
| Sector | Anchor | Norm |
|--------|--------|------|
| SaaS | Net revenue retention | 110–130% strong at Series A |
| SaaS | CAC payback | < 12 months healthy |
| SaaS | LTV:CAC | > 3:1 common threshold |
| SaaS | Growth (Series A) | T2D3 (triple, triple, double, double, double) |
| Marketplace | Take rate | 10–30% by category |
| Marketplace | NRR | 100–115% common |
| Fintech | Unit economics | contribution margin scrutinized; compliance gating |
| Consumer | Retention | D1/D30 scrutinized at seed; ARPU+churn > vanity DAU |
| General | Traction cadence | MoM/QoQ with explicit periods |
| General | Bottom-up TAM | preferred over top-down |

## Key Research / Sources
| Title | Source | Year | Link | Relevance |
|-------|--------|------|------|-----------|
| What we look for in pitches | Sequoia | 2024 | sequoiacap.com | Investor lens |
| Startup pitch deck advice | Y Combinator | 2024 | ycombinator.com | Investor lens |
| 10/20/30 rule of PowerPoint | Guy Kawasaki | 2023 | guykawasaki.com | Clarity rubric |
| First Round Review pitch guidance | First Round | 2024 | review.firstround.com | Narrative & GTM |
| Entrepreneurial finance & signaling | SSRN | 2022 | ssrn.com | Traction/credibility |

## State-of-the-Art Methods & Tools
Deck teardown frameworks, bottom-up TAM modeling, traction-metric
benchmarking (CAC/LTV/payback/NRR), narrative arc design, dated sector
benchmark tracking.

## Authoritative Data Sources
Sequoia, Y Combinator, a16z, First Round Review, SSRN entrepreneurial
finance, venture benchmark reports (always dated).

## Analytical Frameworks
Sequoia template · Kawasaki 10/20/30 · YC essentials · a16z/First Round ·
TAM/SAM/SOM · Persuasion-Logic-Clarity rubric.

## Self-Update Protocol
- Queries: "pitch deck benchmark 2026", "seed round metrics", "VC pitch expectations".
- Sources: Sequoia/YC/a16z/First Round/SSRN. Frequency: weekly.
- Append: `- [DATE] Title — Source — URL <!--h:hash-->`. Dedupe by hash.

## Knowledge Update Log
- [2026-06-18] Seed entry — frameworks + slide canon documented. — Maintainer — local <!--h:000000000001-->
- [2026-06-20] Sequoia pitch template canon documented. — Sequoia — https://sequoiacap.com <!--h:a1b2c3d4e5f6-->
- [2026-06-20] YC essentials: one-liner, traction, market, team, ask. — YC — https://ycombinator.com <!--h:b2c3d4e5f6a7-->
- [2026-06-20] Kawasaki 10/20/30 rule documented. — Guy Kawasaki — https://guykawasaki.com <!--h:c3d4e5f6a7b8-->
- [2026-06-21] SaaS benchmark anchors (NRR/CAC/LTV/T2D3) recorded (dated 2026). — Maintainer — local <!--h:d4e5f6a7b8c9-->