"""Data models for claim-verified topic research."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, model_validator


class TopicFinding(BaseModel):
    """A single source-grounded research finding."""

    title: str
    summary: str
    source_url: Optional[str] = None
    provenance: Optional[str] = None
    year: Optional[int] = None
    source_snippet: Optional[str] = None

    @model_validator(mode="after")
    def validate_source_or_provenance(self) -> "TopicFinding":
        has_url = bool(self.source_url and self.source_url.strip())
        has_provenance = bool(self.provenance and self.provenance.strip())
        if not has_url and not has_provenance:
            raise ValueError(
                "Each TopicFinding must include a non-empty source_url or provenance."
            )
        return self


class ExpandedSection(BaseModel):
    """A synthesized report section after post-expansion claim verification."""

    heading: str
    verified_claims: list[str] = Field(default_factory=list)
    stripped_claims: list[str] = Field(default_factory=list)
    supporting_urls: list[str] = Field(default_factory=list)


class VerifiedTopicReport(BaseModel):
    """Final verified research report with disclosures and audit counts."""

    topic: str
    target_year: Optional[int] = None
    offline_mode: bool = False
    disclosures: list[str] = Field(default_factory=list)
    findings: list[TopicFinding] = Field(default_factory=list)
    sections: list[ExpandedSection] = Field(default_factory=list)
    filtered_out_count: int = 0
    rejected_unverified_count: int = 0
