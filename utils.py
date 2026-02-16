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

def login(session: requests.Session, login_url: str, username: str, password: str):
    csrf_token = get_csrf_token(session, login_url)
    response = session.post(login_url, data={"csrf": csrf_token, "username": username, "password": password}, verify=False)
    response.raise_for_status()
    if "my-account" not in response.url:
        raise RuntimeError("(-) Login failed")
