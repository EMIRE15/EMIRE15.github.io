import os
import sys
import google.generativeai as genai

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    target_file = os.environ.get("TARGET_FILE", "guide-dashcam-howto-choose.html")
    instruction = os.environ.get("REWRITE_INSTRUCTION", "最新情報に更新し、SEOを改善してください")

    if not api_key:
        print("❌ エラー: GEMINI_API_KEY が設定されていません")
        sys.exit(1)

    if not os.path.exists(target_file):
        print(f"❌ エラー: ファイルが見つかりません: {target_file}")
        sys.exit(1)

    with open(target_file, "r", encoding="utf-8") as f:
        original_html = f.read()

    print(f"✅ ファイル読み込み完了: {target_file} ({len(original_html)} 文字)")
    print(f"📝 リライト指示: {instruction}")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="""あなたはプロのWebライターです。
与えられたHTMLファイルをリライトしてください。

ルール:
- HTMLの構造・タグ・クラス名・id・リンク・アフィリエイトリンクは絶対に変更しないこと
- テキストコンテンツのみを改善する（見出し・本文・テーブル内のテキストなど）
- 日本語で自然に書き直す
- 価格情報・年号（例:2025年→2026年）など古い情報は最新化する
- meta description・og:description も更新する
- 出力はHTMLのみ（説明文や```は不要）"""
    )

    prompt = f"""以下のHTMLをリライトしてください。

指示: {instruction}

=== 対象HTML ===
{original_html}
"""

    print("🤖 Gemini API にリクエスト送信中...")
    response = model.generate_content(prompt)
    rewritten_html = response.text.strip()

    if rewritten_html.startswith("```"):
        lines = rewritten_html.splitlines()
        rewritten_html = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(rewritten_html)

    print(f"✅ リライト完了: {target_file} ({len(rewritten_html)} 文字)")

if __name__ == "__main__":
    main()
