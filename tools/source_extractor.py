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

    def extract(self, url):
        """Fetch a URL and extract its main text content."""

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=20,
            )

            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove elements that usually do not contain article content.
            for element in soup(
                ["script", "style", "nav", "header", "footer", "aside"]
            ):
                element.decompose()

            text = soup.get_text(separator=" ", strip=True)

            # Clean excessive whitespace.
            text = " ".join(text.split())

            return {
                "url": url,
                "text": text,
                "success": True,
            }

        except requests.RequestException as error:
            return {
                "url": url,
                "text": "",
                "success": False,
                "error": str(error),
            }