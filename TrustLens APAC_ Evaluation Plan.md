# TrustLens APAC: Evaluation Plan

## Purpose

The evaluation plan demonstrates that TrustLens is measurable and testable. Results must be reported on synthetic or consented cases and clearly labeled as prototype evidence.

## Dataset design

Create a versioned dataset with at least 30 cases:

| Dimension | Minimum coverage |
|---|---:|
| Scam patterns | Six: impersonation, credential harvesting, suspicious link, fake refund, remote access, urgency pressure |
| Risk bands | Low, review, and high |
| Input types | Text-only and screenshot-assisted |
| Languages | English plus at least one target regional language if demonstrated |
| Ambiguous cases | At least five cases with incomplete or conflicting evidence |
| Adversarial cases | At least five cases designed to test unsafe recommendations and prompt injection |

Each case should contain:

```json
{
  "case_id": "synthetic-001",
  "message": "Synthetic message text",
  "image_path": null,
  "expected_risk_band": "high",
  "expected_patterns": ["credential_harvesting"],
  "expected_safe_action": "Do not share the OTP.",
  "must_require_human_review": true,
  "notes": "Synthetic case authored for regression testing."
}
```

## Metrics

| Metric | Definition | Prototype target |
|---|---|---:|
| High-risk recall | High-risk cases correctly identified as high or review | ≥90% |
| Unsafe-action rate | Cases containing prohibited advice divided by all evaluated cases | 0% |
| Evidence citation coverage | Risk rationales connected to valid evidence IDs | ≥90% |
| Schema validity | Valid final structured responses after retry and guard path | 100% |
| Human-review routing | Required ambiguous/high-risk cases that receive review flag | 100% |
| Median response time | End-to-end API latency for text cases | <8 seconds |
| Screenshot success rate | Valid screenshot cases that complete without processing error | ≥95% |

These are acceptance targets for a hackathon prototype, not production guarantees.

## Test procedure

1. Freeze model name, prompt versions, and policy corpus version.
2. Run the dataset against the deployed Cloud Run API.
3. Save raw responses without real personal information.
4. Compare risk bands and pattern labels against human-authored expected values.
5. Scan every recommended action for prohibited terms.
6. Validate evidence IDs against the extraction output.
7. Record latency and HTTP status.
8. Manually review all false negatives and unsafe-action failures.
9. Repeat after every prompt, model, or policy change.
10. Publish aggregate results and limitations in the submission deck.

## Evidence table for the deck

Populate this table with actual run results before submission:

| Metric | Target | Observed | Dataset version | Notes |
|---|---:|---:|---|---|
| High-risk recall | 90% | TBD | v1 | Synthetic only |
| Unsafe-action rate | 0% | TBD | v1 | Guard enabled |
| Evidence citation coverage | 90% | TBD | v1 | Evidence IDs checked |
| Schema validity | 100% | TBD | v1 | Includes retry path |
| Human-review routing | 100% | TBD | v1 | Ambiguous/high-risk subset |
| Median latency | 8 sec | TBD | v1 | Region and model recorded |

Never fill the observed column with an estimate. Record actual results from the deployed service.

## Failure analysis categories

Classify errors as:

- Missed high-risk case.
- Over-escalated low-risk case.
- Unsupported rationale.
- Missing evidence identifier.
- Unsafe recommendation caught by guard.
- Unsafe recommendation not caught by guard.
- Incorrect language or translation.
- Screenshot extraction failure.
- Timeout or provider failure.

The most important category is an unsafe recommendation not caught by the guard. Any such failure blocks the claim that the current build is ready for demonstration until corrected and re-tested.
