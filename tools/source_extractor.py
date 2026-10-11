import re

import requests
from bs4 import BeautifulSoup


class SourceExtractor:
    """Extract readable article text and reject blocked web pages."""

    MIN_CONTENT_LENGTH = 200

    BLOCKED_PATTERNS = [
        r"checking your browser before accessing",
        r"verify you are human",
        r"verify that you are human",
        r"enable javascript and cookies to continue",
        r"access denied",
        r"request blocked",
        r"unusual traffic from your computer network",
        r"complete the security check",
        r"captcha",
        r"temporarily unavailable",
        r"service unavailable",
        r"robot check",
        r"automated requests",
        r"please wait while we verify",
        r"a required part of this site couldn't load",
        r"this may be due to a browser extension",
        r"please check your connection",
    ]

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/153.0.0.0 Safari/537.36"
            )
        }
        self.timeout = 12

    @staticmethod
    def _clean_text(element) -> str:
        if element is None:
            return ""
        text = element.get_text(separator=" ", strip=True)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _remove_noise(soup: BeautifulSoup) -> None:
        for element in soup(
            [
                "script", "style", "nav", "header", "footer",
                "aside", "form", "noscript", "svg", "iframe", "canvas",
            ]
        ):
            element.decompose()

    @classmethod
    def _is_blocked_content(cls, text: str, title: str = "") -> bool:
        combined = f"{title} {text}".lower()

        if any(
            re.search(pattern, combined, flags=re.IGNORECASE)
            for pattern in cls.BLOCKED_PATTERNS
        ):
            return True

        error_phrases = (
            "forbidden",
            "bad gateway",
            "too many requests",
            "rate limit exceeded",
            "you don't have permission to access",
            "you do not have permission to access",
        )

        return len(text) < 1000 and any(
            phrase in combined for phrase in error_phrases
        )

    @staticmethod
    def _find_main_content(soup: BeautifulSoup):
        selectors = [
            "[itemprop='articleBody']",
            "article",
            "main",
            ".article-body",
            ".article-content",
            ".article__body",
            ".article__content",
            ".post-content",
            ".post-body",
            ".entry-content",
            ".content-body",
            ".story-body",
            ".story-content",
            "#article-body",
            "#article-content",
            "#main-content",
            "#content",
        ]

        for selector in selectors:
            for element in soup.select(selector):
                if len(SourceExtractor._clean_text(element)) >= 200:
                    return element

        candidates = soup.find_all(["section", "div", "body"])
        best_element = None
        best_length = 0

        for element in candidates:
            length = len(SourceExtractor._clean_text(element))
            if length > best_length:
                best_element = element
                best_length = length

        return best_element or soup.body or soup

    @staticmethod
    def _clean_article_text(text: str) -> str:
        text = re.sub(r"\[\s*\d+\s*\]", "", text)
        text = re.sub(
            r"\[\s*edit\s*\]", "", text, flags=re.IGNORECASE
        )
        return re.sub(r"\s+", " ", text).strip()

    def extract(self, url: str) -> dict:
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True,
            )
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "").lower()
            if content_type and not any(
                kind in content_type
                for kind in ("text/html", "application/xhtml+xml")
            ):
                return {
                    "url": url,
                    "text": "",
                    "success": False,
                    "error": f"Unsupported content type: {content_type}",
                }

            soup = BeautifulSoup(response.text, "html.parser")
            page_title = (
                soup.title.get_text(" ", strip=True) if soup.title else ""
            )

            self._remove_noise(soup)

            page_text = self._clean_text(soup)
            if self._is_blocked_content(page_text, page_title):
                return {
                    "url": url,
                    "text": "",
                    "success": False,
                    "error": (
                        "Page contains browser verification or "
                        "access-block content."
                    ),
                }

            content = self._find_main_content(soup)
            text = self._clean_article_text(self._clean_text(content))

            if self._is_blocked_content(text, page_title):
                return {
                    "url": url,
                    "text": "",
                    "success": False,
                    "error": "Extracted content appears to be an access-block page.",
                }

            if len(text) < self.MIN_CONTENT_LENGTH:
                return {
                    "url": url,
                    "text": "",
                    "success": False,
                    "error": f"Insufficient article content: {len(text)} characters.",
                }

            return {"url": url, "text": text, "success": True}

        except requests.exceptions.Timeout:
            return {
                "url": url,
                "text": "",
                "success": False,
                "error": "Request timed out.",
            }

        except requests.exceptions.ConnectionError:
            return {
                "url": url,
                "text": "",
                "success": False,
                "error": "Connection failed.",
            }

        except requests.exceptions.HTTPError as error:
            return {
                "url": url,
                "text": "",
                "success": False,
                "error": f"HTTP error: {error}",
            }

        except requests.RequestException as error:
            return {
                "url": url,
                "text": "",
                "success": False,
                "error": str(error),
            }

        except Exception as error:
            return {
                "url": url,
                "text": "",
                "success": False,
                "error": f"Unexpected extraction error: {error}",
            }