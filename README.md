# Claim-Verified Topic Researcher

**Project 35 / X4: Supplement / Agentic — CrewAI Topic Researcher**

A CrewAI-inspired topic research pipeline that produces variable-count, source-linked findings on narrow topics and runs post-expansion **claim entailment verification** so every synthesized claim is grounded in retrieved source evidence.

---

## Architecture

```
Topic Query
   │
   ▼
[1. Topic Scoping & Query Decomposition]
   │  Narrows ambiguous queries into focused sub-questions
   ▼
[2. Multi-Source Retrieval (Serper / Web Tools)]
   │  Collects candidate URLs, snippets, and primary source passages
   ▼
[3. Variable-Count Finding Extraction]
   │  Emits 1..N structured findings based on actual evidence density (no padding)
   ▼
[4. Claim Expansion & Synthesis]
   │  Drafts concise narrative claims linked to source IDs
   ▼
[5. Post-Expansion Claim Entailment Verification]
   │  Checks each expanded claim against its cited source passage (entailed / unsupported / contradicted)
   ▼
[6. Report Emission & Audit Trail]
   └─ Outputs verified markdown report + structured JSON verification ledger
```

---

## 6-Stage Workflow

1. **Topic Scoping**: Normalizes the narrow topic prompt, extracts key entities/constraints, and generates targeted search queries.
2. **Source Retrieval**: Fetches candidate sources and deduplicates by canonical URL while recording retrieval timestamps and source metadata.
3. **Variable-Count Finding Extraction**: Extracts only the findings genuinely supported by retrieved sources (`min_findings=1`, dynamic upper bound) rather than forcing a fixed bullet count.
4. **Claim Expansion**: Expands each finding into a clear, readable research claim with explicit inline source citations.
5. **Post-Expansion Entailment Verification**: Evaluates whether every expanded claim is strictly entailed by its linked source passages; flags or prunes unsupported extrapolations before final output.
6. **Report Emission**: Writes the final verified research report and machine-readable verification summary.

---

## Data Contract

- **`SourceDocument`**: `source_id`, `url`, `title`, `snippet`, `content`, `retrieved_at`
- **`ResearchFinding`**: `finding_id`, `topic`, `summary`, `source_ids`, `confidence`
- **`ExpandedClaim`**: `claim_id`, `finding_id`, `text`, `cited_source_ids`
- **`EntailmentResult`**: `claim_id`, `verdict` (`"entailed" | "unsupported" | "contradicted"`), `rationale`, `support_score`
- **`VerifiedResearchReport`**: `topic`, `findings`, `claims`, `entailment_results`, `verified_markdown`

---

## Production Controls

- **Variable-Count Guardrail**: Prevents hallucinated filler when a narrow topic has fewer than `N` genuine findings.
- **Post-Expansion Entailment Gate**: Blocks or flags any claim that introduces numbers, dates, or causal leaps not present in its cited source text.
- **Strict Source Linking**: Every finding and claim must reference at least one valid `source_id` with a non-empty URL.
- **Deterministic Offline Testing**: Supports injectable mock search/entailment providers so `pytest` runs offline without live API keys.

---

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Run tests:

```bash
pytest
```

---

## Attribution

Inspired by and adapted from **`ed-donner/agents`** (`3_crewai/reference/researcher`).
