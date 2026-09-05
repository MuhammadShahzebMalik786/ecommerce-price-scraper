"""
E-commerce Price Scraper (SeleniumBase)
----------------------------------------
Scrapes product name, price, image URL, and stock status from a paginated
e-commerce catalog, cleans/dedupes the data, and exports it to CSV + JSON.

Target: https://scrapeme.live/shop/  (a public sandbox site built for
scraping practice — safe to scrape, no ToS/authorization concerns, and its
product-grid structure mirrors real WooCommerce/Shopify storefronts).

Usage:
    pip install -r requirements.txt
    python scraper.py --pages 5 --headless

Author: Saqib S.
"""

import argparse
import csv
import json
import re
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path

from selenium.webdriver.common.by import By
from seleniumbase import SB

BASE_URL = "https://scrapeme.live/shop/"


@dataclass
class Product:
    id: str
    name: str
    price: float
    currency: str
    image_url: str
    in_stock: bool
    source_page: int
    product_url: str


def parse_price(raw_price: str) -> tuple[float, str]:
    """Turn '£1.99' style text into (1.99, 'GBP')."""
    raw_price = raw_price.strip()
    currency = "GBP" if "£" in raw_price else ("USD" if "$" in raw_price else "")
    match = re.search(r"[\d,]+\.\d+|\d+", raw_price)
    amount = float(match.group().replace(",", "")) if match else 0.0
    return amount, currency


def scrape_page(sb, page_num: int) -> list[Product]:
    url = BASE_URL if page_num == 1 else f"{BASE_URL}page/{page_num}/"
    sb.open(url)
    sb.wait_for_element("ul.products", timeout=10)

    products = []
    cards = sb.driver.find_elements(By.CSS_SELECTOR, "ul.products li.product")
    for card in cards:
        try:
            name = card.find_element(By.CSS_SELECTOR, "h2").text.strip()
            price_text = card.find_element(By.CSS_SELECTOR, ".price").text
            amount, currency = parse_price(price_text)
            link_el = card.find_element(By.CSS_SELECTOR, "a.woocommerce-LoopProduct-link")
            product_url = link_el.get_attribute("href")
            img_el = card.find_element(By.CSS_SELECTOR, "img")
            image_url = img_el.get_attribute("src")

            # scrapeme.live doesn't expose stock on the grid; default True,
            # a real integration would open the product page or check a
            # ".out-of-stock" class if present.
            in_stock = "out-of-stock" not in card.get_attribute("class")

            product_id = product_url.rstrip("/").split("/")[-1]

            products.append(
                Product(
                    id=product_id,
                    name=name,
                    price=amount,
                    currency=currency,
                    image_url=image_url,
                    in_stock=in_stock,
                    source_page=page_num,
                    product_url=product_url,
                )
            )
        except Exception as e:
            print(f"  [warn] skipped a card on page {page_num}: {e}", file=sys.stderr)
            continue

    return products


def dedupe(products: list[Product]) -> list[Product]:
    seen = {}
    for p in products:
        seen[p.id] = p  # last-seen wins; keeps list unique by product id
    return list(seen.values())


def export(products: list[Product], out_dir: Path):
    out_dir.mkdir(exist_ok=True)

    csv_path = out_dir / "products.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(products[0]).keys()))
        writer.writeheader()
        for p in products:
            writer.writerow(asdict(p))

    json_path = out_dir / "products.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump([asdict(p) for p in products], f, indent=2)

    print(f"\nSaved {len(products)} unique products:")
    print(f"  -> {csv_path}")
    print(f"  -> {json_path}")


def main():
    parser = argparse.ArgumentParser(description="Scrape product listings from scrapeme.live")
    parser.add_argument("--pages", type=int, default=3, help="Number of catalog pages to scrape")
    parser.add_argument("--headless", action="store_true", help="Run browser headlessly")
    parser.add_argument("--out", default="output", help="Output directory")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds to wait between pages (politeness)")
    args = parser.parse_args()

    all_products: list[Product] = []

    with SB(headless=args.headless) as sb:
        for page_num in range(1, args.pages + 1):
            print(f"Scraping page {page_num}/{args.pages}...")
            page_products = scrape_page(sb, page_num)
            print(f"  found {len(page_products)} products")
            all_products.extend(page_products)
            if page_num < args.pages:
                time.sleep(args.delay)

    unique_products = dedupe(all_products)
    if not unique_products:
        print("No products scraped — check selectors or connectivity.", file=sys.stderr)
        sys.exit(1)

    export(unique_products, Path(args.out))


if __name__ == "__main__":
    main()
