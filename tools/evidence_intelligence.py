"""
Evidence Intelligence Engine

Day 3 of Multi-Agent Research Assistant V2.

Responsibilities:
- Extract meaningful claims from source content.
- Find supporting evidence for each claim.
- Map claims to their strongest sources.
- Calculate evidence strength.
- Keep source attribution attached to every claim.
- Prepare structured evidence data for fact checking and citation generation.
"""

from __future__ import annotations

import re
from typing import Any


class EvidenceIntelligence:
    """Build claim-to-evidence mappings from research sources."""

    STOPWORDS = {
        "about",
        "after",
        "again",
        "against",
        "also",
        "because",
        "been",
        "being",
        "between",
        "could",
        "does",
        "doesn",
        "from",
        "have",
        "having",
        "into",
        "more",
        "most",
        "other",
        "over",
        "same",
        "should",
        "some",
        "such",
        "than",
        "that",
        "their",
        "there",
        "these",
        "they",
        "this",
        "those",
        "through",
        "under",
        "were",
        "which",
        "while",
        "with",
        "would",
        "your",
        "what",
        "when",
        "where",
        "will",
        "does",
        "using",
        "used",
        "uses",
        "based",
        "many",
        "much",
        "only",
        "very",
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

        sentences = re.split(
            r"(?<=[.!?])\s+(?=[A-Z0-9])",
            text,
        )

        cleaned = []

        for sentence in sentences:
            sentence = sentence.strip()

            if len(sentence) < 35:
                continue

            cleaned.append(sentence)

        return cleaned

    # ------------------------------------------------------------------
    # Claim extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _looks_like_claim(sentence: str) -> bool:
        """
        Determine whether a sentence contains a potentially
        research-worthy factual statement.
        """

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
        )

        return any(
            re.search(pattern, lowered)
            for pattern in factual_patterns
        )

    def extract_claims(
        self,
        sources: list[dict[str, Any]],
        max_claims: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Extract candidate factual claims from accessible sources.

        Each claim retains its originating source so attribution
        is never lost.
        """

        claims: list[dict[str, Any]] = []

        for source_index, source in enumerate(sources):
            if not source.get("success"):
                continue

            text = source.get("text", "")

            if not text:
                continue

            sentences = self._split_sentences(text)

            for sentence in sentences:
                if not self._looks_like_claim(sentence):
                    continue

                keywords = self._keywords(sentence)

                if len(keywords) < 3:
                    continue

                claim = {
                    "claim_id": f"claim_{len(claims) + 1}",
                    "claim": sentence,
                    "source_index": source_index,
                    "source_title": source.get("title", ""),
                    "source_url": source.get("url", ""),
                    "source_domain": source.get("domain", ""),
                    "keywords": keywords,
                }

                claims.append(claim)

                if len(claims) >= max_claims:
                    self.last_claims = claims
                    return claims

        self.last_claims = claims

        return claims

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

        first = set(cls._keywords(first_text))
        second = set(cls._keywords(second_text))

        if not first or not second:
            return 0.0

        intersection = first.intersection(second)
        union = first.union(second)

        return len(intersection) / len(union)

    # ------------------------------------------------------------------
    # Evidence extraction
    # ------------------------------------------------------------------

    def find_evidence(
        self,
        claim: dict[str, Any],
        sources: list[dict[str, Any]],
        max_evidence_per_source: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Find sentences from sources that are most relevant to a claim.
        """

        claim_text = claim.get("claim", "")

        candidates: list[dict[str, Any]] = []

        for source_index, source in enumerate(sources):
            if not source.get("success"):
                continue

            text = source.get("text", "")

            if not text:
                continue

            sentences = self._split_sentences(text)

            source_candidates = []

            for sentence in sentences:
                overlap = self._keyword_overlap(
                    claim_text,
                    sentence,
                )

                if overlap <= 0:
                    continue

                source_candidates.append(
                    {
                        "evidence": sentence,
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
                        "relevance_score": round(
                            overlap * 100,
                            2,
                        ),
                    }
                )

            source_candidates.sort(
                key=lambda item: item["relevance_score"],
                reverse=True,
            )

            candidates.extend(
                source_candidates[
                    :max_evidence_per_source
                ]
            )

        candidates.sort(
            key=lambda item: item["relevance_score"],
            reverse=True,
        )

        return candidates

    # ------------------------------------------------------------------
    # Evidence strength
    # ------------------------------------------------------------------

    @staticmethod
    def _evidence_strength(
        evidence_items: list[dict[str, Any]],
    ) -> str:
        """
        Convert evidence relevance and source diversity
        into an evidence-strength label.

        A direct/high-overlap match is strong evidence by itself.
        Multiple reasonably relevant pieces of evidence provide
        moderate support.
        """

        if not evidence_items:
            return "No Evidence"

        scores = [
            item.get("relevance_score", 0)
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

        # A direct/high-overlap match is strong evidence by itself.
        if strong_matches:
            return "Strong"

        # Multiple reasonably relevant pieces of evidence
        # provide moderate support.
        if len(moderate_matches) >= 2:
            return "Moderate"

        # One meaningful but weaker match.
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
        """
        Build the complete claim → evidence → source mapping.
        """

        evidence_map: list[dict[str, Any]] = []

        for claim in claims:
            evidence = self.find_evidence(
                claim,
                sources,
            )

            strength = self._evidence_strength(
                evidence,
            )

            source_domains = []

            for item in evidence:
                domain = item.get(
                    "source_domain",
                    "",
                ).strip()

                if (
                    domain
                    and domain not in source_domains
                ):
                    source_domains.append(domain)

            evidence_map.append(
                {
                    "claim_id": claim.get(
                        "claim_id"
                    ),
                    "claim": claim.get(
                        "claim"
                    ),
                    "evidence_strength": strength,
                    "evidence": evidence,
                    "supporting_sources": source_domains,
                    "source_count": len(
                        source_domains
                    ),
                }
            )

        self.last_evidence_map = evidence_map

        return evidence_map

    # ------------------------------------------------------------------
    # Citation records
    # ------------------------------------------------------------------

    @staticmethod
    def build_citation(
        evidence_item: dict[str, Any],
        citation_number: int,
    ) -> dict[str, Any]:
        """Create a normalized citation record."""

        return {
            "citation_id": (
                f"citation_{citation_number}"
            ),
            "source_title": evidence_item.get(
                "source_title",
                "",
            ),
            "source_url": evidence_item.get(
                "source_url",
                "",
            ),
            "source_domain": evidence_item.get(
                "source_domain",
                "",
            ),
            "evidence": evidence_item.get(
                "evidence",
                "",
            ),
        }

    def build_citations(
        self,
        evidence_map: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Build unique citation records from the evidence map.
        """

        citations: list[dict[str, Any]] = []
        seen_urls: set[str] = set()

        for item in evidence_map:
            for evidence in item.get(
                "evidence",
                [],
            ):
                url = evidence.get(
                    "source_url",
                    "",
                ).strip()

                if not url or url in seen_urls:
                    continue

                seen_urls.add(url)

                citations.append(
                    self.build_citation(
                        evidence,
                        len(citations) + 1,
                    )
                )

        return citations

    # ------------------------------------------------------------------
    # Summary helpers
    # ------------------------------------------------------------------

    @staticmethod
    def summarize_evidence(
        evidence_map: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Return high-level evidence statistics."""

        total_claims = len(evidence_map)

        supported = sum(
            1
            for item in evidence_map
            if item.get("evidence_strength")
            in {
                "Strong",
                "Moderate",
            }
        )

        weak = sum(
            1
            for item in evidence_map
            if item.get("evidence_strength")
            == "Weak"
        )

        unsupported = sum(
            1
            for item in evidence_map
            if item.get("evidence_strength")
            in {
                "No Evidence",
                "Insufficient",
            }
        )

        return {
            "total_claims": total_claims,
            "supported_claims": supported,
            "weak_claims": weak,
            "unsupported_claims": unsupported,
            "support_rate": round(
                (supported / total_claims) * 100,
                2,
            )
            if total_claims
            else 0.0,
        }

    # ------------------------------------------------------------------
    # Full Day 3 workflow
    # ------------------------------------------------------------------

    def analyze(
        self,
        sources: list[dict[str, Any]],
        max_claims: int = 20,
    ) -> dict[str, Any]:
        """
        Run the complete evidence-intelligence workflow.
        """

        claims = self.extract_claims(
            sources,
            max_claims=max_claims,
        )

        evidence_map = self.build_evidence_map(
            claims,
            sources,
        )

        citations = self.build_citations(
            evidence_map,
        )

        summary = self.summarize_evidence(
            evidence_map,
        )

        return {
            "claims": claims,
            "evidence_map": evidence_map,
            "citations": citations,
            "summary": summary,
        }