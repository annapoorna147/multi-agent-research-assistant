"""
Evidence Intelligence Engine

Day 3 of Multi-Agent Research Assistant V2.

Responsibilities:
- Extract meaningful claims from source content.
- Rank claims by research usefulness.
- Prioritize actual research findings and measured evidence.
- Remove metadata and bibliographic/reference noise.
- Remove duplicate or near-duplicate claims.
- Find supporting evidence for each claim.
- Map claims to supporting evidence.
- Calculate evidence strength.
- Build citation records and evidence summaries.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any


class EvidenceIntelligence:
    """Build claim-to-evidence mappings from research sources."""

    STOPWORDS = {
        "about", "after", "again", "against", "also", "because",
        "been", "being", "between", "could", "does", "doesn",
        "from", "have", "having", "into", "more", "most", "other",
        "over", "same", "should", "some", "such", "than", "that",
        "their", "there", "these", "they", "this", "those",
        "through", "under", "were", "which", "while", "with",
        "would", "your", "what", "when", "where", "will",
        "using", "used", "uses", "based", "many", "much", "only",
        "very",
    }

    RESEARCH_KEYWORDS = {
        "ai", "artificial", "intelligence", "healthcare",
        "clinical", "clinician", "doctor", "patient", "patients",
        "diagnosis", "diagnostic", "disease", "treatment",
        "medical", "medicine", "health", "imaging",
        "algorithm", "algorithms", "machine", "learning", "deep",
        "prediction", "predictive", "drug", "discovery",
        "monitoring", "screening", "accuracy", "sensitivity",
        "specificity", "study", "studies", "research", "evidence",
        "trial", "trials", "analysis", "application",
        "applications", "technology", "data", "electronic",
        "records", "ehr", "surgery", "radiology", "cancer",
        "telehealth", "outcome", "outcomes", "performance",
        "model", "models", "detection", "identified",
    }

    HIGH_VALUE_RESEARCH_KEYWORDS = {
        "study", "studies", "trial", "trials", "cohort",
        "randomized", "clinical", "patients", "patient",
        "diagnosis", "diagnostic", "treatment", "outcome",
        "outcomes", "accuracy", "sensitivity", "specificity",
        "performance", "validation", "validated", "prediction",
        "predicted", "detected", "detection", "identified",
        "identification", "improved", "improvement", "reduced",
        "reduction", "increased", "increase", "decreased",
        "decrease", "compared", "comparison", "effect", "effects",
        "association", "associated", "evidence", "findings",
        "results", "demonstrated", "reported", "evaluated",
        "evaluation", "experiment", "experiments", "model",
        "models", "algorithm", "algorithms",
    }

    LOW_VALUE_CONTENT_KEYWORDS = {
        "course", "courses", "program", "programs",
        "specialization", "curriculum", "enrollment", "enroll",
        "learner", "learners", "beginner", "certificate",
        "professor", "assistant", "faculty", "instructor",
        "university", "school", "department", "biography",
        "researcher", "career", "education", "students",
    }

    METADATA_KEYWORDS = {
        "copyright", "license", "licence", "creativecommons",
        "creative", "attribution", "author", "authors",
        "pmcid", "pmid", "doi", "issn", "journal",
        "publication", "published", "volume", "issue",
        "abstract", "keywords", "received", "accepted",
        "manuscript", "affiliation", "department", "funding",
        "contributor", "contributions", "permission",
        "reproduction", "distribution", "open-access", "terms",
        "bibliography", "citation", "references",
    }

    def __init__(self) -> None:
        self.last_claims: list[dict[str, Any]] = []
        self.last_evidence_map: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Text normalization
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize whitespace without destroying sentence boundaries."""

        if not text:
            return ""

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    @classmethod
    def _keywords(cls, text: str) -> list[str]:
        """Extract meaningful lowercase keywords."""

        words = re.findall(
            r"\b[a-zA-Z][a-zA-Z0-9-]{2,}\b",
            text.lower(),
        )

        return [
            word
            for word in words
            if word not in cls.STOPWORDS
        ]

    # ------------------------------------------------------------------
    # Sentence processing
    # ------------------------------------------------------------------

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        """Split source text into reasonably clean sentences."""

        text = EvidenceIntelligence._normalize_text(text)

        if not text:
            return []

        text = re.sub(
            r"\[\s*\d+\s*\]",
            "",
            text,
        )

        text = re.sub(
            r"\[\s*edit\s*\]",
            ". ",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s+(?:edit|edited)\s+(?=[A-Z])",
            ". ",
            text,
            flags=re.IGNORECASE,
        )

        sentences = re.split(
            r"(?<=[.!?])\s+(?=[A-Z0-9])",
            text,
        )

        return [
            sentence.strip()
            for sentence in sentences
            if len(sentence.strip()) >= 35
        ]

    # ------------------------------------------------------------------
    # Claim quality scoring
    # ------------------------------------------------------------------

    @classmethod
    def _claim_quality_score(
        cls,
        sentence: str,
    ) -> float:
        """Score how useful a sentence is as a research claim."""

        lowered = sentence.lower()
        words = cls._keywords(sentence)

        if not words:
            return 0.0

        word_counts = Counter(words)
        word_set = set(word_counts)

        research_matches = (
            word_set & cls.RESEARCH_KEYWORDS
        )

        high_value_matches = (
            word_set & cls.HIGH_VALUE_RESEARCH_KEYWORDS
        )

        low_value_matches = (
            word_set & cls.LOW_VALUE_CONTENT_KEYWORDS
        )

        metadata_matches = (
            word_set & cls.METADATA_KEYWORDS
        )

        score = 50.0

        score += min(
            len(research_matches) * 8,
            40,
        )

        score += min(
            len(high_value_matches) * 10,
            50,
        )

        score -= min(
            len(low_value_matches) * 12,
            48,
        )

        score -= min(
            len(metadata_matches) * 15,
            60,
        )

        if len(word_counts) >= 8:
            score += 5

        if len(word_counts) >= 12:
            score += 5

        metadata_patterns = (
            "copyright",
            "creative commons",
            "open-access article",
            "pmcid:",
            "pmid:",
            "doi:",
            "license",
            "licence",
            "terms of use",
            "permission",
            "reproduction",
            "distribution",
            "author(s)",
            "department",
            "affiliation",
        )

        for pattern in metadata_patterns:
            if pattern in lowered:
                score -= 30

        # Quantitative evidence is highly valuable.
        if re.search(
            r"\b\d+(?:\.\d+)?\s*%",
            sentence,
        ):
            score += 12

        if re.search(
            r"\b\d+(?:\.\d+)?\b",
            sentence,
        ):
            score += 5

        research_patterns = (
            r"\bstudy\b",
            r"\bstudies\b",
            r"\bresearch\b",
            r"\btrial\b",
            r"\btrials\b",
            r"\bfindings?\b",
            r"\bevidence\b",
            r"\bresults?\b",
            r"\banalysis\b",
            r"\bevaluat(?:e|ed|es|ing)\b",
            r"\bcompared\b",
            r"\bcompar(?:e|ed|ison)\b",
            r"\bdemonstrat(?:e|ed|es|ing)\b",
            r"\breported\b",
            r"\bidentified\b",
            r"\bdetected\b",
            r"\bpredict(?:ed|s|ing)?\b",
            r"\bvalidated\b",
        )

        for pattern in research_patterns:
            if re.search(
                pattern,
                lowered,
            ):
                score += 6

        if len(metadata_matches) >= 2:
            score -= 25

        if 60 <= len(sentence) <= 300:
            score += 5

        return max(score, 0.0)

    # ------------------------------------------------------------------
    # Claim filters
    # ------------------------------------------------------------------

    @staticmethod
    def _is_reference_entry(
        sentence: str,
    ) -> bool:
        """Reject bibliographic/reference-list fragments."""

        lowered = sentence.lower()

        reference_patterns = (
            r"\bs2cid\b",
            r"\bpmcid\b",
            r"\bpmid\b",
            r"\bdoi\s*:",
            r"\bdoi\.org\b",
            r"\bissn\b",
            r"\bhttps?://",
            r"\bwww\.",
            r"\bcitation\b",
            r"\bbibliography\b",
            r"\breferences\b",
            r"\baccessed\s+\w+\s+\d{4}\b",
            r"\bretrieved\s+\d{1,2}\s+\w+\s+\d{4}\b",
            r"\bavailable\s+at\b",
            r"\bretrieved\s+from\b",
            r"\bet al\.\b",
        )

        if any(
            re.search(
                pattern,
                lowered,
            )
            for pattern in reference_patterns
        ):
            return True

        # Typical reference structure:
        # Author, A. A. (2020)...
        if re.search(
            r"^[A-Z][A-Za-z-]+,\s+[A-Z]\.",
            sentence,
        ):
            return True

        # Typical journal citation:
        # Journal Name. 2020;12(3):123-130.
        if re.search(
            r"\b\d{4}\s*;\s*\d+\s*\(\s*\d+\s*\)",
            sentence,
        ):
            return True

        # Reference-like year + page pattern.
        if re.search(
            r"\b\d{4}\s*:\s*\d+(?:-\d+)?\b",
            sentence,
        ):
            return True

        return False

    @staticmethod
    def _is_metadata_sentence(
        sentence: str,
    ) -> bool:
        """Reject obvious publication/license metadata."""

        lowered = sentence.lower()

        metadata_patterns = (
            "creative commons",
            "creativecommons",
            "open-access article",
            "copyright notice",
            "copyright",
            "terms of use",
            "terms and conditions",
            "distribution or reproduction",
            "use, distribution or reproduction",
            "permission is granted",
            "original author",
            "copyright owner",
            "pmcid:",
            "pmid:",
            "doi:",
            "issn:",
            "journal homepage",
            "author information",
            "author contributions",
            "funding information",
            "data availability statement",
            "conflict of interest",
        )

        return any(
            pattern in lowered
            for pattern in metadata_patterns
        )

    @staticmethod
    def _looks_like_claim(
        sentence: str,
    ) -> bool:
        """Determine whether a sentence contains a factual statement."""

        lowered = sentence.lower()

        question_markers = (
            "what is",
            "what are",
            "how does",
            "how do",
            "why does",
            "why do",
            "when did",
            "where is",
            "who is",
        )

        if any(
            lowered.startswith(marker)
            for marker in question_markers
        ):
            return False

        weak_patterns = (
            "click here",
            "read more",
            "subscribe",
            "sign up",
            "cookie",
            "privacy policy",
            "terms of service",
            "all rights reserved",
            "jump to content",
            "table of contents",
            "free encyclopedia",
            "from wikipedia",
            "this article may",
            "this article's style",
            "learn how and when to remove",
            "may incorporate text from",
            "should be removed",
            "hallucinated information",
            "fictitious references",
        )

        if any(
            pattern in lowered
            for pattern in weak_patterns
        ):
            return False

        factual_patterns = (
            r"\bis\b",
            r"\bare\b",
            r"\bwas\b",
            r"\bwere\b",
            r"\bhas\b",
            r"\bhave\b",
            r"\bhad\b",
            r"\bcan\b",
            r"\bcould\b",
            r"\bwill\b",
            r"\bmay\b",
            r"\baccording to\b",
            r"\bresearch\b",
            r"\bstudy\b",
            r"\bpercent\b",
            r"\b%\b",
            r"\bincreased\b",
            r"\bdecreased\b",
            r"\bcontains\b",
            r"\bincludes\b",
            r"\buses\b",
            r"\bused\b",
            r"\bshowed\b",
            r"\bfound\b",
            r"\breported\b",
            r"\bdemonstrated\b",
            r"\bidentified\b",
            r"\bdetected\b",
            r"\bpredicted\b",
        )

        return any(
            re.search(
                pattern,
                lowered,
            )
            for pattern in factual_patterns
        )

    # ------------------------------------------------------------------
    # Claim extraction
    # ------------------------------------------------------------------

    def extract_claims(
        self,
        sources: list[dict[str, Any]],
        max_claims: int = 20,
    ) -> list[dict[str, Any]]:
        """Extract, clean, rank and deduplicate research claims."""

        candidate_claims: list[dict[str, Any]] = []

        boilerplate_patterns = (
            r"\bjump to content\b",
            r"\btable of contents\b",
            r"\bfrom wikipedia\b",
            r"\bfree encyclopedia\b",
            r"\bprivacy policy\b",
            r"\bterms of use\b",
            r"\bcookie policy\b",
            r"\bcookies\b",
            r"\bsubscribe\b",
            r"\bsign in\b",
            r"\blog in\b",
            r"\bcreate account\b",
            r"\bskip to\b",
            r"\bmenu\b",
            r"\bnavigation\b",
            r"\bjavascript\b",
            r"\bshare this\b",
            r"\bfollow us\b",
            r"\bcontact us\b",
            r"\ball rights reserved\b",
            r"\bthis article may\b",
            r"\bthis article's style\b",
            r"\blearn how and when to remove\b",
            r"\bmay incorporate text from\b",
            r"\bshould be removed\b",
            r"\bhallucinated information\b",
            r"\bfictitious references\b",
        )

        artifact_patterns = (
            r"\bjump to\b",
            r"\btable of contents\b",
            r"\bfree encyclopedia\b",
            r"\bfrom wikipedia\b",
            r"\bedit section\b",
            r"\bsee also\b",
            r"\breferences\b$",
            r"\bexternal links\b",
        )

        for source_index, source in enumerate(
            sources
        ):
            if not source.get("success"):
                continue

            text = source.get(
                "text",
                "",
            )

            if not text:
                continue

            sentences = self._split_sentences(
                text
            )

            for sentence in sentences:
                cleaned_sentence = " ".join(
                    sentence.split()
                ).strip()

                if not cleaned_sentence:
                    continue

                cleaned_sentence = re.sub(
                    r"\[\s*\d+\s*\]",
                    "",
                    cleaned_sentence,
                )

                cleaned_sentence = re.sub(
                    r"\[\s*edit\s*\]",
                    "",
                    cleaned_sentence,
                    flags=re.IGNORECASE,
                )

                cleaned_sentence = " ".join(
                    cleaned_sentence.split()
                ).strip()

                if not cleaned_sentence:
                    continue

                lowered_sentence = (
                    cleaned_sentence.lower()
                )

                if any(
                    re.search(
                        pattern,
                        lowered_sentence,
                    )
                    for pattern in boilerplate_patterns
                ):
                    continue

                if any(
                    re.search(
                        pattern,
                        lowered_sentence,
                    )
                    for pattern in artifact_patterns
                ):
                    continue

                if self._is_reference_entry(
                    cleaned_sentence
                ):
                    continue

                if self._is_metadata_sentence(
                    cleaned_sentence
                ):
                    continue

                if len(cleaned_sentence) < 50:
                    continue

                if len(cleaned_sentence) > 500:
                    continue

                if not self._looks_like_claim(
                    cleaned_sentence
                ):
                    continue

                keywords = self._keywords(
                    cleaned_sentence
                )

                if len(keywords) < 3:
                    continue

                citation_terms = {
                    "s2cid",
                    "pmcid",
                    "pmid",
                    "doi",
                    "issn",
                    "citation",
                    "references",
                    "bibliography",
                }

                if citation_terms.intersection(
                    set(keywords)
                ):
                    continue

                quality_score = (
                    self._claim_quality_score(
                        cleaned_sentence
                    )
                )

                if quality_score < 35:
                    continue

                candidate_claims.append(
                    {
                        "claim": cleaned_sentence,
                        "source_index": source_index,
                        "source_title": source.get(
                            "title",
                            "",
                        ),
                        "source_url": source.get(
                            "url",
                            "",
                        ),
                        "source_domain": source.get(
                            "domain",
                            "",
                        ),
                        "keywords": keywords,
                        "quality_score": round(
                            quality_score,
                            2,
                        ),
                    }
                )

        # Rank by quality.
        candidate_claims.sort(
            key=lambda claim: claim[
                "quality_score"
            ],
            reverse=True,
        )

        # Remove duplicate / near-duplicate claims.
        unique_claims: list[dict[str, Any]] = []

        for candidate in candidate_claims:
            duplicate = False

            for existing in unique_claims:
                similarity = self._keyword_overlap(
                    candidate["claim"],
                    existing["claim"],
                )

                if similarity >= 0.85:
                    duplicate = True
                    break

            if not duplicate:
                unique_claims.append(
                    candidate
                )

        candidate_claims = unique_claims

        # Select claims while maintaining source diversity.
        selected_claims: list[dict[str, Any]] = []
        source_counts: Counter[int] = Counter()

        source_limit = max(
            3,
            max_claims // 2,
        )

        for claim in candidate_claims:
            source_index = claim[
                "source_index"
            ]

            if source_counts[
                source_index
            ] >= source_limit:
                continue

            selected_claims.append(
                claim
            )

            source_counts[
                source_index
            ] += 1

            if len(selected_claims) >= max_claims:
                break

        # Fill remaining slots if needed.
        if len(selected_claims) < max_claims:
            selected_ids = {
                id(claim)
                for claim in selected_claims
            }

            for claim in candidate_claims:
                if id(claim) in selected_ids:
                    continue

                selected_claims.append(
                    claim
                )

                if len(selected_claims) >= max_claims:
                    break

        # Assign stable claim IDs.
        final_claims: list[dict[str, Any]] = []

        for index, claim in enumerate(
            selected_claims,
            start=1,
        ):
            final_claims.append(
                {
                    "claim_id": f"claim_{index}",
                    "claim": claim["claim"],
                    "source_index": claim[
                        "source_index"
                    ],
                    "source_title": claim[
                        "source_title"
                    ],
                    "source_url": claim[
                        "source_url"
                    ],
                    "source_domain": claim[
                        "source_domain"
                    ],
                    "keywords": claim[
                        "keywords"
                    ],
                    "quality_score": claim[
                        "quality_score"
                    ],
                }
            )

        self.last_claims = final_claims

        return final_claims

    # ------------------------------------------------------------------
    # Claim similarity
    # ------------------------------------------------------------------

    @classmethod
    def _keyword_overlap(
        cls,
        first_text: str,
        second_text: str,
    ) -> float:
        """Calculate Jaccard similarity between two keyword sets."""

        first = set(
            cls._keywords(first_text)
        )

        second = set(
            cls._keywords(second_text)
        )

        if not first or not second:
            return 0.0

        intersection = first & second
        union = first | second

        return len(intersection) / len(union)

    # ------------------------------------------------------------------
    # Evidence search
    # ------------------------------------------------------------------

    def find_supporting_evidence(
        self,
        claim: str,
        sources: list[dict[str, Any]],
        threshold: float = 0.15,
    ) -> list[dict[str, Any]]:
        """Find source passages that support a claim."""

        evidence: list[dict[str, Any]] = []

        for source_index, source in enumerate(
            sources
        ):
            if not source.get("success"):
                continue

            text = source.get(
                "text",
                "",
            )

            if not text:
                continue

            sentences = self._split_sentences(
                text
            )

            for sentence in sentences:
                score = self._keyword_overlap(
                    claim,
                    sentence,
                )

                if score >= threshold:
                    evidence.append(
                        {
                            "source_index": source_index,
                            "source_title": source.get(
                                "title",
                                "",
                            ),
                            "source_url": source.get(
                                "url",
                                "",
                            ),
                            "source_domain": source.get(
                                "domain",
                                "",
                            ),
                            "evidence": sentence,
                            "relevance_score": round(
                                score * 100,
                                2,
                            ),
                        }
                    )

        evidence.sort(
            key=lambda item: item[
                "relevance_score"
            ],
            reverse=True,
        )

        return evidence

    # ------------------------------------------------------------------
    # Evidence strength
    # ------------------------------------------------------------------

    @staticmethod
    def _evidence_strength(
        evidence_items: list[dict[str, Any]],
    ) -> str:
        """Classify evidence strength."""

        if not evidence_items:
            return "No Evidence"

        scores = [
            item.get(
                "relevance_score",
                0,
            )
            for item in evidence_items
        ]

        strong_matches = [
            score
            for score in scores
            if score >= 50
        ]

        moderate_matches = [
            score
            for score in scores
            if score >= 25
        ]

        if strong_matches:
            return "Strong"

        if len(moderate_matches) >= 2:
            return "Moderate"

        if moderate_matches:
            return "Weak"

        return "Insufficient"

    # ------------------------------------------------------------------
    # Claim-to-evidence mapping
    # ------------------------------------------------------------------

    def build_evidence_map(
        self,
        claims: list[dict[str, Any]],
        sources: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Build evidence mappings for extracted claims."""

        evidence_map: list[dict[str, Any]] = []

        for claim in claims:
            claim_text = claim.get(
                "claim",
                "",
            )

            supporting_evidence = (
                self.find_supporting_evidence(
                    claim_text,
                    sources,
                )
            )

            evidence_map.append(
                {
                    "claim_id": claim.get(
                        "claim_id",
                        "",
                    ),
                    "claim": claim_text,
                    "source_title": claim.get(
                        "source_title",
                        "",
                    ),
                    "source_url": claim.get(
                        "source_url",
                        "",
                    ),
                    "source_domain": claim.get(
                        "source_domain",
                        "",
                    ),
                    "evidence": supporting_evidence,
                    "evidence_strength": (
                        self._evidence_strength(
                            supporting_evidence
                        )
                    ),
                }
            )

        self.last_evidence_map = evidence_map

        return evidence_map

    # ------------------------------------------------------------------
    # Citation records
    # ------------------------------------------------------------------

    @staticmethod
    def build_citations(
        evidence_map: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Build citation records from evidence mappings."""

        citations: list[dict[str, Any]] = []

        for item in evidence_map:
            for evidence in item.get(
                "evidence",
                [],
            ):
                citations.append(
                    {
                        "claim_id": item.get(
                            "claim_id",
                            "",
                        ),
                        "claim": item.get(
                            "claim",
                            "",
                        ),
                        "source_title": evidence.get(
                            "source_title",
                            "",
                        ),
                        "source_url": evidence.get(
                            "source_url",
                            "",
                        ),
                        "source_domain": evidence.get(
                            "source_domain",
                            "",
                        ),
                        "evidence": evidence.get(
                            "evidence",
                            "",
                        ),
                        "relevance_score": evidence.get(
                            "relevance_score",
                            0,
                        ),
                    }
                )

        return citations

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    @staticmethod
    def build_summary(
        evidence_map: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Summarize evidence coverage, not factual verification."""

        total_claims = len(evidence_map)

        strong = sum(
            1 for item in evidence_map
            if item.get("evidence_strength") == "Strong"
        )
        moderate = sum(
            1 for item in evidence_map
            if item.get("evidence_strength") == "Moderate"
        )
        weak = sum(
            1 for item in evidence_map
            if item.get("evidence_strength") == "Weak"
        )
        insufficient = sum(
            1 for item in evidence_map
            if item.get("evidence_strength")
            in {"No Evidence", "Insufficient"}
        )

        evidence_coverage_rate = (
            round((strong + moderate) / total_claims * 100, 2)
            if total_claims else 0.0
        )

        return {
            "total_claims": total_claims,
            "supported_claims": strong + moderate,
            "strong": strong,
            "moderate": moderate,
            "weak": weak,
            "weak_claims": weak,
            "unsupported_claims": insufficient,
            "support_rate": evidence_coverage_rate,
            "evidence_coverage_rate": evidence_coverage_rate,
            "metric_note": (
                "Evidence coverage is based on keyword relevance "
                "between claims and source passages. It does not "
                "establish that claims are independently verified."
            ),
        }

    # ------------------------------------------------------------------
    # Full analysis
    # ------------------------------------------------------------------

    def analyze(
        self,
        sources: list[dict[str, Any]],
        max_claims: int = 20,
    ) -> dict[str, Any]:
        """Run the complete evidence intelligence workflow."""

        claims = self.extract_claims(
            sources,
            max_claims=max_claims,
        )

        evidence_map = self.build_evidence_map(
            claims,
            sources,
        )

        citations = self.build_citations(
            evidence_map
        )

        summary = self.build_summary(
            evidence_map
        )

        return {
            "claims": claims,
            "evidence_map": evidence_map,
            "citations": citations,
            "summary": summary,
        }