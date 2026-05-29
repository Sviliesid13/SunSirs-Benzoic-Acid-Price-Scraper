import csv
import os
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

URL = "https://www.sunsirs.com/uk/prodetail-177.html"
CSV_FILE = "prices.csv"


def scrape_price() -> tuple[str, str] | tuple[None, None]:
    """Launch headless Chrome, load the page, extract latest price and its date."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()
        page.goto(URL, wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(3_000)

        # The table structure is:
        # <tr><td>Commodity</td><td>Sectors</td><td>Price</td><td>Date</td></tr>
        # <tr><td>Toluene</td><td>Chemical</td><td>6594.33</td><td>2026-05-28</td></tr>
        # First data row = most recent entry
        rows = page.query_selector_all("table tr")

        price = None
        date_str = None

        for row in rows:
            cells = row.query_selector_all("td")
            if len(cells) == 4:
                commodity = cells[0].inner_text().strip()
                price_val = cells[2].inner_text().strip()
                date_val  = cells[3].inner_text().strip()
                # Skip the header row; grab the first real data row
                if commodity != "Commodity" and price_val.replace(".", "").isdigit():
                    price    = price_val
                    date_str = date_val
                    break

        browser.close()
        return date_str, price


def append_to_csv(date_str: str, price: str) -> None:
    """Append a new row; create file with header if it doesn't exist."""
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "price_cny_per_ton"])
        writer.writerow([date_str, price])


def main():
    print(f"Scraping {URL} ...")
    date_str, price = scrape_price()

    if price and date_str:
        print(f"  Date:  {date_str}")
        print(f"  Price: {price} CNY/ton")
        append_to_csv(date_str, price)
        print(f"  Saved to {CSV_FILE}")
    else:
        print("  ERROR: could not extract price. Page structure may have changed.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
