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
            'headline': '前後2カメラ SONYセンサー搭載ドラレコの特徴・スペック解説｜夜間画質・駐車監視は？',
            'description': 'SONYセンサー搭載の前後2カメラドライブレコーダーを、公表スペックから解説。夜間画質・取り付け・駐車監視のポイントと注意点まとめ。',
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
            'headline': 'ワイヤレスイヤホン Bluetooth5.4 ノイキャン搭載の特徴・スペック解説｜ドライブ中の通話に使える？',
            'description': 'Bluetooth5.4・ノイズキャンセリング・デュアルマイク搭載の低価格ワイヤレスイヤホンを公表スペックから解説。ドライブ中のハンズフリー通話での使いどころと注意点まとめ。',
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
            'headline': 'CREAS WING 傘型サンシェードの口コミ・評判とサイズの選び方',
            'description': '楽天レビュー1万4千件超・★4.46のCREAS WING 傘型サンシェード。改良型と強化版の違い、全7サイズの寸法と選び方、傘型ならではのメリット・注意点をまとめました。',
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
            'headline': '真空吸着マグネットスマホホルダー MagSafe対応の特徴・スペック解説｜3way設置と選び方',
            'description': '真空吸着＋MagSafe対応のスマホホルダーを公表スペックから解説。ダッシュボード・ドリンクホルダー・エアコン口の3way設置の違いと、Androidでの使い方、購入前の注意点まとめ。',
            'keywords': 'スマホホルダー,MagSafe,マグネット,車載,楽天',
        },
        'product': {
            'name': '真空吸着マグネット スマホホルダー MagSafe対応・360°回転',
            'price': '2180',
            'description': '真空吸着＋超強力マグネットのW固定でズレ・落下を防ぐ設計。片手ワンタッチ着脱。3way対応。',
        },
    },
    'review-air-duster.html': {
        'article': {
            'headline': '充電式エアーダスター200000RPMの特徴・スペック解説｜車内清掃に使える？選ぶ前の注意点',
            'description': '充電式エアーダスター200000RPM・4段階調整モデルを公表スペックから解説。車内清掃・エアコン吹き出し口・PC掃除での使いどころと、騒音・バッテリーなどの注意点まとめ。',
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
            'headline': '23600mAhはスマホ何回分？iPhone約4回が目安｜ケーブル内蔵モバイルバッテリーの特徴・スペック解説',
            'description': '23600mAhのモバイルバッテリーでスマホは何回充電できる？一般的な変換ロスを考えると使える容量は約14,000mAh前後、iPhone 15 Proなら約4回が目安。4本ケーブル内蔵モデルの特徴と車での使い方を解説。',
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
            'headline': 'ATOTO A6 カーナビ9インチの特徴・スペック解説｜CarPlay対応の後付けナビは純正の代わりになるか？',
            'description': 'CarPlay・Android Auto対応の後付けナビATOTO A6 9インチを公表スペックから解説。取り付けに必要なもの、純正ナビとの違い、購入前の注意点まとめ。',
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
            'headline': 'ガラスコーティング剤スプレータイプの特徴・スペック解説｜3ヶ月持続は本当？施工手順と注意点',
            'description': '「約3ヶ月持続」をうたうスプレー式ガラスコーティング剤を公表スペックから解説。施工手順、持続期間を左右する条件、専門店コーティングとの違いまとめ。',
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
            'headline': '車載ハンディファンおすすめ比較｜クリップ式・首振りなど選び方ガイド',
            'description': '車載ハンディファンを電源方式・取り付け方式・首振り機能など公表スペックで比較。クリップ式USB-AとUSB-C自動首振りモデルの違いと選び方を解説。',
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
            'headline': 'シガーソケット充電器おすすめ比較｜USB-C PD対応モデルの選び方と注意点',
            'description': 'シガーソケット充電器をUSB-C PD対応・2ポート・QC3.0など公表スペックで比較。iPhone・Android別の選び方と、発熱・安全機能など購入前の注意点を解説。',
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
            'headline': '車用ゴミ箱 折りたたみ式 PUレザー LED付きの特徴・スペック解説｜取り付け方と選び方',
            'description': '車用ゴミ箱 折りたたみ式PUレザー（LED付き）を公表スペックから解説。ヘッドレストへの取り付け方、容量、LED・折りたたみ機能と購入前の注意点まとめ。',
            'keywords': '車用ゴミ箱,折りたたみ,PUレザー,車内インテリア,楽天',
        },
        'product': {
            'name': '車用ゴミ箱 折りたたみ式 PUレザー・フック固定・LED付き',
            'price': '1980',
            'description': '多車種対応フックで後部座席にスッキリ固定。PUレザー素材でおしゃれ。LED付きで夜間も使いやすい。',
        },
    },
    'review-clinview-gcoat.html': {
        'article': {
            'headline': 'クリンビュー Gコート ウルトラタフドロップの特徴・スペック解説｜撥水力と持続期間の目安',
            'description': 'クリンビュー Gコート ウルトラタフドロップを公表スペックから解説。スプレー式ガラス系コーティングの施工手順、持続期間の目安、向いている人と注意点まとめ。',
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
            'headline': 'リンレイ ガラス系ハイブリッドWAX Gガード固形の特徴・スペック解説｜艶と撥水を両立するWAX',
            'description': 'リンレイ ガラス系ハイブリッドWAX Gガード固形を公表スペックから解説。ガラス系×WAXの特徴、施工手順と手間、スプレータイプとの違いまとめ。',
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
            'headline': 'エアースペンサー ピンクシャワーはどんな香り？特徴と持続期間の目安（メーカー30〜45日）',
            'description': 'エアースペンサー ピンクシャワーはどんな香り？石鹸系フローラルと案内される香りの特徴、メーカー目安30〜45日の持続期間、エアコン吹き出し口での使い方とカートリッジ交換のポイントをまとめました。',
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
            'headline': 'HID屋 LEDフォグランプ Vシリーズの特徴・スペック解説｜2色切り替えと車検対応のポイント',
            'description': 'HID屋 LEDフォグランプ Vシリーズを公表スペックから解説。ホワイト・イエローなどの色切り替え、車検対応になる色、取り付け前に確認すべきバルブ規格まとめ。',
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
            'headline': 'HID屋 H4 LEDヘッドライト Qシリーズの特徴・スペック解説｜68400cdの明るさと車検対応の注意点',
            'description': 'HID屋 H4 LEDヘッドライト Qシリーズを公表スペックから解説。68400cdの明るさ、車検対応の考え方と光軸調整、取り付け前に確認すべきポイントまとめ。',
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
            'headline': 'プロスタッフ CCウォーターゴールド 300mlの特徴・スペック解説｜撥水力・持続期間と使い方',
            'description': 'プロスタッフ CCウォーターゴールドを公表スペックから解説。ボディ・窓・樹脂に使えるガラス系スプレーコーティングの特徴、持続期間の目安、向いている人まとめ。',
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
            'headline': 'ユピテル YK-2200の口コミ・評判と特徴まとめ｜取り付け方法・できること',
            'description': 'ユピテル YK-2200の楽天口コミ（★4.71）と特徴をまとめました。レーザー式・Kバンドオービスの識別警報、誤警報を減らすセーフティーモード、4.0インチ液晶、無線LANでのデータ更新、取り付け方法まで解説。',
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
            'headline': 'タイヤ空気圧モニター TPMS ソーラー充電（楽天1位）の特徴・スペック解説｜取り付けと選び方',
            'description': '楽天1位のタイヤ空気圧モニター（TPMS）を公表スペックから解説。4本リアルタイム監視・音声警告・ソーラー充電の仕組みと、取り付け・ペアリングの注意点まとめ。',
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

    # Product スキーマを追加（実機レビューではないためReview/AggregateRatingは付けない）
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
        '🚗 ドライブをもっと快適に！\n\n車好き・ガジェット好き向けに、楽天で買える車用品をスペック比較でわかりやすく解説中📦\n\n楽天で買えるおすすめ車用品はこちら👇\nhttps://drivegearlab.online/\n\n#車好き #カーグッズ #楽天 #ガジェット好き',
        '💡 楽天で買える車用品、何を選べばいい？\n\nDRIVE GEAR LABでは選び方のポイントと注意点をスペックから解説中！\n\n👇 チェックしてみてください\nhttps://drivegearlab.online/\n\n#楽天 #車用品 #カーグッズ #ドライブ好き',
        '🔥 今週のおすすめ車用品をチェック！\n\nドライブレコーダー・スマホホルダー・モバイルバッテリーなど20アイテム以上掲載中🔍\n\nhttps://drivegearlab.online/\n\n#ドライブレコーダー #スマホホルダー #車載グッズ #楽天購入品',
        '☀️ 夏のドライブ対策してますか？\n\nサンシェード・ハンディファンなど暑さ対策グッズを楽天からご紹介！\n\nhttps://drivegearlab.online/\n\n#夏 #車中暑対策 #サンシェード #楽天 #カーグッズ',
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
