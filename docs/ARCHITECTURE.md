# Architecture

## Overview

`claim-verified-topic-researcher` implements a deterministic, source-grounded topic research pipeline designed to prevent common LLM synthesis failure modes:

1. **No Forced-Count Padding**: Narrow or niche topics may yield fewer than 10 findings. The engine never pads reports with filler or speculative items to hit an arbitrary quota.
2. **Mandatory Provenance**: Every `TopicFinding` must carry either a `source_url` or an explicit `provenance` string. Findings lacking both are rejected before synthesis.
3. **Temporal Year Filtering**: When `target_year` is specified, findings with a mismatched `year` are filtered out and recorded in `filtered_out_count` rather than silently mixed into current-year analysis.
4. **Post-Expansion Claim Entailment Verification**: After expanding findings into narrative sections (`ExpandedSection`), each sentence/claim is checked against the supporting evidence (`source_snippet` / `summary` / `provenance`). Ungrounded claims are flagged in `stripped_claims` and removed from `verified_claims`.
5. **Explicit Offline Mode Disclosure**: When no live search tool is provided (`search_tool is None`), the engine sets `offline_mode=True` and includes a clear disclosure in `disclosures` noting the absence of live search tools.

## Data Models (`topic_researcher/models.py`)

- **`TopicFinding`**: Core evidence unit (`title`, `summary`, `source_url`, `provenance`, `year`, `source_snippet`).
- **`ExpandedSection`**: Narrative expansion (`heading`, `verified_claims`, `stripped_claims`, `supporting_urls`).
- **`VerifiedTopicReport`**: Final structured output (`topic`, `target_year`, `offline_mode`, `disclosures`, `findings`, `sections`, `filtered_out_count`, `rejected_unverified_count`).

## Pipeline Flow (`topic_researcher/engine.py`)

```
Query + Target Year + Optional Search Tool
   │
   ├─► Live Search Tool (if provided) OR Offline Mode Disclosure
   │
   ├─► Provenance Gate (require source_url or provenance)
   │
   ├─► Year Filter (retain only target_year findings when configured)
   │
   ├─► Variable-Count Findings (0..N, never padded to 10)
   │
   └─► Post-Expansion Claim Entailment Verifier
         ├─► Entailed claims -> ExpandedSection.verified_claims
         └─► Ungrounded claims -> ExpandedSection.stripped_claims
```
