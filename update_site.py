import os
import requests
from datetime import datetime

APP_ID = os.environ['RAKUTEN_APP_ID']
ACCESS_KEY = os.environ['RAKUTEN_ACCESS_KEY']
AFFILIATE_ID = os.environ['RAKUTEN_AFFILIATE_ID']

KEYWORDS = [
    'ドライブレコーダー',
    'スマホホルダー 車',
    'モバイルバッテリー',
    'カーナビ',
    'サンシェード 車',
    'エアダスター',
    'カーコーティング',
    'イヤホン bluetooth',
]

def fetch_items(keyword):
    url = 'https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20220601'
    params = {
        'applicationId': APP_ID,
        'accessKey': ACCESS_KEY,
        'keyword': keyword,
        'hits': 3,
        'sort': '-reviewCount',
        'imageFlag': 1,
        'format': 'json',
    }
    headers = {
        'Referer': 'https://emire15.github.io/',
        'Origin': 'https://emire15.github.io',
        'User-Agent': 'Mozilla/5.0',
    }
    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"[{keyword}] status={res.status_code}")
        data = res.json()
        if 'Items' not in data:
            print(f"[{keyword}] response={data}")
        return data.get('Items', [])
    except Exception as e:
        print(f"[{keyword}] error={e}")
        return []

def make_card(item):
    info = item['Item']
    name = info['itemName'][:40]
    price = f"¥{info['itemPrice']:,}"
    img = info['mediumImageUrls'][0]['imageUrl'] if info['mediumImageUrls'] else ''
    url = info['itemUrl']
    return f'''
    <div class="auto-item">
      <a href="{url}" target="_blank" rel="nofollow noopener">
        <img src="{img}" alt="{name}" loading="lazy">
        <p class="item-name">{name}</p>
        <p class="item-price">{price}</p>
        <span class="btn">楽天で見る →</span>
      </a>
    </div>'''

def main():
    now = datetime.now().strftime('%Y年%m月%d日 %H:%M')
    cards = ''
    for kw in KEYWORDS:
        items = fetch_items(kw)
        print(f"[{kw}] {len(items)}件取得")
        for item in items:
            cards += make_card(item)

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DRIVE GEAR LAB | 自動更新アイテム一覧</title>
<style>
body {{ font-family: sans-serif; background: #111; color: #eee; margin: 0; padding: 20px; }}
h1 {{ text-align: center; color: #e60027; }}
p.updated {{ text-align: center; color: #aaa; font-size: 0.85em; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; max-width: 1200px; margin: 0 auto; }}
.auto-item {{ background: #1e1e1e; border-radius: 8px; padding: 12px; text-align: center; }}
.auto-item a {{ text-decoration: none; color: inherit; }}
.auto-item img {{ width: 100%; border-radius: 4px; }}
.item-name {{ font-size: 0.8em; margin: 8px 0 4px; }}
.item-price {{ color: #e60027; font-weight: bold; }}
.btn {{ display: inline-block; background: #e60027; color: #fff; padding: 6px 12px; border-radius: 4px; font-size: 0.8em; margin-top: 8px; }}
</style>
</head>
<body>
<h1>🚗 DRIVE GEAR LAB 自動更新アイテム</h1>
<p class="updated">最終更新: {now}</p>
<div class="grid">
{cards}
</div>
</body>
</html>'''

    with open('auto-items.html', 'w', encoding='utf-8') as f:
        f.write(html)
    update_sitemap()
    print('Done!')
def update_sitemap():
    import glob
    base_url = 'https://emire15.github.io/'
    today = datetime.now().strftime('%Y-%m-%d')
    
    html_files = glob.glob('*.html')
    exclude = ['google3193697637b4df7b.html']
    
    urls = []
    for f in sorted(html_files):
        if f in exclude:
            continue
        if f == 'index.html':
            urls.insert(0, f'  <url>\n    <loc>{base_url}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>1.0</priority>\n  </url>')
        else:
            urls.append(f'  <url>\n    <loc>{base_url}{f}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>')
    
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += '\n'.join(urls)
    sitemap += '\n</urlset>'
    
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)
    print('Sitemap updated!')


if __name__ == '__main__':
    main()

