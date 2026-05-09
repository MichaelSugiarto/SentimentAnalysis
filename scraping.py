# scraping.py
# Scraping ulasan dari Google Play Store menggunakan google-play-scraper

from google_play_scraper import reviews, Sort
import pandas as pd
import time
import random

# ── Daftar aplikasi yang akan di-scrape ───────────────────────────────────────
APPS = [
    ('com.gojek.app',          'Gojek'),
    ('com.tokopedia.tkpd',     'Tokopedia'),
    ('com.shopee.id',          'Shopee'),
    ('id.dana.mobile',         'DANA'),
    ('com.bukalapak.android',  'Bukalapak'),
    ('com.ovo.id',             'OVO'),
    ('com.grab.grabmerchant',  'Grab'),
    ('id.co.lazada.mobileapp', 'Lazada'),
]

# Target per (app × sort_order) = 2.000 → total potensi 32.000 sebelum dedup
COUNT_PER_BATCH = 2000

all_reviews = []

for app_id, app_name in APPS:
    print(f"\n[SCRAPING] {app_name} ({app_id})")
    for sort_order in [Sort.NEWEST, Sort.MOST_RELEVANT]:
        try:
            result, _ = reviews(
                app_id,
                lang='id',
                country='id',
                sort=sort_order,
                count=COUNT_PER_BATCH,
                filter_score_with=None,
            )
            for r in result:
                all_reviews.append({
                    'app':    app_name,
                    'review': r['content'],
                    'score':  r['score'],
                    'date':   str(r['at']),
                })
            print(f"  ✓ Sort={sort_order} → {len(result):,} ulasan")
            time.sleep(random.uniform(2, 4))   # hindari rate-limit
        except Exception as e:
            print(f"  ✗ Error: {e}")
            time.sleep(5)

# ── Bersihkan & simpan ────────────────────────────────────────────────────────
df = pd.DataFrame(all_reviews)
df.drop_duplicates(subset=['review'], inplace=True)
df = df[df['review'].str.strip() != '']
df.reset_index(drop=True, inplace=True)

print(f"\n{'='*50}")
print(f"Total ulasan unik : {len(df):,}")
print(f"Distribusi score  :\n{df['score'].value_counts().sort_index()}")

df.to_csv('dataset.csv', index=False, encoding='utf-8-sig')
print("\n✅  Dataset disimpan → dataset.csv")