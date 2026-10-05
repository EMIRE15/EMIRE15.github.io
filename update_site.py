import os
import json
import re
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))

APP_ID = os.environ['RAKUTEN_APP_ID']
ACCESS_KEY = os.environ['RAKUTEN_ACCESS_KEY']
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
        'product': {
            'name': 'ドライブレコーダー 前後2カメラ SONYセンサー搭載',
            'price': '10980',
            'description': 'SONYセンサー採用で夜間も鮮明。前後同時録画で万が一の事故記録もバッチリ。駐車監視・Gセンサー搭載。',
        },
    },
    'review-earphones.html': {
        'article': {
            'headline': 'ワイヤレスイヤホン Bluetooth 5.4 ノイズキャンセリング 実機レビュー',
            'description': 'Bluetooth 5.4対応ワイヤレスイヤホンをドライブ視点でレビュー。ノイキャン性能・通話品質・バッテリーを正直評価。',
            'keywords': 'ワイヤレスイヤホン,ノイズキャンセリング,Bluetooth,楽天',
        },
        'product': {
            'name': 'ワイヤレスイヤホン Bluetooth 5.4 ノイズキャンセリング',
            'price': '2780',
            'description': '最新Bluetooth 5.4対応でドライブ中も途切れにくい。ノイキャン搭載で車内のロードノイズをカット。',
        },
    },
    'review-sunshade.html': {
        'article': {
            'headline': '傘型サンシェード CREAS WING 実機レビュー',
            'description': 'ワンタッチ傘型サンシェードを実際に使ってレビュー。車内温度の実測データ・サイズ選びガイド付き。',
            'keywords': 'サンシェード,傘型,車内温度,楽天,CREAS WING',
        },
        'product': {
            'name': '傘型サンシェード 全7サイズ 年間ランキング1位【CREAS WING】',
            'price': '1980',
            'description': 'ワンタッチで開閉できる傘型タイプ。XS〜XXLまで全7サイズ展開。夏の車内温度上昇を強力カット。',
        },
    },
    'review-phone-holder.html': {
        'article': {
            'headline': '真空吸着マグネット スマホホルダー MagSafe対応 実機レビュー',
            'description': '真空吸着+マグネットのスマホホルダーをレビュー。固定力・着脱のしやすさ・MagSafe対応を正直評価。',
            'keywords': 'スマホホルダー,MagSafe,マグネット,車載,楽天',
        },
        'product': {
            'name': '真空吸着マグネット スマホホルダー MagSafe対応・360°回転',
            'price': '2180',
            'description': '真空吸着＋超強力マグネットのW固定でズレ・落下ゼロ。片手ワンタッチ着脱。3way対応。',
        },
    },
    'review-air-duster.html': {
        'article': {
            'headline': '充電式エアーダスター 200000RPM 実機レビュー',
            'description': '充電式エアーダスターを車内清掃・ガジェット掃除で実際に使ってレビュー。風力・バッテリー持ちを正直評価。',
            'keywords': 'エアーダスター,充電式,車内清掃,楽天',
        },
        'product': {
            'name': '充電式エアーダスター ブロワー 200000RPM・4段階風量調整',
            'price': '5980',
            'description': 'コンプレッサー不要で200000RPMの圧倒的な風力。車内清掃・エアコンフィルター掃除に大活躍。',
        },
    },
    'review-battery.html': {
        'article': {
            'headline': '大容量モバイルバッテリー 23600mAh 4本ケーブル内蔵 実機レビュー',
            'description': '4本ケーブル内蔵モバイルバッテリーを実際に計測してレビュー。実容量・充電速度・ドライブでの使い勝手を正直評価。',
            'keywords': 'モバイルバッテリー,大容量,PD充電,ケーブル内蔵,楽天',
        },
        'product': {
            'name': '大容量モバイルバッテリー 23600mAh PD22.5W・4本ケーブル内蔵',
            'price': '2980',
            'description': '4本のケーブルが本体内蔵でケーブル忘れゼロ。PD22.5W急速充電対応。PSE認証済で安心。',
        },
    },
    'review-navi.html': {
        'article': {
            'headline': 'ATOTO A6 カーナビ 9インチ CarPlay対応 実機レビュー',
            'description': 'Apple CarPlay・Android Auto対応カーナビをレビュー。iPhoneとの連携・画面の見やすさ・取り付けを正直評価。',
            'keywords': 'カーナビ,CarPlay,Android Auto,9インチ,楽天',
        },
        'product': {
            'name': 'ATOTO A6 カーナビ 9インチ CarPlay・Android Auto対応',
            'price': '39300',
            'description': 'Apple CarPlay・Android Auto対応の2DINカーナビ。iPhoneのマップやSpotifyをそのまま9インチ大画面で使える。',
        },
    },
    'review-coating.html': {
        'article': {
            'headline': 'ガラスコーティング剤 超撥水スプレータイプ 実機レビュー',
            'description': 'スプレー式ガラスコーティング剤を実際に使ってレビュー。撥水効果・耐久性・施工のしやすさを正直評価。',
            'keywords': 'ガラスコーティング,撥水,スプレー,カーケア,楽天',
        },
        'product': {
            'name': 'ガラスコーティング剤 超撥水スプレータイプ 3ヶ月持続',
            'price': '1990',
            'description': 'スプレーして拭くだけの簡単施工で約3ヶ月の艶・撥水効果が持続。タオル・スポンジ付属。',
        },
    },
    'review-handy-fan.html': {
        'article': {
            'headline': '車載ハンディファン おすすめ3選 選び方ガイド実機レビュー',
            'description': '車載ハンディファンを実際に使ってレビュー。USB給電・クリップ式・首振り機能など選び方のポイントも解説。',
            'keywords': 'ハンディファン,車載,USB,夏,冷却,楽天',
        },
        'product': {
            'name': 'ハンディファン 冷却プレート付き 120段階・5000mAh大容量',
            'price': '2780',
            'description': 'テレビ紹介の話題商品。冷却プレートが直接肌を冷やすため夏の車移動・屋外に最適。',
        },
    },
    'review-cigar-charger.html': {
        'article': {
            'headline': 'シガーソケット充電器 USB-C PD対応 おすすめ3選 実機レビュー',
            'description': 'シガーソケット充電器を実際に計測してレビュー。USB-C PD対応・急速充電・発熱を正直評価。',
            'keywords': 'シガーソケット充電器,USB-C,PD充電,カーチャージャー,楽天',
        },
        'product': {
            'name': 'シガーソケット充電器 巻き取りリール式 4ポート・PD急速充電対応',
            'price': '2480',
            'description': '楽天1位200冠達成の大人気カーチャージャー。リール式で収納スッキリ。4台同時充電可能。',
        },
    },
    'review-trash-box.html': {
        'article': {
            'headline': '車用ゴミ箱 折りたたみ式 PUレザー LED付き 実機レビュー',
            'description': '車用折りたたみゴミ箱を3ヶ月使ってレビュー。取り付けやすさ・容量・LEDの実用性を正直評価。',
            'keywords': '車用ゴミ箱,折りたたみ,PUレザー,車内インテリア,楽天',
        },
        'product': {
            'name': '車用ゴミ箱 折りたたみ式 PUレザー・フック固定・LED付き',
            'price': '1980',
            'description': '多車種対応フックで後部座席にスッキリ固定。PUレザー素材でおしゃれ。LED付きで夜間も使いやすい。',
        },
    },
    'review-iphone17.html': {
        'article': {
            'headline': 'iPhone 17 ドライブ・カーライフ視点 徹底レビュー',
            'description': 'iPhone 17をCarPlay・MagSafe・ナビ活用などカーライフ視点でレビュー。車乗りが気になるポイントを正直評価。',
            'keywords': 'iPhone 17,CarPlay,MagSafe,楽天モバイル',
        },
        'product': {
            'name': 'Apple iPhone 17 SIMフリー 楽天モバイル',
            'price': '176800',
            'description': '楽天モバイルで購入できるiPhone 17 SIMフリー端末。MagSafe対応でスマホホルダーとの相性も抜群。',
        },
    },
    'review-clinview-gcoat.html': {
        'article': {
            'headline': 'クリンビュー Gコート ウルトラタフドロップ 実機レビュー',
            'description': 'クリンビュー Gコートを2ヶ月使ってレビュー。撥水効果・耐久性・施工のしやすさを正直評価。',
            'keywords': 'クリンビュー,Gコート,ガラスコーティング,撥水,楽天',
        },
        'product': {
            'name': 'クリンビュー Gコート ウルトラタフドロップ 80ml',
            'price': '1780',
            'description': 'オートバックス取扱いの本格ガラスコーティング剤。超撥水効果でボディの水弾きが段違い。',
        },
    },
    'review-rinrei-wax.html': {
        'article': {
            'headline': 'リンレイ ガラス系ハイブリッドWAX Gガード固形 実機レビュー',
            'description': 'リンレイ公式ガラス系WAXを複数色の車に施工してレビュー。艶・撥水・耐久性を正直評価。',
            'keywords': 'リンレイ,ガラス系WAX,カーワックス,固形,楽天',
        },
        'product': {
            'name': 'リンレイ ガラス系ハイブリッドWAX Gガード 固形',
            'price': '1738',
            'description': 'ガラス系成分×WAXのハイブリッド処方で艶と撥水を両立。固形タイプで施工しやすい。',
        },
    },
    'review-air-spencer.html': {
        'article': {
            'headline': 'エアースペンサー ピンクシャワー 実機レビュー',
            'description': 'エアースペンサー ピンクシャワーを1ヶ月使ってレビュー。香りの強さ・持続期間・使い心地を正直評価。',
            'keywords': 'エアースペンサー,ピンクシャワー,カーフレグランス,車内芳香剤,楽天',
        },
        'product': {
            'name': 'エアースペンサー カートリッジ ピンクシャワー',
            'price': '598',
            'description': '栄光社の定番カーフレグランス。甘さ控えめのフローラル系の香りで車内を爽やかに演出。',
        },
    },
    'review-led-fog.html': {
        'article': {
            'headline': 'HID屋 LEDフォグランプ Vシリーズ 2色切り替え 実機レビュー',
            'description': 'HID屋 LEDフォグランプを実際に取り付けてレビュー。明るさ・色切り替え・車検対応の実態を正直評価。',
            'keywords': 'HID屋,LEDフォグランプ,2色切り替え,車検対応,楽天',
        },
        'product': {
            'name': 'HID屋 LEDフォグランプ 2色切り替え Vシリーズ 車検対応',
            'price': '9860',
            'description': '4色切り替え可能。5600lm〜9900lmの圧倒的明るさ。H8/H11/H16/HB4対応。',
        },
    },
    'review-led-headlight.html': {
        'article': {
            'headline': 'HID屋 H4 LEDヘッドライト Qシリーズ 爆光 実機レビュー',
            'description': 'HID屋 H4 LEDヘッドライトを実際に取り付けてレビュー。68400cdの明るさと車検対応を正直評価。',
            'keywords': 'HID屋,LEDヘッドライト,H4,爆光,車検対応,楽天',
        },
        'product': {
            'name': 'HID屋 H4 LEDヘッドライト Qシリーズ 68400cd 爆光 車検対応',
            'price': '15980',
            'description': '68400cdの特注高性能LEDチップ搭載。H4 Hi/Lo切り替え対応でポン付け換装が可能。',
        },
    },
    'review-prostaff-wax.html': {
        'article': {
            'headline': 'プロスタッフ CCウォーターゴールド 300ml 実機レビュー',
            'description': 'プロスタッフ CCウォーターゴールドを3色の車に施工してレビュー。撥水効果・艶・耐久性を正直評価。',
            'keywords': 'プロスタッフ,CCウォーターゴールド,ガラスコーティング,楽天',
        },
        'product': {
            'name': 'プロスタッフ CCウォーターゴールド 300ml ガラス系コーティング',
            'price': '2180',
            'description': 'CM放映の人気カーコーティング剤。スプレーして拭くだけの超簡単施工。全色対応。',
        },
    },
    'review-yupiteru-radar.html': {
        'article': {
            'headline': 'ユピテル YK-2200 GPSレーダー探知機 実機レビュー',
            'description': 'ユピテル YK-2200を3ヶ月使ってレビュー。オービス対応・音声案内の精度・取り付けやすさを正直評価。',
            'keywords': 'ユピテル,GPSレーダー,オービス,レーダー探知機,楽天',
        },
        'product': {
            'name': 'ユピテル YK-2200 GPSレーダー オービス対応 最新データ搭載',
            'price': '36970',
            'description': 'オートバックス取扱いのユピテル製GPSレーダー探知機。最新の取締りポイントデータを搭載。',
        },
    },
    'review-tpms.html': {
        'article': {
            'headline': 'タイヤ空気圧モニター TPMS ソーラー充電 楽天1位 実機レビュー',
            'description': 'タイヤ空気圧モニターを3ヶ月使ってレビュー。4本リアルタイム監視・警告精度・ソーラー充電の実力を正直評価。',
            'keywords': 'タイヤ空気圧モニター,TPMS,ソーラー充電,安全運転,楽天',
        },
        'product': {
            'name': 'タイヤ空気圧モニター TPMS 音声案内 ワイヤレス ソーラー充電',
            'price': '7980',
            'description': '楽天1位の人気タイヤ空気圧センサー。リアルタイムで4本の空気圧・温度を音声で知らせてくれる。',
        },
    },
}

# ============================================================
# 商品画像URL（Product schemaのimage必須項目。index.htmlのカード画像と同一）
# ============================================================
PRODUCT_IMAGES = {
    "review-dashcam.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/yumenomori/cabinet/09856724/h26yh4780.jpg",
    "review-earphones.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/gracevally/cabinet/09355687/09355695/12855263/x1front-2026old.jpg",
    "review-sunshade.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/creaswing/cabinet/cwrt50/car-311-0005.jpg",
    "review-phone-holder.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/creamchic/cabinet/smp/smp_004/smp-0045_00.jpg",
    "review-air-duster.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/gmy-japan/cabinet/250902/1011.jpg",
    "review-battery.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/furumiyashop/cabinet/zt/p60-2380-2.jpg",
    "review-navi.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/famous2017/cabinet/08758553/imgrc0095748973.jpg",
    "review-coating.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/zepancar/cabinet/10636932/zt/zepancar-spl-ss.jpg",
    "review-handy-fan.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/azusa/cabinet/h8fan/h08pro_main01.jpg",
    "review-cigar-charger.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/lohas1/cabinet/10463166/10803904/imgrc0106897964.jpg",
    "review-trash-box.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/creaswing/cabinet/cwrt30/car-0011.jpg",
    "review-iphone17.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/rakutenmobile-store/cabinet/product/iphone-17/pc/17-d-m.jpg",
    "review-clinview-gcoat.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/autobacs-ec/cabinet/image/10951522/01751081_1.jpg",
    "review-rinrei-wax.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/rinreiwax/cabinet/car/339014.jpg",
    "review-air-spencer.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/autobacs-ec/cabinet/image/12821157/00552265_1.jpg",
    "review-led-fog.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/auc-tradingtrade/cabinet/foglamp/v_fog/r_v_fog_h8-1.jpg",
    "review-led-headlight.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/auc-tradingtrade/cabinet/lh/tt007_0017/r_search_head_q_h4.jpg",
    "review-prostaff-wax.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/prostaff-shop/cabinet/s121_p.jpg",
    "review-yupiteru-radar.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/autobacs-ec/cabinet/image/12821157/01844289_1.jpg",
    "review-tpms.html": "https://thumbnail.image.rakuten.co.jp/@0_mall/rise0828/cabinet/5065456-0.jpg"
}

# ============================================================
# 楽天商品コード（価格の日次自動取得用）
# item_code: 楽天API itemCode / url_path: 当サイトのリンク先。APIの返却itemUrlに
# url_pathが含まれない場合は別商品とみなし、STRUCTURED_DATAの固定価格を使う
# ============================================================
# Product schemaのbrand(メーカー名)。ノーブランド品は登録しない(brand自体を出力しない)
PRODUCT_BRANDS = {
    'review-sunshade.html': 'CREAS WING',
    'review-navi.html': 'ATOTO',
    'review-iphone17.html': 'Apple',
    'review-clinview-gcoat.html': 'クリンビュー',
    'review-rinrei-wax.html': 'リンレイ',
    'review-air-spencer.html': 'エアースペンサー',
    'review-led-fog.html': 'HID屋',
    'review-led-headlight.html': 'HID屋',
    'review-prostaff-wax.html': 'プロスタッフ',
    'review-yupiteru-radar.html': 'ユピテル',
}


PRODUCT_RAKUTEN = {
    "review-dashcam.html": {
        "item_code": "yumenomori:10000183",
        "url_path": "yumenomori/b1jlh26he"
    },
    "review-earphones.html": {
        "item_code": "gracevally:10000003",
        "url_path": "gracevally/grace-x1"
    },
    "review-sunshade.html": {
        "item_code": "creaswing:10000036",
        "url_path": "creaswing/car-311-0005"
    },
    "review-phone-holder.html": {
        "item_code": "creamchic:10000255",
        "url_path": "creamchic/gs-smp-0045"
    },
    "review-air-duster.html": {
        "item_code": "gmy-japan:10000080",
        "url_path": "gmy-japan/s-p70"
    },
    "review-battery.html": {
        "item_code": "furumiyashop:10000146",
        "url_path": "furumiyashop/cdb00p60"
    },
    "review-navi.html": {
        "item_code": "famous2017:10000689",
        "url_path": "famous2017/f7g210pe-al"
    },
    "review-coating.html": {
        "item_code": "zepancar:10000005",
        "url_path": "zepancar/quick-coating"
    },
    "review-handy-fan.html": {
        "item_code": "azusa:10000130",
        "url_path": "azusa/0302"
    },
    "review-cigar-charger.html": {
        "item_code": "lohas1:10011400",
        "url_path": "lohas1/ph-ptsx6-gm"
    },
    "review-trash-box.html": {
        "item_code": "creaswing:10000209",
        "url_path": "creaswing/car-0011"
    },
    "review-iphone17.html": {
        "item_code": "rakutenmobile-store:10001785",
        "url_path": "rakutenmobile-store/iphone-17"
    },
    "review-clinview-gcoat.html": {
        "item_code": "autobacs-ec:10057014",
        "url_path": "autobacs-ec/4974672209244"
    },
    "review-rinrei-wax.html": {
        "item_code": "rinreiwax:10002427",
        "url_path": "rinreiwax/339014"
    },
    "review-air-spencer.html": {
        "item_code": "autobacs-ec:10031111",
        "url_path": "autobacs-ec/4970301590424"
    },
    "review-led-fog.html": {
        "item_code": "auc-tradingtrade:10003942",
        "url_path": "auc-tradingtrade/v_fog"
    },
    "review-led-headlight.html": {
        "item_code": "auc-tradingtrade:10000295",
        "url_path": "auc-tradingtrade/tt007_0017"
    },
    "review-prostaff-wax.html": {
        "item_code": "prostaff-shop:10000000",
        "url_path": "prostaff-shop/s121"
    },
    "review-yupiteru-radar.html": {
        "item_code": "autobacs-ec:10090584",
        "url_path": "autobacs-ec/4968543130942"
    },
    "review-tpms.html": {
        "item_code": "rise0828:10000055",
        "url_path": "rise0828/b1t3cthe"
    }
}

BASE_URL = 'https://drivegearlab.online'

# ============================================================
# 構造化データ挿入関数（Article + Product + Review + Breadcrumb）
# ============================================================
def inject_structured_data(filename, data):
    path = Path(filename)
    if not path.exists():
        print(f'[structured_data] SKIP (not found): {filename}')
        return

    html = path.read_text(encoding='utf-8')
    page_url = f'{BASE_URL}/{filename}'
    today = datetime.now(JST).strftime('%Y-%m-%d')

    article = data.get('article', {})
    product = data.get('product', {})

    graph = [
        {
            '@type': 'Article',
            'headline': article.get('headline', ''),
            'description': article.get('description', ''),
            'keywords': article.get('keywords', ''),
            'url': page_url,
            'datePublished': '2025-06-01',
            'dateModified': today,
            'author': {
                '@type': 'Organization',
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
    ]

    # Product + Review スキーマを追加
    if product:
        graph.append({
            '@type': 'Product',
            'name': product.get('name', ''),
            'description': product.get('description', ''),
            'url': page_url,
            'offers': {
                '@type': 'Offer',
                'price': product.get('price', '0'),
                'priceCurrency': 'JPY',
                'availability': product.get('availability', 'https://schema.org/InStock'),
                'url': page_url,
            },
            'review': {
                '@type': 'Review',
                'reviewRating': {
                    '@type': 'Rating',
                    'ratingValue': '4.5',
                    'bestRating': '5',
                    'worstRating': '1',
                },
                'author': {
                    '@type': 'Organization',
                    'name': 'DRIVE GEAR LAB',
                },
                'reviewBody': article.get('description', ''),
            },
            'aggregateRating': {
                '@type': 'AggregateRating',
                'ratingValue': '4.5',
                'reviewCount': '1',
                'bestRating': '5',
                'worstRating': '1',
            },
        })

    # Product schemaにimageを付与（欠落するとGSC販売者のリスティングで無効判定になる）
    if product:
        img = product.get('image') or PRODUCT_IMAGES.get(filename)
        if img:
            graph[-1]['image'] = img
        else:
            print(f'[structured_data] WARNING: image未設定: {filename}')
        # brandはメーカーが明確な商品のみ(サイト名をbrandにすると自己レビュー扱いのリスク)
        brand = PRODUCT_BRANDS.get(filename)
        if brand:
            graph[-1]['brand'] = {'@type': 'Brand', 'name': brand}

    schema = {
        '@context': 'https://schema.org',
        '@graph': graph,
    }

    schema_tag = (
        '\n<script type="application/ld+json">\n'
        + json.dumps(schema, ensure_ascii=False, indent=2)
        + '\n</script>'
    )

    # 既存のld+jsonを削除して新しいものに置き換え
    html = re.sub(
        r'\n?<script type="application/ld\+json">.*?</script>\n?',
        '',
        html,
        flags=re.DOTALL,
    )

    new_html = html.replace('</head>', schema_tag + '\n</head>', 1)
    path.write_text(new_html, encoding='utf-8')
    print(f'[structured_data] updated: {filename}')


# ============================================================
# 楽天API fetch
# ============================================================
def fetch_items(keyword):
    url = 'https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701'
    params = {
        'applicationId': APP_ID,
        'accessKey': ACCESS_KEY,
        'affiliateId': AFFILIATE_ID,
        'keyword': keyword,
        'hits': 3,
        'sort': '-reviewCount',
        'imageFlag': 1,
        'format': 'json',
    }
    headers = {
        'Referer': 'https://drivegearlab.online/',
        'Origin': 'https://drivegearlab.online',
    }
    try:
        import time
        time.sleep(2)
        res = requests.get(url, params=params, headers=headers, timeout=10)
        print(f'[{keyword}] status={res.status_code}')
        data = res.json()
        if 'Items' not in data:
            print(f'[{keyword}] response={data}')
        return data.get('Items', [])
    except Exception as e:
        print(f'[{keyword}] error={e}')
        return []


def fetch_item_price(filename):
    """楽天APIで商品の現在価格・在庫を取得。失敗・商品不一致時はNoneを返す"""
    info = PRODUCT_RAKUTEN.get(filename)
    if not info:
        return None
    url = 'https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701'
    params = {
        'applicationId': APP_ID,
        'accessKey': ACCESS_KEY,
        'itemCode': info['item_code'],
        'availability': 0,  # 売り切れ商品も取得対象にする
        'hits': 1,
        'format': 'json',
    }
    headers = {
        'Referer': 'https://drivegearlab.online/',
        'Origin': 'https://drivegearlab.online',
    }
    try:
        import time
        time.sleep(1.5)
        res = requests.get(url, params=params, headers=headers, timeout=10)
        items = res.json().get('Items', [])
        if not items:
            print(f'[price] {filename}: 取得0件 status={res.status_code}')
            return None
        item = items[0].get('Item', items[0])
        item_url = item.get('itemUrl', '')
        if info['url_path'] not in item_url:
            print(f'[price] {filename}: 商品不一致のためスキップ itemUrl={item_url}')
            return None
        price = int(item['itemPrice'])
        in_stock = item.get('availability', 1) == 1
        return price, in_stock
    except Exception as e:
        print(f'[price] {filename}: error={e}')
        return None


def sync_page_prices():
    """各レビューページの購入ボックスの価格表示を、STRUCTURED_DATAの現在価格に揃える"""
    changed = 0
    for filename, data in STRUCTURED_DATA.items():
        path = Path(filename)
        price = data['product'].get('price')
        if not path.exists() or not price:
            continue
        out = 'OutOfStock' in data['product'].get('availability', '')
        html = path.read_text(encoding='utf-8')
        # 価格を表示している購入ボックスだけを対象にする(「楽天で価格を確認」表示のページは触らない)
        new_html = re.sub(
            r'(<div class="(?:buy|product)-price">)¥[\d,]+〜?\s*(?:<span>[^<]*</span>)?(</div>)',
            lambda m: f'{m.group(1)}¥{int(price):,}<span>{"在庫切れ" if out else "税込"}</span>{m.group(2)}',
            html,
        )
        if new_html != html:
            path.write_text(new_html, encoding='utf-8')
            changed += 1
    print(f'[price] レビューページ購入ボックス価格 更新{changed}件')


def sync_index_prices():
    """index.htmlのカード価格を、STRUCTURED_DATAの現在価格(API取得後)に揃える"""
    path = Path('index.html')
    if not path.exists():
        return
    html = path.read_text(encoding='utf-8')
    changed = 0
    for filename, data in STRUCTURED_DATA.items():
        price = data['product'].get('price')
        if not price:
            continue
        out = 'OutOfStock' in data['product'].get('availability', '')
        new_inner = f'¥{int(price):,}<span class="price-note">{"在庫切れ" if out else "税込"}</span>'
        pattern = re.compile(
            r'(<div class="card-img-wrap"><a href="' + re.escape(filename) + r'">'
            r'(?:(?!<div class="card")[\s\S])*?<div class="card-price">)'
            r'((?:(?!</div>)[\s\S])*)(</div>)'
        )
        m = pattern.search(html)
        # 価格を表示していないカード(「楽天で価格確認」など)はそのままにする
        if not m or '¥' not in m.group(2):
            continue
        if m.group(2) != new_inner:
            html = html[:m.start(2)] + new_inner + html[m.end(2):]
            changed += 1
    if changed:
        path.write_text(html, encoding='utf-8')
    print(f'[price] index.htmlカード価格 更新{changed}件')


# ============================================================
# サイトマップ・投稿下書き
# ============================================================
def update_sitemap():
    today = datetime.now(JST).strftime('%Y-%m-%d')

    # 除外するHTMLファイル（テンプレート・404など、公開ページでないもの）
    EXCLUDE = {'404.html'}
    # Google Search Console等のサイト所有権確認用ファイル（google1234...html）は
    # 検索結果に出す意味がないため、パターンで自動除外する
    def is_verification_file(name):
        return name.startswith('google') and name[6:-5].isalnum()

    # 優先度を上げたい主要ページ（それ以外は自動でmonthly/0.7）
    PRIORITY_OVERRIDE = {
        'index.html': ('1.0', 'weekly'),
        'about.html': ('0.4', 'yearly'),
        'privacy-policy.html': ('0.3', 'yearly'),
    }

    # リポジトリ直下の全 .html ファイルを自動スキャン（ハードコードしない）
    html_files = sorted(
        f for f in os.listdir('.')
        if f.endswith('.html') and f not in EXCLUDE and not is_verification_file(f)
    )

    pages = []
    for f in html_files:
        page = '' if f == 'index.html' else f
        priority, freq = PRIORITY_OVERRIDE.get(f, ('0.7', 'monthly'))
        pages.append((page, priority, freq))

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
    print(f'sitemap.xml updated ({len(pages)} URLs, auto-scanned)')


def generate_post_draft():
    import random
    today = datetime.now(JST).strftime('%Y年%m月%d日')
    templates = [
        '🚗 ドライブをもっと快適に！\n\n車好き・ガジェット好きが実際に買って良かったアイテムだけを正直レビュー中📦\n\n楽天で買えるおすすめ車用品はこちら👇\nhttps://drivegearlab.online/\n\n#車好き #カーグッズ #楽天 #ガジェット好き',
        '💡 楽天で買える車用品、何を選べばいい？\n\nDRIVE GEAR LABでは実際に購入・使用したアイテムだけを忖度なしでレビュー中！\n\n👇 チェックしてみてください\nhttps://drivegearlab.online/\n\n#楽天 #車用品 #カーグッズ #ドライブ好き',
        '🔥 今週のおすすめ車用品をチェック！\n\nドライブレコーダー・スマホホルダー・モバイルバッテリーなど20アイテム以上掲載中🔍\n\nhttps://drivegearlab.online/\n\n#ドライブレコーダー #スマホホルダー #車載グッズ #楽天購入品',
        '☀️ 夏のドライブ対策してますか？\n\nサンシェード・ハンディファンなど暑さ対策グッズを楽天最安値でご紹介！\n\nhttps://drivegearlab.online/\n\n#夏 #車中暑対策 #サンシェード #楽天 #カーグッズ',
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
            item_url = (info.get('affiliateUrl') or info.get('itemUrl', '#')).replace(' ', '')
            items_data.append({
                'name': info['itemName'][:40],
                'price': f"¥{info['itemPrice']:,}",
                'img': img_url,
                'url': item_url,
            })

    output = {
        'updated_at': now,
        'items': items_data,
    }
    if items_data:
        with open('auto-items.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f'auto-items.json generated ({len(items_data)}件)')
    else:
        # API障害時に「今日のおすすめ」を空で上書きしない(前回分を残す)
        print('::warning::楽天APIから0件 — auto-items.jsonは前回分を維持')

    # ── 2. 全レビューページに構造化データを挿入・更新 ──
    print('\n--- 構造化データ挿入開始 ---')
    updated, fallback = 0, []
    for filename, data in STRUCTURED_DATA.items():
        result = fetch_item_price(filename)
        if result:
            price, in_stock = result
            old = data['product'].get('price')
            data['product']['price'] = str(price)
            data['product']['availability'] = (
                'https://schema.org/InStock' if in_stock else 'https://schema.org/OutOfStock'
            )
            if old != str(price):
                print(f'[price] {filename}: {old} -> {price}')
            updated += 1
        else:
            fallback.append(filename)
    print(f'[price] API取得 {updated}件 / 固定価格フォールバック {len(fallback)}件 {fallback}')
    if updated == 0 and fallback:
        print('::warning::楽天API価格取得が全件失敗 — 固定価格で表示中')
    for filename, data in STRUCTURED_DATA.items():
        inject_structured_data(filename, data)
    sync_index_prices()
    sync_page_prices()
    print('--- 構造化データ挿入完了 ---\n')

    # ── 3. サイトマップ・投稿下書きを更新 ──
    update_sitemap()
    generate_post_draft()
    print('Done!')


if __name__ == '__main__':
    main()
