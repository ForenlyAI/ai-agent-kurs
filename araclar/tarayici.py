"""Lab sitesinin (arastirma.site, :8070) gerçek tarayıcı ekran görüntüsü — 1280×800.
    uv run --project araclar python araclar/tarayici.py <ders> <ad> <yol> [--kaydir PX]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ortak import LAB, MASAUSTU, ekran_yolu  # noqa: E402


def cek(ders: str, ad: str, yol: str, kaydir: int = 0) -> Path:
    from playwright.sync_api import sync_playwright
    png = ekran_yolu(ders, ad)
    with sync_playwright() as p:
        t = p.chromium.launch()
        s = t.new_page(viewport=MASAUSTU)
        s.goto("http://localhost:8070" + yol)
        s.evaluate("document.fonts.ready.then(() => true)")
        if kaydir:
            s.evaluate(f"window.scrollTo(0, {kaydir})")
        s.screenshot(path=str(png))
        t.close()
    print(png.relative_to(LAB))
    return png


if __name__ == "__main__":
    a = sys.argv[1:]
    k = 0
    if "--kaydir" in a:
        i = a.index("--kaydir"); k = int(a[i + 1]); del a[i:i + 2]
    cek(a[0], a[1], a[2], k)
