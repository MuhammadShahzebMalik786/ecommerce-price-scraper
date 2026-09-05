# E-commerce Price Scraper (SeleniumBase)

A production-style scraper that pulls **product name, price, currency, image URL, and stock status** from a paginated e-commerce catalog, deduplicates the results, and exports clean **CSV + JSON**.

## Why this project

Retailers and market-research clients constantly need up-to-date competitor pricing. This scraper demonstrates the exact workflow that kind of job requires:

1. **Reliable page-by-page crawling** with pagination handling
2. **Structured field extraction** (name, price parsing with currency detection, image, stock)
3. **Data cleaning** — normalized price parsing, deduplication by product ID
4. **Clean export** to CSV and JSON, ready to load into a spreadsheet or database
5. **Politeness controls** (configurable delay between requests) and headless mode for server/CI use

## Tech stack

- **Python 3.10+**
- **SeleniumBase** — handles browser automation, waits, and anti-bot quirks more robustly than raw Selenium
- Standard library `csv`/`json`/`dataclasses` for clean, dependency-light output handling

## Target site

Scraped against [scrapeme.live/shop](https://scrapeme.live/shop/) — a public sandbox storefront (Pokémon-themed) purpose-built for scraping practice, with the same WooCommerce grid/pagination structure used by thousands of real online stores. This keeps the demo 100% authorized and reproducible while proving the technique transfers directly to real client sites (Shopify, WooCommerce, custom catalogs).

## Usage

```bash
pip install -r requirements.txt
python scraper.py --pages 5 --headless
```

Output lands in `output/products.csv` and `output/products.json`.

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--pages` | 3 | Number of catalog pages to scrape |
| `--headless` | off | Run without opening a visible browser window |
| `--out` | `output` | Output directory |
| `--delay` | 1.0 | Seconds between page requests (politeness) |

## Adapting this for a real client

- Swap the CSS selectors in `scrape_page()` for the target site's markup
- Add proxy/rotation support for large-scale or rate-limited targets
- Point `export()` at a PostgreSQL/MySQL connection instead of CSV for direct DB loads
- Add a scheduler (cron / Airflow) to re-run on an interval and diff prices over time
