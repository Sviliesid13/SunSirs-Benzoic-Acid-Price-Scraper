import csv
import os
import re
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

URL = "https://www.sunsirs.com/uk/prodetail-177.html"
CSV_FILE = "prices.csv"


def scrape_price() -> str | None:
    """Launch a headless browser, load the page, and extract the latest price."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        page = context.new_page()

        # Wait for the page to fully load including JS-rendered content
        page.goto(URL, wait_until="networkidle", timeout=60_000)

        # Give extra time for dynamic price tables to render
        page.wait_for_timeout(3_000)

        # Try multiple selectors — site structure may vary
        price = None

        # Strategy 1: look for a table cell that contains a number like "1234.56"
        # The price table on sunsirs typically has rows with date | price | change
        rows = page.query_selector_all("table tr")
        for row in rows:
            cells = row.query_selector_all("td")
            if len(cells) >= 2:
                candidate = cells[1].inner_text().strip()
                # Match a numeric price (e.g. "1234.56" or "1,234.56")
                if re.match(r"^[\d,]+\.?\d*$", candidate):
                    price = candidate.replace(",", "")
                    break  # First data row = most recent price

        # Strategy 2: fallback — scan all text for price pattern near "price" keyword
        if not price:
            content = page.inner_text("body")
            match = re.search(
                r"(?:price|Price)\s*[:\|]?\s*([\d,]+\.?\d*)", content
            )
            if match:
                price = match.group(1).replace(",", "")

        browser.close()
        return price


def append_to_csv(date_str: str, price: str) -> None:
    """Append a new row to prices.csv, creating the file with headers if needed."""
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "price_cny_per_ton"])
        writer.writerow([date_str, price])


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"Scraping {URL} ...")

    price = scrape_price()

    if price:
        print(f"  Date:  {today}")
        print(f"  Price: {price}")
        append_to_csv(today, price)
        print(f"  Saved to {CSV_FILE}")
    else:
        print("  ERROR: could not extract price. Page structure may have changed.")
        # Exit with error so GitHub Actions marks the run as failed
        raise SystemExit(1)


if __name__ == "__main__":
    main()
