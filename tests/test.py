import re
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EMAIL_RE = re.compile(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}')

def extract_email_from_html(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    for h4 in soup.find_all("h4"):
        text = h4.get_text(" ", strip=True)
        if "Your email address is" in text:
            m = EMAIL_RE.search(text)
            return m.group(0) if m else None
    return None

def test_extract_email_from_url(url: str) -> None:
    with requests.Session() as s:
        r = s.get(url, verify=False, timeout=15)
        r.raise_for_status()

    email = extract_email_from_html(r.text)

    # "test" assertion
    assert email is not None, f"FAIL: No email found on {url}"
    print("PASS:", email)

if __name__ == "__main__":
    url = input("Url: ").strip()
    test_extract_email_from_url(url)

