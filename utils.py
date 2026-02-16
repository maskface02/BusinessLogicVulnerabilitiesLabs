import requests
from bs4 import BeautifulSoup

def get_csrf_token(session: requests.Session, url: str) -> str:
    r = session.get(url, verify=False)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    csrf_input = soup.find("input", {"name": "csrf"})
    if not csrf_input or not csrf_input.get("value"):
        raise RuntimeError(f"Could not find CSRF token on: {url}")

    return csrf_input["value"]


