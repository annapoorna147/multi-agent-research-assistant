from __future__ import annotations

import re
from typing import Any


class ContradictionDetector:
    """
    Detect agreement, disagreement, and uncertainty
    between research claims from different sources.
    """

    NEGATION_WORDS = {
        "not",
        "no",
        "never",
        "none",
        "without",
        "cannot",
        "can't",
        "doesn't",
        "doesnt",
        "isn't",
        "isnt",
        "aren't",
        "arent",
        "won't",
        "wont",
        "false",
        "incorrect",
        "unlikely",
        "impossible",
    }

    UNCERTAINTY_WORDS = {
        "may",
        "might",
        "could",
        "possibly",
        "potentially",
        "uncertain",
        "unclear",
        "suggests",
        "suggest",
        "likely",
        "unlikely",
        "possibly",
    }

    CONTRADICTION_PATTERNS = [
        (r"\bis\b", r"\bis not\b"),
        (r"\bare\b", r"\bare not\b"),
        (r"\bcan\b", r"\bcannot\b"),
        (r"\bdoes\b", r"\bdoes not\b"),
        (r"\bwill\b", r"\bwill not\b"),
        (r"\btrue\b", r"\bfalse\b"),
        (r"\bsupports\b", r"\bcontradicts\b"),
        (r"\bpositive\b", r"\bnegative\b"),
        (r"\bincreases\b", r"\bdecreases\b"),
        (r"\bincrease\b", r"\bdecrease\b"),
        (r"\bhigher\b", r"\blower\b"),
        (r"\bmore\b", r"\bless\b"),
    ]

    # ---------------------------------------------------------
    # Text helpers
    # ---------------------------------------------------------

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize text for comparison."""

        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    @classmethod
    def _tokens(cls, text: str) -> set[str]:
        """Return normalized word tokens."""

        normalized = cls._normalize(text)

        return {
            token
            for token in normalized.split()
            if len(token) > 2
        }

    @classmethod
    def _has_negation(cls, text: str) -> bool:
        """Check whether a statement contains negation."""

        tokens = set(cls._normalize(text).split())

        return bool(tokens.intersection(cls.NEGATION_WORDS))

    @classmethod
    def _has_uncertainty(cls, text: str) -> bool:
        """Check whether a statement contains uncertainty."""

        tokens = set(cls._normalize(text).split())

        return bool(tokens.intersection(cls.UNCERTAINTY_WORDS))

    # ---------------------------------------------------------
    # Similarity
    # ---------------------------------------------------------

    @classmethod
    def _similarity(
        cls,
        first: str,
        second: str,
    ) -> float:
        """
        Calculate Jaccard similarity between two statements.
        """

        first_tokens = cls._tokens(first)
        second_tokens = cls._tokens(second)

        if not first_tokens or not second_tokens:
            return 0.0

        intersection = first_tokens.intersection(second_tokens)
        union = first_tokens.union(second_tokens)

        return round(
            (len(intersection) / len(union)) * 100,
            2,
        )

    # ---------------------------------------------------------
    # Contradiction detection
    # ---------------------------------------------------------

    @classmethod
    def _has_pattern_contradiction(
        cls,
        first: str,
        second: str,
    ) -> bool:
        """Detect common opposing language patterns."""

        first_normalized = cls._normalize(first)
        second_normalized = cls._normalize(second)

        for positive_pattern, negative_pattern in cls.CONTRADICTION_PATTERNS:
            first_positive = re.search(
                positive_pattern,
                first_normalized,
            )

            first_negative = re.search(
                negative_pattern,
                first_normalized,
            )

            second_positive = re.search(
                positive_pattern,
                second_normalized,
            )

            second_negative = re.search(
                negative_pattern,
                second_normalized,
            )

            if (
                first_positive
                and second_negative
            ) or (
                first_negative
                and second_positive
            ):
                return True

        return False

    @classmethod
    def compare_claims(
        cls,
        first_claim: str,
        second_claim: str,
    ) -> dict[str, Any]:
        """
        Compare two claims and classify their relationship.
        """

        similarity = cls._similarity(
            first_claim,
            second_claim,
        )

        first_negated = cls._has_negation(first_claim)
        second_negated = cls._has_negation(second_claim)

        pattern_contradiction = cls._has_pattern_contradiction(
            first_claim,
            second_claim,
        )

        if (
            similarity >= 35
            and (
                pattern_contradiction
                or first_negated != second_negated
            )
        ):
            relationship = "Contradiction"

        elif similarity >= 35:
            if (
                cls._has_uncertainty(first_claim)
                or cls._has_uncertainty(second_claim)
            ):
                relationship = "Uncertainty"

            else:
                relationship = "Agreement"

        else:
            relationship = "Unrelated"

        return {
            "first_claim": first_claim,
            "second_claim": second_claim,
            "similarity": similarity,
            "relationship": relationship,
        }

    # ---------------------------------------------------------
    # Source-level analysis
    # ---------------------------------------------------------

    def analyze(
        self,
        claims: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Compare claims and produce a contradiction report.

        Expected claim format:

        {
            "claim_id": "claim_1",
            "claim": "...",
            "source_domain": "example.com"
        }
        """

        comparisons = []

        agreements = []
        contradictions = []
        uncertainties = []

        for index, first in enumerate(claims):
            for second in claims[index + 1:]:
                if (
                    first.get("source_domain")
                    == second.get("source_domain")
                ):
                    continue

                comparison = self.compare_claims(
                    first.get("claim", ""),
                    second.get("claim", ""),
                )

                comparison["first_claim_id"] = first.get(
                    "claim_id"
                )

                comparison["second_claim_id"] = second.get(
                    "claim_id"
                )

                comparison["first_source"] = first.get(
                    "source_domain"
                )

                comparison["second_source"] = second.get(
                    "source_domain"
                )

                comparisons.append(comparison)

                relationship = comparison["relationship"]

                if relationship == "Agreement":
                    agreements.append(comparison)

                elif relationship == "Contradiction":
                    contradictions.append(comparison)

                elif relationship == "Uncertainty":
                    uncertainties.append(comparison)

        if contradictions:
            overall_status = "Contradictions Detected"

        elif uncertainties:
            overall_status = "Uncertainty Detected"

        elif agreements:
            overall_status = "Sources Generally Agree"

        else:
            overall_status = "No Strong Relationship Detected"

        return {
            "comparisons": comparisons,
            "agreements": agreements,
            "contradictions": contradictions,
            "uncertainties": uncertainties,
            "summary": {
                "total_comparisons": len(comparisons),
                "agreements": len(agreements),
                "contradictions": len(contradictions),
                "uncertainties": len(uncertainties),
                "overall_status": overall_status,
            },
        }