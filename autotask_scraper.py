#!/usr/bin/env python3
"""
autotask_entity_scraper.py

Scrapes the Autotask REST API documentation to build a list of every
API entity together with the names of any fields in that entity's
"Field definitions" table whose Datatype is "datetime".

Source page:
    https://www.autotask.net/help/developerhelp/Content/APIs/REST/Entities/_EntitiesOverview.htm

Output:
    - autotask_entities_datetime_fields.json
    - autotask_entities_datetime_fields.csv

Requirements:
    pip install selenium beautifulsoup4 webdriver-manager

Notes on approach
------------------
The docs site is a Zoomin/MadCap-style help center. The list of entities is
reachable two ways on the overview page:

  1. The left-hand sidebar / table-of-contents tree (JS-rendered - this is
     why Selenium is used rather than plain requests).
  2. A "List of entities" table in the main content of the overview page
     itself, which contains the same links.

Because sidebar markup on doc sites like this can change and is sometimes
rendered inside an iframe, this script tries several known selector
patterns for the sidebar first, and if none of them yield entity links,
falls back to scraping the anchor tags out of the main-content entity
table (which points at the exact same set of "...Entity.htm" pages).
Either way you get the full set of entity detail pages to crawl.
"""

import csv
import json
import re
import time
import logging
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #

OVERVIEW_URL = (
    "https://www.autotask.net/help/developerhelp/Content/APIs/REST/"
    "Entities/_EntitiesOverview.htm"
)
BASE_URL = "https://www.autotask.net"

PAGE_LOAD_TIMEOUT = 25          # seconds to wait for a page/element to appear
BETWEEN_REQUEST_DELAY = 0.75    # be polite - seconds between entity page loads
HEADLESS = True
OUTPUT_JSON = "autotask_entities_datetime_fields.json"
OUTPUT_CSV = "autotask_entities_datetime_fields.csv"

# Candidate CSS selectors for the sidebar/TOC links. Tried in order; the
# first one that yields a non-empty set of matching links wins.
SIDEBAR_SELECTORS = [
    "#site-toc a[href]",
    "#toc a[href]",
    ".mc-toc a[href]",
    ".Zoomin-TOC a[href]",
    "nav[role='navigation'] a[href]",
    ".toc-list a[href]",
    "#leftNavigation a[href]",
    ".sidebar a[href]",
]

# Only follow links that actually point at an entity documentation page.
ENTITY_LINK_PATTERN = re.compile(r"/Entities/[^/]+Entity\.htm(?:#.*)?$", re.IGNORECASE)
# Some entity pages don't end in "...Entity.htm" (e.g. InventoryStockedItems.htm)
# so fall back to "lives under /REST/Entities/ and isn't the overview page itself"
ENTITY_DIR_PATTERN = re.compile(r"/APIs/REST/Entities/[^/]+\.htm(?:#.*)?$", re.IGNORECASE)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("autotask_scraper")


@dataclass
class EntityResult:
    name: str
    url: str
    datetime_fields: Optional[list] = field(default=None)
    error: Optional[str] = None


# --------------------------------------------------------------------------- #
# Driver setup
# --------------------------------------------------------------------------- #

def build_driver(headless: bool = HEADLESS) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1600,1200")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver


# --------------------------------------------------------------------------- #
# Step 1: collect entity links from the overview page
# --------------------------------------------------------------------------- #

def collect_entity_links(driver: webdriver.Chrome) -> "dict[str, str]":
    """
    Returns a dict mapping entity display name -> absolute URL.
    Tries the sidebar/TOC first, then falls back to the in-page
    "List of entities" table.
    """
    log.info("Loading overview page: %s", OVERVIEW_URL)
    driver.get(OVERVIEW_URL)

    # Give the JS-rendered TOC a chance to populate.
    try:
        WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except TimeoutException:
        log.warning("Timed out waiting for overview page body to load.")

    links: dict[str, str] = {}

    # --- Attempt 1: sidebar / TOC selectors -------------------------------
    for selector in SIDEBAR_SELECTORS:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
        except WebDriverException:
            elements = []

        if not elements:
            continue

        found = {}
        for el in elements:
            href = el.get_attribute("href")
            text = (el.text or "").strip()
            if not href:
                continue
            abs_url = urljoin(BASE_URL, href)
            if ENTITY_LINK_PATTERN.search(abs_url) or ENTITY_DIR_PATTERN.search(abs_url):
                if "_EntitiesOverview" in abs_url:
                    continue
                name = text if text else abs_url.rsplit("/", 1)[-1].replace("Entity.htm", "").replace(".htm", "")
                found[name] = abs_url

        if found:
            log.info(
                "Sidebar selector %r yielded %d entity links.", selector, len(found)
            )
            links.update(found)
            break  # first working selector wins
        else:
            log.debug("Sidebar selector %r present but no entity links matched.", selector)

    # --- Attempt 2: fall back to the main-content "List of entities" table -
    if not links:
        log.info(
            "No sidebar entity links found via known selectors; "
            "falling back to the in-page entity table."
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            abs_url = urljoin(OVERVIEW_URL, href)
            if "_EntitiesOverview" in abs_url:
                continue
            if ENTITY_LINK_PATTERN.search(abs_url) or ENTITY_DIR_PATTERN.search(abs_url):
                name = a.get_text(strip=True) or abs_url.rsplit("/", 1)[-1]
                links[name] = abs_url

    log.info("Collected %d unique entity links total.", len(links))
    return links


# --------------------------------------------------------------------------- #
# Step 2: visit each entity page and pull the datetime fields
# --------------------------------------------------------------------------- #

def extract_datetime_fields(driver: webdriver.Chrome, url: str) -> "list[str]":
    """
    Loads an entity's documentation page and returns the list of Field
    Name values whose Datatype column contains "datetime".
    Returns an empty list if the field-definitions table has no datetime
    fields (caller turns that into None), and raises on hard failures.
    """
    driver.get(url)
    try:
        WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
    except TimeoutException:
        # Some entity pages (e.g. pure "refer to..." stub rows) may have no
        # table at all - that's a legitimate "no fields" case, not an error.
        log.warning("No table found (or slow load) on %s", url)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find the "Field definitions" heading, then the first table that
    # follows it in document order.
    field_table = None
    heading = None
    for tag in soup.find_all(re.compile("^h[1-6]$")):
        if "field definitions" in tag.get_text(strip=True).lower():
            heading = tag
            break

    if heading is not None:
        for sib in heading.find_all_next():
            if sib.name == "table":
                field_table = sib
                break
            # stop if we hit the next top-level heading (i.e. table isn't
            # under Field definitions after all)
            if sib.name in ("h1", "h2") and sib is not heading:
                break
    else:
        # Fallback: some entity stub pages don't have a "Field definitions"
        # heading structured exactly this way. Look for any table whose
        # header row contains "Datatype".
        for table in soup.find_all("table"):
            header_text = table.get_text(" ", strip=True).lower()
            if "field name" in header_text and "datatype" in header_text:
                field_table = table
                break

    if field_table is None:
        return []

    rows = field_table.find_all("tr")
    if not rows:
        return []

    header_cells = [c.get_text(strip=True).lower() for c in rows[0].find_all(["th", "td"])]
    try:
        name_idx = next(i for i, h in enumerate(header_cells) if "field name" in h)
    except StopIteration:
        name_idx = 0
    try:
        type_idx = next(i for i, h in enumerate(header_cells) if "datatype" in h)
    except StopIteration:
        # Can't find the type column - bail out gracefully.
        return []

    datetime_fields = []
    for row in rows[1:]:
        cells = row.find_all(["td", "th"])
        if len(cells) <= max(name_idx, type_idx):
            continue
        field_name = cells[name_idx].get_text(strip=True)
        datatype = cells[type_idx].get_text(strip=True).lower()
        if "datetime" in datatype:
            datetime_fields.append(field_name)

    return datetime_fields


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    driver = build_driver()
    results: list[EntityResult] = []

    try:
        entity_links = collect_entity_links(driver)

        if not entity_links:
            log.error("No entity links were found at all - aborting.")
            return

        total = len(entity_links)
        for i, (name, url) in enumerate(sorted(entity_links.items()), start=1):
            log.info("[%d/%d] %s -> %s", i, total, name, url)
            try:
                dt_fields = extract_datetime_fields(driver, url)
                results.append(
                    EntityResult(
                        name=name,
                        url=url,
                        datetime_fields=dt_fields if dt_fields else None,
                    )
                )
            except (TimeoutException, WebDriverException) as e:
                log.warning("Failed to load/parse %s: %s", url, e)
                results.append(
                    EntityResult(name=name, url=url, datetime_fields=None, error=str(e))
                )
            time.sleep(BETWEEN_REQUEST_DELAY)

    finally:
        driver.quit()

    # --- write outputs ------------------------------------------------------
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "entity": r.name,
                    "url": r.url,
                    "datetime_fields": r.datetime_fields,
                    "error": r.error,
                }
                for r in results
            ],
            f,
            indent=2,
        )
    log.info("Wrote %s", OUTPUT_JSON)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["entity", "url", "datetime_fields", "error"])
        for r in results:
            fields_str = "; ".join(r.datetime_fields) if r.datetime_fields else "None"
            writer.writerow([r.name, r.url, fields_str, r.error or ""])
    log.info("Wrote %s", OUTPUT_CSV)

    log.info("Done. Scraped %d entities.", len(results))


if __name__ == "__main__":
    main()