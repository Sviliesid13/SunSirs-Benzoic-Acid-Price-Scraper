import csv
import os
import time
import requests
from bs4 import BeautifulSoup

URL = "https://www.sunsirs.com/uk/prodetail-177.html"
CSV_FILE = "prices.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


def scrape_price(retries: int = 3) -> tuple[str, str] | tuple[None, None]:
    """Fetch page with retries, parse the price table, return (date, price)."""
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(URL, headers=HEADERS, timeout=30)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            for row in soup.select("table tr"):
                cells = row.find_all("td")
                if len(cells) == 4:
                    commodity = cells[0].get_text(strip=True)
                    price_val = cells[2].get_text(strip=True)
                    date_val  = cells[3].get_text(strip=True)
                    if commodity != "Commodity" and price_val.replace(".", "").isdigit():
                        return date_val, price_val
        except Exception as e:
            print(f"  Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(5)
    return None, None


def append_to_csv(date_str: str, price: str) -> None:
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
        print("  ERROR: could not extract price.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
