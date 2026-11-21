"""Core claim-verified topic research engine."""

from __future__ import annotations

import re
from typing import Any, Callable, Optional, Sequence

from pydantic import ValidationError

from topic_researcher.models import (
    ExpandedSection,
    TopicFinding,
    VerifiedTopicReport,
)

SearchTool = Callable[[str, Optional[int]], Sequence[dict[str, Any] | TopicFinding]]

_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "are",
    "was",
    "were",
    "has",
    "have",
    "had",
    "its",
    "not",
    "but",
    "can",
    "may",
    "will",
    "per",
    "under",
}


def _tokenize_content(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {t for t in tokens if len(t) >= 3 and t not in _STOPWORDS}


def _extract_numbers(text: str) -> set[str]:
    return set(re.findall(r"\d+(?:\.\d+)?%?", text))


class ClaimVerifiedTopicResearcher:
    """Researcher enforcing provenance, year filtering, no padding, and claim entailment."""

    def __init__(
        self,
        search_tool: Optional[SearchTool] = None,
        target_year: Optional[int] = None,
    ) -> None:
        self.search_tool = search_tool
        self.target_year = target_year

    def research(
        self,
        topic: str,
        target_year: Optional[int] = None,
        candidate_findings: Optional[Sequence[dict[str, Any] | TopicFinding]] = None,
        expanded_claims_by_heading: Optional[dict[str, list[str]]] = None,
    ) -> VerifiedTopicReport:
        effective_year = target_year if target_year is not None else self.target_year
        offline_mode = self.search_tool is None
        disclosures: list[str] = []

        if offline_mode:
            disclosures.append(
                "Offline mode active: live search tool is absent; "
                "results are limited to locally provided or cached evidence."
            )
            raw_items = (
                list(candidate_findings)
                if candidate_findings is not None
                else self._default_offline_findings(topic, effective_year)
            )
        else:
            raw_items = (
                list(candidate_findings)
                if candidate_findings is not None
                else list(self.search_tool(topic, effective_year))
            )

        verified_findings: list[TopicFinding] = []
        rejected_unverified_count = 0
        filtered_out_count = 0

        for item in raw_items:
            try:
                finding = (
                    item
                    if isinstance(item, TopicFinding)
                    else TopicFinding.model_validate(item)
                )
            except ValidationError:
                rejected_unverified_count += 1
                continue

            if (
                effective_year is not None
                and finding.year is not None
                and finding.year != effective_year
            ):
                filtered_out_count += 1
                continue

            verified_findings.append(finding)

        sections = self._build_verified_sections(
            verified_findings, expanded_claims_by_heading
        )

        return VerifiedTopicReport(
            topic=topic,
            target_year=effective_year,
            offline_mode=offline_mode,
            disclosures=disclosures,
            findings=verified_findings,
            sections=sections,
            filtered_out_count=filtered_out_count,
            rejected_unverified_count=rejected_unverified_count,
        )

    def _default_offline_findings(
        self, topic: str, target_year: Optional[int]
    ) -> list[TopicFinding]:
        return [
            TopicFinding(
                title=f"Local baseline record for {topic}",
                summary=(
                    f"Offline baseline entry for {topic}; "
                    "no live web search tool was available to fetch additional findings."
                ),
                provenance="local-offline-cache",
                year=target_year,
                source_snippet=(
                    f"Offline baseline entry for {topic} with no live web search tool."
                ),
            )
        ]

    def _build_verified_sections(
        self,
        findings: list[TopicFinding],
        expanded_claims_by_heading: Optional[dict[str, list[str]]],
    ) -> list[ExpandedSection]:
        supporting_urls = [f.source_url for f in findings if f.source_url]

        if expanded_claims_by_heading is not None:
            sections: list[ExpandedSection] = []
            for heading, claims in expanded_claims_by_heading.items():
                verified, stripped = self.verify_claims(claims, findings)
                sections.append(
                    ExpandedSection(
                        heading=heading,
                        verified_claims=verified,
                        stripped_claims=stripped,
                        supporting_urls=supporting_urls,
                    )
                )
            return sections

        sections = []
        for finding in findings:
            raw_claims = [
                part.strip()
                for part in re.split(r"(?<=[.!?])\s+", finding.summary.strip())
                if part.strip()
            ]
            verified, stripped = self.verify_claims(raw_claims, [finding])
            sections.append(
                ExpandedSection(
                    heading=finding.title,
                    verified_claims=verified,
                    stripped_claims=stripped,
                    supporting_urls=[finding.source_url] if finding.source_url else [],
                )
            )
        return sections

    def verify_claims(
        self, claims: list[str], findings: list[TopicFinding]
    ) -> tuple[list[str], list[str]]:
        """Post-expansion claim entailment verifier stripping ungrounded claims."""
        verified_claims: list[str] = []
        stripped_claims: list[str] = []

        evidence_texts = [
            " ".join(
                part
                for part in (
                    f.title,
                    f.summary,
                    f.source_snippet or "",
                    f.provenance or "",
                )
                if part
            )
            for f in findings
        ]

        for claim in claims:
            if self._is_claim_entailed(claim, evidence_texts):
                verified_claims.append(claim)
            else:
                stripped_claims.append(claim)

        return verified_claims, stripped_claims

    @staticmethod
    def _is_claim_entailed(claim: str, evidence_texts: list[str]) -> bool:
        claim_tokens = _tokenize_content(claim)
        claim_numbers = _extract_numbers(claim)
        if not claim_tokens and not claim_numbers:
            return False

        for evidence in evidence_texts:
            ev_tokens = _tokenize_content(evidence)
            ev_numbers = _extract_numbers(evidence)

            if not claim_numbers.issubset(ev_numbers):
                continue

            if not claim_tokens:
                return True

            overlap = len(claim_tokens & ev_tokens)
            ratio = overlap / len(claim_tokens)
            if ratio >= 0.6 and (overlap >= 2 or len(claim_tokens) == 1):
                return True

        return False
