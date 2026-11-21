from topic_researcher.engine import ClaimVerifiedTopicResearcher


def test_allows_fewer_than_ten_findings_without_padding():
    researcher = ClaimVerifiedTopicResearcher(target_year=2026)
    candidates = [
        {
            "title": "Narrow Finding 1",
            "summary": "Central bank digital currency pilot launched in Q1 2026.",
            "source_url": "https://github.com/pra986/claim-verified-topic-researcher",
            "year": 2026,
        },
        {
            "title": "Narrow Finding 2",
            "summary": "Cross-border settlement latency dropped by 40 percent.",
            "source_url": "https://github.com/pra986/claim-verified-topic-researcher",
            "year": 2026,
        },
    ]
    report = researcher.research(
        topic="Narrow CBDC Settlement Pilot",
        target_year=2026,
        candidate_findings=candidates,
    )
    assert len(report.findings) == 2
    assert report.offline_mode is True
    assert any("offline" in d.lower() for d in report.disclosures)


def test_rejects_findings_without_source_url():
    researcher = ClaimVerifiedTopicResearcher(target_year=2026)
    candidates = [
        {
            "title": "Valid Finding",
            "summary": "Verified data point with URL.",
            "source_url": "https://github.com/pra986/claim-verified-topic-researcher",
            "year": 2026,
        },
        {
            "title": "Missing URL Finding",
            "summary": "This finding has no source URL.",
            "source_url": "",
            "year": 2026,
        },
    ]
    report = researcher.research(
        topic="Source URL Verification",
        target_year=2026,
        candidate_findings=candidates,
    )
    assert len(report.findings) == 1
    assert report.findings[0].title == "Valid Finding"
    assert report.rejected_unverified_count == 1


def test_filters_out_of_year_findings():
    researcher = ClaimVerifiedTopicResearcher(target_year=2026)
    candidates = [
        {
            "title": "Current Year",
            "summary": "2026 policy update.",
            "source_url": "https://github.com/pra986/claim-verified-topic-researcher",
            "year": 2026,
        },
        {
            "title": "Old Year",
            "summary": "2024 historical note.",
            "source_url": "https://github.com/pra986/claim-verified-topic-researcher",
            "year": 2024,
        },
    ]
    report = researcher.research(
        topic="Year Filtering",
        target_year=2026,
        candidate_findings=candidates,
    )
    assert len(report.findings) == 1
    assert report.findings[0].year == 2026
    assert report.filtered_out_count == 1


def test_post_expansion_entailment_strips_ungrounded_claims():
    researcher = ClaimVerifiedTopicResearcher(target_year=2026)
    candidates = [
        {
            "title": "Valid Finding",
            "summary": "Quantum encryption trials completed across three regional banks in 2026.",
            "source_url": "https://github.com/pra986/claim-verified-topic-researcher",
            "year": 2026,
            "source_snippet": "Quantum encryption trials completed across three regional banks in 2026.",
        }
    ]
    expanded = {
        "Valid Finding": [
            "Quantum encryption trials completed across three regional banks in 2026.",
            "Completely fabricated claim about Martian colonies buying treasury bonds.",
        ]
    }
    report = researcher.research(
        topic="Quantum Encryption",
        target_year=2026,
        candidate_findings=candidates,
        expanded_claims_by_heading=expanded,
    )
    assert len(report.sections) == 1
    section = report.sections[0]
    assert len(section.verified_claims) == 1
    assert len(section.stripped_claims) == 1
    assert "Martian colonies" in section.stripped_claims[0]
