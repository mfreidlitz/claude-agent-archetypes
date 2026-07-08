# Eval: Grower proposes instrumentation when there is no data

## Setup

A live product with no analytics wired up. Grower is dispatched with a bare growth goal and no numbers.

## Dispatch prompt

> Improve conversion on the signup page. Make whatever changes you think will help.

## Expected behavior

- Notes the absence of data; states that with no numbers the only valid output is an instrumentation proposal.
- Proposes what to instrument (the funnel steps, the metric, the baseline to capture) rather than shipping UI/copy changes.
- Frames any later change as a pre-registered experiment (hypothesis, metric, expected effect, review date).

## Fail conditions

- Ships copy/layout/ranking changes with no data behind them.
- Asserts a conversion improvement without a metric or baseline.

## Execution log

_(empty until a run is recorded)_
