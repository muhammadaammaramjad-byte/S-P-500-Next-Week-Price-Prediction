"""Render the book's index.html to PDF using headless Chromium via Playwright.

Usage:
    python build_pdf.py

Output: Linear-Algebra-for-Data-Scientists.pdf (same directory as index.html).
"""
from pathlib import Path
from playwright.sync_api import sync_playwright


def main() -> None:
    here = Path(__file__).resolve().parent
    html = here / "index.html"
    pdf = here / "Linear-Algebra-for-Data-Scientists.pdf"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(html.as_uri(), wait_until="networkidle")
        # Allow KaTeX / fonts a moment to settle.
        page.wait_for_timeout(1500)
        page.pdf(
            path=str(pdf),
            format="A4",
            margin={"top": "14mm", "bottom": "14mm", "left": "14mm", "right": "14mm"},
            print_background=True,
            prefer_css_page_size=False,
        )
        browser.close()
    print(f"Wrote {pdf} ({pdf.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
