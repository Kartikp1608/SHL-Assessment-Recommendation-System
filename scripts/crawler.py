# playwright_individual_final.py
# Scrapes all Individual Test Solutions (377+) from SHL

import time
import csv
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import parse 

BASE = "https://www.shl.com"
START_URL = "https://www.shl.com/products/product-catalog/?start={}&type=1"  
OUTPUT = "individual_tests_full.csv"

FIELDS = [
    "assessment_id",
    "name",
    "url",
    "description",
    "competencies",
    "adaptive",
    "col2_raw",
    "test_type_raw",
    "keys"
]

def t(x):
    return x.get_text(" ", strip=True) if x else ""

def parse_row(row):
    aid = row.get("data-entity-id", "")
    a = row.select_one("td[class*='table-heading__title'] a") or row.select_one("a")
    name = t(a)
    href = a["href"] if a and a.has_attr("href") else ""
    url = urljoin(BASE, href)

    cols = row.select("td[class*='table-heading__general']")
    adaptive = False
    col2 = ""
    test_type = ""

    if len(cols) > 0:
        adaptive = bool(cols[0].select_one(".catalogue__circle.-yes"))
    if len(cols) > 1:
        col2 = t(cols[1])
    if len(cols) > 0:
        test_type = t(cols[-1])

    keys = [t(x) for x in row.select(".product-catalogue__key")]

    return {
        "assessment_id": aid,
        "name": name,
        "url": url,
        "adaptive": str(adaptive),
        "col2_raw": col2,
        "test_type_raw": test_type,
        "keys": "|".join(keys)
    }

def parse_detail(html):
    soup = BeautifulSoup(html, "html.parser")

    desc = ""
    for sel in [
        ".product-description",
        ".product-detail-content",
        ".product-detail__intro",
        "meta[name='description']"
    ]:
        el = soup.select_one(sel)
        if el:
            desc = el["content"] if el.name == "meta" else t(el)
            break
    
    competencies = [t(x) for x in soup.select(".product-catalogue__key")]
    competencies = "|".join(competencies)

    duration = 0
    duration_el = soup.select_one(".field--name-field-duration")
    if duration_el:
        txt = t(duration_el)
        # extract number from "20 minutes"
        num = "".join([c for c in txt if c.isdigit()])
        duration = int(num) if num.isdigit() else 0

    # fallback (some pages use technical specs list)
    if duration == 0:
        for li in soup.select(".product-detail__technical li"):
            line = t(li).lower()
            if "minute" in line:
                num = "".join([c for c in line if c.isdigit()])
                duration = int(num) if num.isdigit() else 0
                break

    adaptive_support = "No"
    adapt_el = soup.select_one(".field--name-field-adaptive-support")
    if adapt_el:
        val = t(adapt_el).lower()
        adaptive_support = "Yes" if "yes" in val else "No"

    # table fallback
    if adaptive_support == "No":
        if soup.select_one(".catalogue__circle.-yes"):
            adaptive_support = "Yes"

    remote_support = "Yes"
    remote_el = soup.select_one(".field--name-field-remote-testing")
    if remote_el:
        val = t(remote_el).lower()
        remote_support = "Yes" if "yes" in val else "No"

    test_type = []
    test_type_el = soup.select_one(".field--name-field-test-type")
    if test_type_el:
        test_type_raw = t(test_type_el)
        test_type = [x.strip() for x in test_type_raw.split(",") if x.strip()]

    return {
        "description": desc,
        "competencies": competencies,
        "duration": duration,
        "adaptive_support": adaptive_support,
        "remote_support": remote_support,
        "test_type": "|".join(test_type)
    }

def run():
    results = []
    seen = set()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()

        for start in range(0, 10000, 12):
            url = START_URL.format(start)
            print("Visiting:", url)

            page.goto(url, timeout=0)

            # do NOT wait for selector, just wait for page to load
            page.wait_for_timeout(1500)

            soup = BeautifulSoup(page.content(), "html.parser")
            rows = soup.select("tr[data-entity-id]")

            print("Found", len(rows), "rows")

            # if no rows, this is the end
            if len(rows) == 0:
                print("No rows stopping")
                break

            for row in rows:
                meta = parse_row(row)
                if not meta["url"] or meta["url"] in seen:
                    continue

                seen.add(meta["url"])

                print("  scraping:", meta["name"])
                page.goto(meta["url"], timeout=0)
                page.wait_for_timeout(800)

                details = parse_detail(page.content())
                meta["description"] = details["description"]
                meta["competencies"] = details["competencies"]
                meta["duration"] = details["duration"]
                meta["adaptive_support"] = details["adaptive_support"]
                meta["remote_support"] = details["remote_support"]
                meta["test_type"] = details["test_type"]

                results.append(meta)

                time.sleep(0.10)

        browser.close()

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(results)

    print("========= DONE =========")
    print("Total items scraped:", len(results))

if __name__ == "__main__":
    run()
