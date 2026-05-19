import os
import json
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))

APP_ID = os.environ['RAKUTEN_APP_ID']
AFFILIATE_ID = os.environ.get('RAKUTEN_AFFILIATE_ID', '')

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

# ============================================================
# 構造化データの定義（レビューページごと）
# ============================================================
STRUCTURED_DATA = {
    'review-dashcam.html': {
        'article': {
            'headline': 'ドライブレコーダー 前後2カメラ SONYセンサー搭載 実機レビュー',
            'description': 'SONYセンサー採用ドライブレコーダーを実際に使ってレビュー。夜間画質・取り付けやすさ・駐車監視機能を正直評価。',
            'keywords': 'ドライブレコーダー,前後カメラ,SONYセンサー,楽天',
        },
    },
    'review-earphones.html': {
        'article': {
            'headline': 'ワイヤレスイヤホン Bluetooth 5.4 ノイズキャンセリング 実機レビュー',
            'description': 'Bluetooth 5.4対応ワイヤレスイヤホンをドライブ視点でレビュー。ノイキャン性能・通話品質・バッテリーを正直評価。',
            'keywords': 'ワイヤレスイヤホン,ノイズキャンセリング,Bluetooth,楽天',
        },
    },
    'review-sunshade.html': {
        'article': {
            'headline': '傘型サンシェード CREAS WING 実機レビュー',
            'description': 'ワンタッチ傘型サンシェードを実際に使ってレビュー。車内温度の実測データ・サイズ選びガイド付き。',
            'keywords': 'サンシェード,傘型,車内温度,楽天,CREAS WING',
        },
    },
    'review-phone-holder.html': {
        'article': {
            'headline': '真空吸着マグネット スマホホルダー MagSafe対応 実機レビュー',
            'description': '真空吸着+マグネットのスマホホルダーをレビュー。固定力・着脱のしやすさ・MagSafe対応を正直評価。',
            'keywords': 'スマホホルダー,MagSafe,マグネット,車載,楽天',
        },
    },
    'review-air-duster.html': {
        'article': {
            'headline': '充電式エアーダスター 200000RPM 実機レビュー',
            'description': '充電式エアーダスターを車内清掃・ガジェット掃除で実際に使ってレビュー。風力・バッテリー持ちを正直評価。',
            'keywords': 'エアーダスター,充電式,車内清掃,楽天',
        },
    },
    'review-battery.html': {
        'article': {
            'headline': '大容量モバイルバッテリー 23600mAh 4本ケーブル内蔵 実機レビュー',
            'description': '4本ケーブル内蔵モバイルバッテリーを実際に計測してレビュー。実容量・充電速度・ドライブでの使い勝手を正直評価。',
            'keywords': 'モバイルバッテリー,大容量,PD充電,ケーブル内蔵,楽天',
        },
    },
    'review-navi.html': {
        'article': {
            'headline': 'ATOTO A6 カーナビ 9インチ CarPlay対応 実機レビュー',
            'description': 'Apple CarPlay・Android Auto対応カーナビをレビュー。iPhoneとの連携・画面の見やすさ・取り付けを正直評価。',
            'keywords': 'カーナビ,CarPlay,Android Auto,9インチ,楽天',
        },
    },
    'review-coating.html': {
        'article': {
            'headline': 'ガラスコーティング剤 超撥水スプレータイプ 実機レビュー',
            'description': 'スプレー式ガラスコーティング剤を実際に使ってレビュー。撥水効果・耐久性・施工のしやすさを正直評価。',
            'keywords': 'ガラスコーティング,撥水,スプレー,カーケア,楽天',
        },
    },
    'review-handy-fan.html': {
        'article': {
            'headline': '車載ハンディファン おすすめ3選 選び方ガイド実機レビュー',
            'description': '車載ハンディファンを実際に使ってレビュー。USB給電・クリップ式・首振り機能など選び方のポイントも解説。',
            'keywords': 'ハンディファン,車載,USB,夏,冷却,楽天',
        },
    },
    'review-cigar-charger.html': {
        'article': {
            'headline': 'シガーソケット充電器 USB-C PD対応 おすすめ3選 実機レビュー',
            'description': 'シガーソケット充電器を実際に計測してレビュー。USB-C PD対応・急速充電・発熱を正直評価。',
            'keywords': 'シガーソケット充電器,USB-C,PD充電,カーチャージャー,楽天',
        },
    },
    'review-trash-box.html': {
        'article': {
            'headline': '車用ゴミ箱 折りたたみ式 PUレザー LED付き 実機レビュー',
            'description': '車用折りたたみゴミ箱を3ヶ月使ってレビュー。取り付けやすさ・容量・LEDの実用性を正直評価。',
            'keywords': '車用ゴミ箱,折りたたみ,PUレザー,車内インテリア,楽天',
        },
    },
    'review-iphone17.html': {
        'article': {
            'headline': 'iPhone 17 ドライブ・カーライフ視点 徹底レビュー',
            'description': 'iPhone 17をCarPlay・MagSafe・ナビ活用などカーライフ視点でレビュー。車乗りが気になるポイントを正直評価。',
            'keywords': 'iPhone 17,CarPlay,MagSafe,楽天モバイル',
        },
    },
    'review-clinview-gcoat.html': {
        'article': {
            'headline': 'クリンビュー Gコート ウルトラタフドロップ 実機レビュー',
            'description': 'クリンビュー Gコートを2ヶ月使ってレビュー。撥水効果・耐久性・施工のしやすさを正直評価。',
            'keywords': 'クリンビュー,Gコート,ガラスコーティング,撥水,楽天',
        },
    },
    'review-rinrei-wax.html': {
        'article': {
            'headline': 'リンレイ ガラス系ハイブリッドWAX Gガード固形 実機レビュー',
            'description': 'リンレイ公式ガラス系WAXを複数色の車に施工してレビュー。艶・撥水・耐久性を正直評価。',
            'keywords': 'リンレイ,ガラス系WAX,カーワックス,固形,楽天',
        },
    },
    'review-air-spencer.html': {
        'article': {
            'headline': 'エアースペンサー ピンクシャワー 実機レビュー',
            'description': 'エアースペンサー ピンクシャワーを1ヶ月使ってレビュー。香りの強さ・持続期間・使い心地を正直評価。',
            'keywords': 'エアースペンサー,ピンクシャワー,カーフレグランス,車内芳香剤,楽天',
        },
    },
    'review-led-fog.html': {
        'article': {
            'headline': 'HID屋 LEDフォグランプ Vシリーズ 2色切り替え 実機レビュー',
            'description': 'HID屋 LEDフォグランプを実際に取り付けてレビュー。明るさ・色切り替え・車検対応の実態を正直評価。',
            'keywords': 'HID屋,LEDフォグランプ,2色切り替え,車検対応,楽天',
        },
    },
    'review-led-headlight.html': {
        'article': {
            'headline': 'HID屋 H4 LEDヘッドライト Qシリーズ 爆光 実機レビュー',
            'description': 'HID屋 H4 LEDヘッドライトを実際に取り付けてレビュー。68400cdの明るさと車検対応を正直評価。',
            'keywords': 'HID屋,LEDヘッドライト,H4,爆光,車検対応,楽天',
        },
    },
    'review-prostaff-wax.html': {
        'article': {
            'headline': 'プロスタッフ CCウォーターゴールド 300ml 実機レビュー',
            'description': 'プロスタッフ CCウォーターゴールドを3色の車に施工してレビュー。撥水効果・艶・耐久性を正直評価。',
            'keywords': 'プロスタッフ,CCウォーターゴールド,ガラスコーティング,楽天',
        },
    },
    'review-yupiteru-radar.html': {
        'article': {
            'headline': 'ユピテル YK-2200 GPSレーダー探知機 実機レビュー',
            'description': 'ユピテル YK-2200を3ヶ月使ってレビュー。オービス対応・音声案内の精度・取り付けやすさを正直評価。',
            'keywords': 'ユピテル,GPSレーダー,オービス,レーダー探知機,楽天',
        },
    },
    'review-tpms.html': {
        'article': {
            'headline': 'タイヤ空気圧モニター TPMS ソーラー充電 楽天1位 実機レビュー',
            'description': 'タイヤ空気圧モニターを3ヶ月使ってレビュー。4本リアルタイム監視・警告精度・ソーラー充電の実力を正直評価。',
            'keywords': 'タイヤ空気圧モニター,TPMS,ソーラー充電,安全運転,楽天',
        },
    },
}

BASE_URL = 'https://www.drivegearlab.online'

# ============================================================
# 構造化データ挿入関数
# ============================================================
def inject_structured_data(filename, data):
    path = Path(filename)
    if not path.exists():
        print(f'[structured_data] SKIP (not found): {filename}')
        return

    html = path.read_text(encoding='utf-8')

    if 'application/ld+json' in html:
        print(f'[structured_data] already exists: {filename}')
        return

    page_url = f'{BASE_URL}/{filename}'
    today = datetime.now(JST).strftime('%Y-%m-%d')

    article = data.get('article', {})

    schema = {
        '@context': 'https://schema.org',
        '@graph': [
            {
                '@type': 'Article',
                'headline': article.get('headline', ''),
                'description': article.get('description', ''),
                'keywords': article.get('keywords', ''),
                'url': page_url,
                'datePublished': '2025-06-01',
                'dateModified': today,
                'author': {
                    '@type': 'Person',
                    'name': 'DRIVE GEAR LAB',
                    'url': BASE_URL,
                },
                'publisher': {
                    '@type': 'Organization',
                    'name': 'DRIVE GEAR LAB',
                    'url': BASE_URL,
                },
                'mainEntityOfPage': {
                    '@type': 'WebPage',
                    '@id': page_url,
                },
            },
            {
                '@type': 'BreadcrumbList',
                'itemListElement': [
                    {
                        '@type': 'ListItem',
                        'position': 1,
                        'name': 'DRIVE GEAR LAB',
                        'item': BASE_URL,
                    },
                    {
                        '@type': 'ListItem',
                        'position': 2,
                        'name': article.get('headline', ''),
                        'item': page_url,
                    },
                ],
            },
        ],
    }

    schema_tag = (
        '\n<script type="application/ld+json">\n'
        + json.dumps(schema, ensure_ascii=False, indent=2)
        + '\n</script>'
    )

    new_html = html.replace('</head>', schema_tag + '\n</head>', 1)
    path.write_text(new_html, encoding='utf-8')
    print(f'[structured_data] injected: {filename}')


# ============================================================
# 楽天API fetch
# ============================================================
def fetch_items(keyword):
    url = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601'
    params = {
        'applicationId': APP_ID,
        'affiliateId': AFFILIATE_ID,
        'keyword': keyword,
        'hits': 3,
        'sort': '-reviewCount',
        'imageFlag': 1,
        'format': 'json',
    }
    headers = {
        'Referer': 'https://www.drivegearlab.online/',
        'Origin': 'https://www.drivegearlab.online',
        'User-Agent': 'Mozilla/5.0',
    }
    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        print(f'[{keyword}] status={res.status_code}')
        data = res.json()
        if 'Items' not in data:
            print(f'[{keyword}] response={data}')
        return data.get('Items', [])
    except Exception as e:
        print(f'[{keyword}] error={e}')
        return []


# ============================================================
# サイトマップ・投稿下書き
# ============================================================
def update_sitemap():
    today = datetime.now(JST).strftime('%Y-%m-%d')
    pages = [
        ('', '1.0', 'weekly'),
        ('guide-dashcam-howto-choose.html', '0.9', 'monthly'),
        ('guide-summer-heat-countermeasure.html', '0.9', 'monthly'),
        ('guide-smartphone-holder-howto-choose.html', '0.9', 'monthly'),
        ('review-dashcam.html', '0.8', 'monthly'),
        ('review-earphones.html', '0.8', 'monthly'),
        ('review-sunshade.html', '0.8', 'monthly'),
        ('review-phone-holder.html', '0.8', 'monthly'),
        ('review-air-duster.html', '0.8', 'monthly'),
        ('review-battery.html', '0.8', 'monthly'),
        ('review-navi.html', '0.8', 'monthly'),
        ('review-coating.html', '0.8', 'monthly'),
        ('review-handy-fan.html', '0.8', 'monthly'),
        ('review-cigar-charger.html', '0.8', 'monthly'),
        ('review-trash-box.html', '0.8', 'monthly'),
        ('review-iphone17.html', '0.8', 'monthly'),
        ('review-clinview-gcoat.html', '0.8', 'monthly'),
        ('review-rinrei-wax.html', '0.8', 'monthly'),
        ('review-air-spencer.html', '0.8', 'monthly'),
        ('review-led-fog.html', '0.8', 'monthly'),
        ('review-led-headlight.html', '0.8', 'monthly'),
        ('review-prostaff-wax.html', '0.8', 'monthly'),
        ('review-yupiteru-radar.html', '0.8', 'monthly'),
        ('review-tpms.html', '0.8', 'monthly'),
        ('about.html', '0.4', 'yearly'),
        ('privacy-policy.html', '0.3', 'yearly'),
    ]
    urls = ''
    for page, priority, freq in pages:
        loc = f'{BASE_URL}/{page}'
        urls += f'''  <url>
    <loc>{loc}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>\n'''

    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}</urlset>'''
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)
    print('sitemap.xml updated')


def generate_post_draft():
    import random
    today = datetime.now(JST).strftime('%Y年%m月%d日')
    templates = [
        '🚗 ドライブをもっと快適に！\n\n車好き・ガジェット好きが実際に買って良かったアイテムだけを正直レビュー中📦\n\n楽天で買えるおすすめ車用品はこちら👇\nhttps://www.drivegearlab.online/\n\n#車好き #カーグッズ #楽天 #ガジェット好き',
        '💡 楽天で買える車用品、何を選べばいい？\n\nDRIVE GEAR LABでは実際に購入・使用したアイテムだけを忖度なしでレビュー中！\n\n👇 チェックしてみてください\nhttps://www.drivegearlab.online/\n\n#楽天 #車用品 #カーグッズ #ドライブ好き',
        '🔥 今週のおすすめ車用品をチェック！\n\nドライブレコーダー・スマホホルダー・モバイルバッテリーなど20アイテム以上掲載中🔍\n\nhttps://www.drivegearlab.online/\n\n#ドライブレコーダー #スマホホルダー #車載グッズ #楽天購入品',
        '☀️ 夏のドライブ対策してますか？\n\nサンシェード・ハンディファンなど暑さ対策グッズを楽天最安値でご紹介！\n\nhttps://www.drivegearlab.online/\n\n#夏 #車中暑対策 #サンシェード #楽天 #カーグッズ',
    ]
    draft = random.choice(templates)
    with open('post_draft.txt', 'w', encoding='utf-8') as f:
        f.write(f'【{today}の投稿候補】\n\n{draft}\n')
    print('post_draft.txt generated')


# ============================================================
# メイン処理
# ============================================================
def main():
    now = datetime.now(JST).strftime('%Y年%m月%d日 %H:%M')

    # ── 1. 楽天APIでauto-items.jsonを生成 ──
    items_data = []
    for kw in KEYWORDS:
        items = fetch_items(kw)
        print(f'[{kw}] {len(items)}件取得')
        for item in items:
            info = item.get('Item', item)
            img_url = info['mediumImageUrls'][0]['imageUrl'] if info.get('mediumImageUrls') else ''
            items_data.append({
                'name': info['itemName'][:40],
                'price': f"¥{info['itemPrice']:,}",
                'img': img_url,
                'url': info.get('affiliateUrl') or info.get('itemUrl', '#'),
            })

    output = {
        'updated_at': now,
        'items': items_data,
    }
    with open('auto-items.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f'auto-items.json generated ({len(items_data)}件)')

    # ── 2. 全レビューページに構造化データを挿入 ──
    print('\n--- 構造化データ挿入開始 ---')
    for filename, data in STRUCTURED_DATA.items():
        inject_structured_data(filename, data)
    print('--- 構造化データ挿入完了 ---\n')

    # ── 3. サイトマップ・投稿下書きを更新 ──
    update_sitemap()
    generate_post_draft()
    print('Done!')


if __name__ == '__main__':
    main()
