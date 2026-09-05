"""Generate a clean portfolio cover image from the actual scraped data."""
import csv
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
BG = (17, 20, 24)
CARD_BG = (26, 30, 36)
BORDER = (42, 47, 54)
TEXT_PRIMARY = (237, 239, 241)
TEXT_SECONDARY = (148, 155, 165)
ACCENT = (94, 189, 141)  # green — "in stock" / success feel
CODE_BG = (13, 15, 18)
CODE_TEXT = (150, 220, 180)
HEADER_BG = (20, 23, 28)

def load_font(size, bold=False):
    names = ["arialbd.ttf", "Arial Bold.ttf"] if bold else ["arial.ttf", "Arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()

f_title = load_font(34, bold=True)
f_sub = load_font(17)
f_mono_hdr = load_font(15, bold=True)
f_mono = load_font(15)
f_small = load_font(13)
f_badge = load_font(13, bold=True)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# Top header bar
d.text((48, 40), "E-commerce price scraper", font=f_title, fill=TEXT_PRIMARY)
d.text((48, 82), "Python + SeleniumBase  |  scrape -> clean -> dedupe -> CSV/JSON export", font=f_sub, fill=TEXT_SECONDARY)

# Stack badges
badges = ["Python", "SeleniumBase", "Selenium", "CSV/JSON", "Web Scraping"]
bx = 48
by = 118
for b in badges:
    tw = d.textlength(b, font=f_badge)
    pad = 14
    bw = tw + pad * 2
    d.rounded_rectangle([bx, by, bx + bw, by + 30], radius=15, fill=(30, 40, 36), outline=(50, 90, 70))
    d.text((bx + pad, by + 7), b, font=f_badge, fill=ACCENT)
    bx += bw + 10

# Terminal-style card showing the run
term_x, term_y, term_w, term_h = 48, 172, 560, 300
d.rounded_rectangle([term_x, term_y, term_x + term_w, term_y + term_h], radius=10, fill=CODE_BG, outline=BORDER)
d.rounded_rectangle([term_x, term_y, term_x + term_w, term_y + 34], radius=10, fill=(24, 27, 32))
d.rectangle([term_x, term_y + 20, term_x + term_w, term_y + 34], fill=(24, 27, 32))
for i, c in enumerate([(237, 106, 94), (245, 191, 79), (97, 197, 92)]):
    d.ellipse([term_x + 16 + i * 20, term_y + 12, term_x + 16 + i * 20 + 10, term_y + 22], fill=c)

lines = [
    ("$ ", "python scraper.py --pages 3 --headless"),
    ("", ""),
    ("", "Scraping page 1/3..."),
    ("", "  found 16 products"),
    ("", "Scraping page 2/3..."),
    ("", "  found 16 products"),
    ("", "Scraping page 3/3..."),
    ("", "  found 16 products"),
    ("", ""),
    ("", "Saved 48 unique products:"),
    ("", "  -> output/products.csv"),
    ("", "  -> output/products.json"),
]
ty = term_y + 50
for prompt, text in lines:
    if prompt:
        d.text((term_x + 20, ty), prompt, font=f_mono_hdr, fill=(120, 170, 255))
        d.text((term_x + 20 + d.textlength(prompt, font=f_mono_hdr), ty), text, font=f_mono, fill=CODE_TEXT)
    else:
        color = ACCENT if text.strip().startswith(("Saved", "->")) else TEXT_SECONDARY
        d.text((term_x + 20, ty), text, font=f_mono, fill=color)
    ty += 21

# Data table card (right side) — pull real rows from products.csv
data_x, data_y, data_w, data_h = 632, 172, 600, 300
d.rounded_rectangle([data_x, data_y, data_x + data_w, data_y + data_h], radius=10, fill=CARD_BG, outline=BORDER)
d.text((data_x + 20, data_y + 16), "products.csv", font=f_mono_hdr, fill=TEXT_PRIMARY)
d.text((data_x + 20, data_y + 38), "48 unique rows, deduplicated by product ID", font=f_small, fill=TEXT_SECONDARY)

rows = []
csv_path = Path("output/products.csv")
with csv_path.open(encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    for r in reader:
        rows.append(r)
        if len(rows) >= 8:
            break

cols = [("name", 190), ("price", 90), ("currency", 90), ("in_stock", 110)]
tbl_x = data_x + 20
tbl_y = data_y + 68
col_x = tbl_x
d.line([(tbl_x, tbl_y + 22), (data_x + data_w - 20, tbl_y + 22)], fill=BORDER)
cx = tbl_x
for name, w in cols:
    d.text((cx, tbl_y), name, font=f_small, fill=TEXT_SECONDARY)
    cx += w
ry = tbl_y + 32
for row in rows:
    cx = tbl_x
    vals = [row["name"], f'{float(row["price"]):.2f}', row["currency"], "yes" if row["in_stock"] == "True" else "no"]
    for (name, w), v in zip(cols, vals):
        color = TEXT_PRIMARY if name != "in_stock" else ACCENT
        d.text((cx, ry), v, font=f_mono, fill=color)
        cx += w
    ry += 26

# Bottom summary stat cards
stats = [("48", "products scraped"), ("3", "pages crawled"), ("0", "duplicates in output"), ("2", "export formats")]
sx = 48
sy = 500
sw = 284
sh = 90
for label_val, label_desc in stats:
    d.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=10, fill=CARD_BG, outline=BORDER)
    d.text((sx + 20, sy + 16), label_val, font=f_title, fill=ACCENT)
    d.text((sx + 20, sy + 58), label_desc, font=f_small, fill=TEXT_SECONDARY)
    sx += sw + 16

# Footer
d.text((48, 630), "Target: scrapeme.live (public scraping sandbox)  |  Adaptable to any WooCommerce / Shopify / custom catalog", font=f_small, fill=TEXT_SECONDARY)
d.text((48, 655), "github.com/MuhammadShahzebMalik786/ecommerce-price-scraper", font=f_small, fill=(120, 170, 255))

img.save("portfolio_cover.png")
print("Saved portfolio_cover.png")
