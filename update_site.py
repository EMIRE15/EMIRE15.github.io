import os
import requests
from datetime import datetime

APP_ID = os.environ['RAKUTEN_APP_ID']
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
    url = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706'
    params = {
        'applicationId': APP_ID,
        'keyword': keyword,
        'hits': 3,
        'sort': '-reviewCount',
        'imageFlag': 1,
        'format': 'json',
    }
    try:
        res = requests.get(url, params=params, timeout=10)
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
    print('Done!')

if __name__ == '__main__':
    main()
