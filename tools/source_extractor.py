import requests
from bs4 import BeautifulSoup


class SourceExtractor:
    """Extract readable text from web pages."""

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/153.0.0.0 Safari/537.36"
            )
        }

        self.timeout = 8

    def extract(self, url):
        """Fetch a URL and extract its main text content."""

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True,
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser",
            )

            # Remove elements that usually do not contain
            # useful article content.
            for element in soup(
                [
                    "script",
                    "style",
                    "nav",
                    "header",
                    "footer",
                    "aside",
                    "form",
                    "noscript",
                ]
            ):
                element.decompose()

            text = soup.get_text(
                separator=" ",
                strip=True,
            )

            # Clean excessive whitespace.
            text = " ".join(
                text.split()
            )

            # Detect pages that returned no meaningful text.
            if not text:
                return {
                    "url": url,
                    "text": "",
                    "success": False,
                    "error": "No readable text found on page.",
                }

            return {
                "url": url,
                "text": text,
                "success": True,
            }

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