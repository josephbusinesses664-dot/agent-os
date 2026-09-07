# Demand Validation — evidence rules & falsifiable tests

Deep material for the demand-validation skill. Load when the decision is
significant (pricing, positioning, build/no-build) rather than routine.

## Claim ≠ Fact — the seven labels

Every statement in a demand-validation artifact carries exactly one label:

| Label | Meaning | Example |
|---|---|---|
| observation | what was directly seen/measured | "thread has 31 upvotes" |
| source | where an observation came from | "r/ecommerce, Apr 2026, link" |
| evidence | observation + source + relevance to the question | "3 distinct authors report weekly manual cleanup (links)" |
| inference | reasoning from evidence | "the pain recurs across communities" |
| assumption | accepted as true without evidence | "poster budgets resemble buyer budgets" |
| recommendation | what to do, given the above | "run a landing-page smoke test" |
| confidence | calibrated strength of the above | "medium — no pricing evidence yet" |

The failure mode this prevents: an inference stated fluently gets promoted
to "fact" somewhere downstream. Every artifact keeps the labels visible.

## Falsification-first test design

A demand test is only valid if it can fail. Before running any test, write
down the result that would kill the idea:

- Landing page smoke test → kill if conversion < 2% with targeted traffic.
- Pre-order / deposit → kill if < 10 committed payments in 2 weeks.
- Concierge MVP → kill if users won't repeat after the free first time.
- LOI (letter of intent) → kill if < 3 signable LOIs from ICP interviews.

If no outcome would change the decision, the test is theater — redesign it.

## Willingness-to-pay ladder (weakest → strongest evidence)

1. "I'd pay for this" (statement)
2. Clicked pricing page
3. Entered email on a paid-tier waitlist
4. Started checkout
5. Paid a deposit / pre-ordered
6. Renewed after first cycle

Never cite rung 1 as willingness-to-pay without labeling it. Report the
highest rung actually observed, with counts.

## Contradiction handling

When evidence conflicts (interviewees love it, thread data is lukewarm):
- preserve both, with sources;
- look for a segmentation variable (team size, frequency, budget) that
  explains the split;
- if none explains it, lower confidence and widen the test — do not pick
  the answer that matches the hypothesis.

## Stop condition

Stop when: the decision has enough labeled evidence to act, or further
searching stops changing the conclusion (diminishing information gain).
Write the stop condition down before starting; otherwise research expands
to fill the budget.
