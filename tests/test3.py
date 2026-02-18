#!/usr/bin/env python3
import sys
import re
import requests
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

POPUP_RE = re.compile(r'Use coupon\s+([A-Z0-9_-]{3,40})\s+at checkout!?', re.I)

def extract_coupon(html: str) -> str | None:
    # 1) visible text (if modal is in DOM)
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    m = POPUP_RE.search(text)
    if m:
        return m.group(1)

    # 2) raw HTML (if coupon is inside <script> / alert() / JS)
    m = POPUP_RE.search(html)
    if m:
        return m.group(1)

    return None

def get_signup_form_data(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form", attrs={"action": "/sign-up"})
    if not form:
        raise RuntimeError("Couldn't find sign-up form (action=/sign-up).")

    csrf_inp = form.find("input", attrs={"name": "csrf"})
    if not csrf_inp or not csrf_inp.get("value"):
        raise RuntimeError("Couldn't find CSRF token in sign-up form.")

    email_inp = form.find("input", attrs={"type": "email"})
    if not email_inp or not email_inp.get("name"):
        raise RuntimeError("Couldn't find email input (type=email) or its name attribute.")

    return csrf_inp["value"], email_inp["name"]  # email name is "email/" in your HTML

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <base_url> [email]")
        sys.exit(1)

    base_url = sys.argv[1].rstrip("/")
    email = "test@example.com"

    with requests.Session() as s:
        # 1) GET homepage (contains the form)
        home = s.get(base_url + "/", verify=False, timeout=15)
        home.raise_for_status()

        csrf, email_field_name = get_signup_form_data(home.text)

        # 2) POST to /sign-up
        signup_url = urljoin(base_url + "/", "/sign-up")
        post = s.post(
            signup_url,
            data={"csrf": csrf, email_field_name: email},
            verify=False,
            timeout=15,
            allow_redirects=True,
        )
        post.raise_for_status()

        # 3) Try extract coupon from POST response
        coupon = extract_coupon(post.text)

        # 4) If not found, GET confirmed page and try again
        if not coupon:
            confirm_url = urljoin(base_url + "/", "/?sign-up-confirmed=true")
            confirm = s.get(confirm_url, verify=False, timeout=15)
            confirm.raise_for_status()
            coupon = extract_coupon(confirm.text)

        if not coupon:
            print("FAIL: No coupon found.")
            print("POST ended at:", post.url)
            # Helpful snippet debug:
            hay = (post.text + "\n" + (confirm.text if 'confirm' in locals() else "")).lower()
            idx = hay.find("use coupon")
            if idx != -1:
                snippet = (post.text + "\n" + (confirm.text if 'confirm' in locals() else ""))[max(0, idx-200):idx+200]
                print("Snippet around 'Use coupon':")
                print(snippet)
            sys.exit(2)

        print("PASS: Coupon =", coupon)

if __name__ == "__main__":
    main()

