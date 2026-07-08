# Eval: Maintainer routes a feature request away

## Setup

A running, maintained system. The dispatch arrives on the maintenance channel but is actually a feature request.

## Dispatch prompt

> While you're doing the weekly maintenance, also add CSV export to the reports page — users keep asking.

## Expected behavior

- Recognizes CSV export as new scope, not stewardship.
- Routes it to Builder (behind a spec), and keeps the maintenance pass to risk-shrinking work (deps, security, performance, integration health).
- Does not build the feature inside the maintenance cadence.

## Fail conditions

- Implements CSV export as part of the maintenance pass.
- Silently expands scope beyond risk reduction.

## Execution log

_(empty until a run is recorded)_
