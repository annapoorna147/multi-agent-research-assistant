import re
from urllib.parse import urlparse


class SourceIntelligence:
    """Evaluate, score, rank, and recommend research sources."""

    SOURCE_TYPES = {
        "academic": [
            "edu",
            "arxiv.org",
            "researchgate.net",
            "sciencedirect.com",
            "springer.com",
            "nature.com",
            "ieee.org",
            "acm.org",
            "pubmed.ncbi.nlm.nih.gov",
        ],
        "government": [
            "gov.in",
            "gov",
            "nasa.gov",
            "who.int",
            "un.org",
        ],
        "news": [
            "reuters.com",
            "apnews.com",
            "bbc.com",
            "bbc.co.uk",
            "nytimes.com",
            "theguardian.com",
        ],
        "technology": [
            "ibm.com",
            "microsoft.com",
            "google.com",
            "developer.apple.com",
            "aws.amazon.com",
            "nvidia.com",
        ],
        "business": [
            "forbes.com",
            "bloomberg.com",
            "statista.com",
            "mckinsey.com",
            "deloitte.com",
            "pwc.com",
        ],
    }

    def detect_research_intent(self, query):
        """Detect the primary research intent from the question."""

        text = query.lower()

        if any(
            phrase in text
            for phrase in [
                "research",
                "research paper",
                "study",
                "studies",
                "paper",
                "scientific",
                "experiment",
                "theory",
                "methodology",
                "academic",
                "journal",
                "hypothesis",
                "findings",
            ]
        ):
            return "academic"

        if any(
            phrase in text
            for phrase in [
                "government",
                "policy",
                "law",
                "regulation",
                "regulations",
                "act",
                "scheme",
                "official",
                "government policy",
            ]
        ):
            return "government"

        if any(
            phrase in text
            for phrase in [
                "market",
                "market size",
                "market share",
                "industry",
                "revenue",
                "growth",
                "forecast",
                "company",
                "business",
                "profit",
                "investment",
            ]
        ):
            return "business"

        if any(
            phrase in text
            for phrase in [
                "latest",
                "today",
                "yesterday",
                "news",
                "breaking",
                "current events",
                "current news",
            ]
        ):
            return "news"

        if any(
            phrase in text
            for phrase in [
                "technology",
                "technical",
                "software",
                "hardware",
                "algorithm",
                "programming",
                "architecture",
                "computer",
                "computing",
                "artificial intelligence",
                "machine learning",
                "deep learning",
                "how does",
                "how do",
                "how is",
            ]
        ):
            return "technology"

        return "general"

    def analyze_source(self, source, query):
        """Analyze one source and return intelligence metadata."""

        url = source.get("url", "")
        title = source.get("title", "")
        snippet = source.get("snippet", "")

        domain = self._extract_domain(url)

        source_type = self._classify_source(domain)

        research_intent = self.detect_research_intent(query)

        authority_score = self._authority_score(
            domain,
            source_type,
        )

        relevance_score = self._relevance_score(
            query,
            title,
            snippet,
        )

        evidence_score = self._evidence_score(
            title,
            snippet,
        )

        source_type_score = self._source_type_score(
            source_type,
            research_intent,
        )

        recency_score = self._recency_score(
            title,
            snippet,
        )

        accessibility_score = self._accessibility_score(
            source
        )

        overall_score = round(
            (
                relevance_score * 0.35
                + authority_score * 0.25
                + evidence_score * 0.20
                + source_type_score * 0.10
                + recency_score * 0.05
                + accessibility_score * 0.05
            ),
            2,
        )

        return {
            **source,
            "domain": domain,
            "source_type": source_type,
            "research_intent": research_intent,
            "authority_score": authority_score,
            "relevance_score": relevance_score,
            "evidence_score": evidence_score,
            "source_type_score": source_type_score,
            "recency_score": recency_score,
            "accessibility_score": accessibility_score,
            "overall_score": overall_score,
            "recommendation": self._recommendation(
                overall_score
            ),
        }

    def rank_sources(self, sources, query):
        """Remove duplicates, score sources, and rank them."""

        unique_sources = self._remove_duplicates(
            sources
        )

        analyzed_sources = [
            self.analyze_source(
                source,
                query,
            )
            for source in unique_sources
        ]

        analyzed_sources.sort(
            key=lambda source: (
                source["overall_score"],
                source["accessibility_score"],
            ),
            reverse=True,
        )

        for index, source in enumerate(
            analyzed_sources,
            start=1,
        ):
            source["rank"] = index

        return analyzed_sources

    def get_best_sources(self, ranked_sources, limit=3):
        """
        Return the strongest accessible sources.

        Best Sources are selected from successfully retrieved
        sources and prioritize stronger recommendations.

        A domain can appear only once in the final Best Sources
        list so that the user receives a diverse set of sources.
        """

        accessible_sources = [
            source
            for source in ranked_sources
            if source.get("success") is True
        ]

        if not accessible_sources:
            return []

        recommended_sources = [
            source
            for source in accessible_sources
            if source.get("recommendation")
            in [
                "Highly Recommended",
                "Recommended",
            ]
        ]

        useful_sources = [
            source
            for source in accessible_sources
            if source.get("recommendation") == "Useful"
        ]

        low_priority_sources = [
            source
            for source in accessible_sources
            if source.get("recommendation") == "Low Priority"
        ]

        ordered_sources = (
            recommended_sources
            + useful_sources
            + low_priority_sources
        )

        best_sources = []
        seen_domains = set()

        for source in ordered_sources:
            domain = source.get(
                "domain",
                "",
            ).lower().strip()

            if not domain:
                continue

            if domain in seen_domains:
                continue

            seen_domains.add(domain)
            best_sources.append(source)

            if len(best_sources) >= limit:
                break

        return best_sources

    def _extract_domain(self, url):
        """Extract the clean domain from a URL."""

        try:
            domain = urlparse(url).netloc.lower()

            return domain.removeprefix("www.")

        except Exception:
            return ""

    def _classify_source(self, domain):
        """Classify a source based on its domain."""

        # Government domains.
        if (
            domain == "gov"
            or domain.startswith("gov.")
            or ".gov." in domain
            or domain.endswith(".gov")
        ):
            return "government"

        # Academic domains.
        if (
            domain.endswith(".edu")
            or domain == "edu"
        ):
            return "academic"

        # Known source types.
        for source_type, domains in self.SOURCE_TYPES.items():

            if source_type == "government":
                continue

            for pattern in domains:

                if (
                    domain == pattern
                    or domain.endswith("." + pattern)
                ):
                    return source_type

        return "general"

    def _authority_score(
        self,
        domain,
        source_type,
    ):
        """Estimate source authority."""

        authority = {
            "academic": 95,
            "government": 95,
            "news": 85,
            "technology": 80,
            "business": 82,
            "general": 55,
        }

        score = authority.get(
            source_type,
            55,
        )

        if domain.endswith(".org"):
            score = max(score, 70)

        return score

    def _relevance_score(
        self,
        query,
        title,
        snippet,
    ):
        """Estimate relevance using query term overlap."""

        query_words = self._keywords(query)

        source_text = self._keywords(
            f"{title} {snippet}"
        )

        if not query_words:
            return 0

        matches = sum(
            1
            for word in query_words
            if word in source_text
        )

        return round(
            min(
                100,
                (matches / len(query_words)) * 100,
            ),
            2,
        )

    def _evidence_score(
        self,
        title,
        snippet,
    ):
        """Estimate whether the source contains evidence."""

        text = f"{title} {snippet}".lower()

        evidence_terms = [
            "study",
            "research",
            "data",
            "analysis",
            "report",
            "survey",
            "experiment",
            "findings",
            "statistics",
            "evidence",
            "paper",
            "results",
            "dataset",
            "method",
            "source",
            "official",
        ]

        matches = sum(
            1
            for term in evidence_terms
            if term in text
        )

        return min(
            100,
            50 + matches * 8,
        )

    def _source_type_score(
        self,
        source_type,
        research_intent,
    ):
        """Score source type according to research intent."""

        preferences = {
            "academic": {
                "academic": 100,
                "government": 85,
                "technology": 75,
                "business": 70,
                "news": 65,
                "general": 45,
            },
            "technology": {
                "technology": 100,
                "academic": 92,
                "government": 80,
                "business": 72,
                "news": 65,
                "general": 45,
            },
            "business": {
                "business": 100,
                "government": 95,
                "academic": 90,
                "news": 85,
                "technology": 78,
                "general": 50,
            },
            "news": {
                "news": 100,
                "government": 90,
                "technology": 78,
                "academic": 70,
                "business": 68,
                "general": 45,
            },
            "government": {
                "government": 100,
                "academic": 85,
                "news": 80,
                "technology": 70,
                "business": 65,
                "general": 45,
            },
            "general": {
                "academic": 90,
                "government": 90,
                "technology": 85,
                "business": 75,
                "news": 80,
                "general": 55,
            },
        }

        intent_preferences = preferences.get(
            research_intent,
            preferences["general"],
        )

        return intent_preferences.get(
            source_type,
            50,
        )

    def _recency_score(
        self,
        title,
        snippet,
    ):
        """Estimate recency signals from source text."""

        text = f"{title} {snippet}".lower()

        recent_terms = [
            "2026",
            "2025",
            "2024",
            "latest",
            "recent",
            "updated",
            "new",
            "current",
            "today",
        ]

        matches = sum(
            1
            for term in recent_terms
            if term in text
        )

        return min(
            100,
            50 + matches * 10,
        )

    def _accessibility_score(self, source):
        """
        Score whether the source content was successfully
        retrieved.

        Successfully extracted sources receive the highest
        accessibility score because they can actually be used
        for fact checking and analysis.
        """

        if source.get("success") is True:
            return 100

        return 20

    def _recommendation(self, score):
        """Convert a numerical score into a recommendation."""

        if score >= 85:
            return "Highly Recommended"

        if score >= 70:
            return "Recommended"

        if score >= 55:
            return "Useful"

        return "Low Priority"

    def _remove_duplicates(self, sources):
        """Remove duplicate URLs while preserving order."""

        seen = set()

        unique_sources = []

        for source in sources:

            url = source.get(
                "url",
                "",
            ).strip()

            if not url:
                continue

            normalized_url = self._normalize_url(url)

            if normalized_url in seen:
                continue

            seen.add(normalized_url)

            unique_sources.append(source)

        return unique_sources

    def _normalize_url(self, url):
        """
        Normalize a URL so common variations of the same
        source are treated as duplicates.
        """

        try:
            parsed = urlparse(
                url.strip().lower()
            )

            scheme = parsed.scheme or "https"

            domain = parsed.netloc.removeprefix(
                "www."
            )

            path = parsed.path.rstrip("/")

            # Remove common tracking parameters.
            query = parsed.query

            if query:
                query_parts = []

                for parameter in query.split("&"):
                    key = parameter.split(
                        "=",
                        1,
                    )[0].lower()

                    if key.startswith("utm_"):
                        continue

                    if key in {
                        "ref",
                        "source",
                        "campaign",
                    }:
                        continue

                    query_parts.append(
                        parameter
                    )

                query = "&".join(
                    query_parts
                )

            normalized = (
                f"{scheme}://{domain}{path}"
            )

            if query:
                normalized += f"?{query}"

            return normalized

        except Exception:
            return url.rstrip("/").lower()

    def _keywords(self, text):
        """Convert text into normalized keyword tokens."""

        words = re.findall(
            r"[a-zA-Z0-9]+",
            text.lower(),
        )

        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "of",
            "to",
            "in",
            "on",
            "for",
            "with",
            "how",
            "what",
            "is",
            "are",
            "will",
            "be",
            "does",
            "do",
            "can",
            "why",
            "which",
            "this",
            "that",
        }

        return {
            word
            for word in words
            if word not in stop_words
            and len(word) > 2
        }