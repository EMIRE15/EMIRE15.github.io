import os
import sys
from google import genai

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    target_file = os.environ.get("TARGET_FILE", "guide-dashcam-howto-choose.html")
    instruction = os.environ.get("REWRITE_INSTRUCTION", "Update to latest info and improve SEO")

    if not api_key:
        print("Error: GEMINI_API_KEY is not set")
        sys.exit(1)

    if not os.path.exists(target_file):
        print(f"Error: File not found: {target_file}")
        sys.exit(1)

    with open(target_file, "r", encoding="utf-8") as f:
        original_html = f.read()

    print(f"File loaded: {target_file} ({len(original_html)} chars)")

    client = genai.Client(api_key=api_key)

    prompt = f"""You are a professional web writer. Rewrite the following HTML.

Rules:
- Do NOT change HTML structure, tags, class names, ids, links, or affiliate links
- Only improve text content
- Keep the language Japanese
- Update outdated info like years and prices
- Output HTML only, no explanation

Instruction: {instruction}

=== HTML ===
{original_html}
"""

    print("Sending request to Gemini API...")
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

    rewritten_html = response.text.strip()

    if rewritten_html.startswith("```"):
        lines = rewritten_html.splitlines()
        rewritten_html = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(rewritten_html)

    print(f"Done: {target_file} ({len(rewritten_html)} chars)")

if __name__ == "__main__":
    main()
