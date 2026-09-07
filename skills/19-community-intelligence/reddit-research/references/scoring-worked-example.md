# Worked Example — scoring a theme end-to-end

Scenario: research question — "Is there demand for a tool that normalizes
ecommerce product feeds?"

## 1. Ledger (extract first, classify second)

| # | Quote (abridged) | Subreddit | Date | Engagement | Signals |
|---|---|---|---|---|---|
| 1 | "I spend 3 hours a week fixing feed errors by hand" | r/ecommerce | 2026-04 | 22 up / 14 cmt | workflow problem, frequency |
| 2 | "Built a python script to clean our feed, happy to share" | r/shopify | 2026-03 | 8 / 5 | workaround |
| 3 | "Feed tool Y chokes on our variant data" | r/ecommerce | 2026-04 | 15 / 9 | competitor weakness |
| 4 | "Would pay real money for something that just fixed feeds" | r/FulfillmentByAmazon | 2026-02 | 31 / 18 | purchase intent, willingness to pay |
| 5 | "What's everyone using for feed management?" | r/ecommerce | 2026-05 | 12 / 25 | recommendation request |
| 6 | "This new AI feed thing is amazing" | r/smallbusiness | 2026-05 | 210 / 44 | hype/curiosity |

## 2. Theme: "manual feed cleanup pain"
- Threads: 1, 2, 3, 4 (4 distinct authors, 3 communities, Feb–May → recurring)
- Signal scores (0–2): severity 2 (hours weekly, error-prone), frequency 2
  (weekly, scripted), urgency 0, workaround cost 2 (script + manual hours),
  stated spend 1 ("real money", no number), replacement intent 1 (tool Y
  dissatisfaction), purchase intent 1, willingness to pay 1 (no number),
  breadth 2 (3 communities), confidence 2 (dated, linked, verbatim).
- **Verdict: strong theme.** Not "proven market" — that needs demand
  validation outside Reddit (see demand-validation skill).

## 3. Theme: "AI feed tools" (the 210-upvote hype post)
- Threads: 6 only. Severity 0, breadth 1, confidence 1.
- **Verdict: high-engagement / low-intent.** The upvote count must not leak
  into the score. Report separately as trend signal.

## 4. What the handoff carries
To demand-validation: theme statement, ledger rows 1–4 (quotes, links,
dates), confidence + rationale, unknowns (no stated prices, sample n=4).
To opportunity-scoring: theme score above with per-axis numbers, not a
single made-up "opportunity score".

## 5. Anti-patterns this example avoids
- Treating post 6's 210 upvotes as demand (loud ≠ valuable).
- Averaging threads 1–4 into "some interest" (scores must stay per-axis).
- Writing "users would pay for this" without the verbatim quote + link.
- Claiming market size from 4 threads across 3 subreddits.
