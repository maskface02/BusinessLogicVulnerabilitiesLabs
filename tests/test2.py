import requests
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_latest_verification_link(session: requests.Session, mail_url: str):
    r = session.get(mail_url, verify=False, timeout=15)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.select("table tr")[1:]  # skip header

    latest_dt = None
    latest_link = None

    for tr in rows:
        tds = tr.find_all("td")
        if len(tds) < 5:
            continue

        sent_str = tds[0].get_text(strip=True)  # "2026-02-15 23:20:16 +0000"
        try:
            dt = datetime.strptime(sent_str, "%Y-%m-%d %H:%M:%S %z")
        except ValueError:
            continue

        body_td = tds[4]
        a = body_td.find("a", href=True)
        if not a:
            continue

        link = urljoin(mail_url, a["href"])

        if latest_dt is None or dt > latest_dt:
            latest_dt = dt
            latest_link = link

    return latest_link

if __name__ == "__main__":
    mail_url = input("Mail URL (…/email): ").strip()
    with requests.Session() as s:
       latest_link = get_latest_verification_link(s, mail_url)

    if not latest_link:
        print("FAIL: no verification link found")
    else:
        print("PASS")
        print("Latest link:", latest_link)

