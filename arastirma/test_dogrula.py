"""Doğrulayıcının kendi testi — negatif örnekler lab'ın ilk koşumundaki GERÇEK hatalardan (ders 2.5).
    uv run python -m arastirma.test_dogrula
"""
from .dogrula import denetle

TESTLER = [   # (bulgu, kaynak, geçmeli mi)
    ("2025'te scooter kaynaklı 318 kaza kayda geçti.", "BEL-2026", True),
    ("Kazaların %71'i kaldırımda gerçekleşti.", "BEL-2026", True),
    ("Scooterlar kaldırımda günde ortalama 1,5 saat park ediyor.", "UNI-PARK", False),   # ilk koşum: 1,5 m → 1,5 saat
    ("318 kaza, 2023'teki 96 kazanın %332'sidir.", "BEL-2026", False),                   # ilk koşum: uydurma hesap
    ("Araçların %38'i kaldırımı daraltacak şekilde park edilmiş.", "UNI-PARK", True),
    ("Filo 5.600 araçtır.", "BEL-2026", False),                                           # doğru sayı, yanlış kaynak
    ("Filo 5.600 araçtır.", "SEK-2026", True),
    ("Hız sınırı 20 km/s'ye indirildi.", "PIL-2026", True),
    ("Kaza sayısı %23 azaldı.", "PIL-2026", True),
    ("Kaza sayısı %32 azaldı.", "PIL-2026", False),
    ("Park alanı başına maliyet 14.500 TL.", "MAL-2026", True),
    ("Park alanı başına maliyet 14.500 km.", "MAL-2026", False),
]


def main() -> int:
    dogru = 0
    for bulgu, kaynak, bek in TESTLER:
        g, neden = denetle(bulgu, kaynak)
        dogru += g == bek
        print(f"{'✓' if g == bek else '✗'} {'GEÇTİ ' if g else 'REDDET'} · {neden} · {bulgu[:52]}")
    print(f"{dogru}/{len(TESTLER)} doğru karar")
    return 0 if dogru == len(TESTLER) else 1


if __name__ == "__main__":
    raise SystemExit(main())
