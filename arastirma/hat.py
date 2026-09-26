"""Araştırma asistanı hattı — AI Agent 101 lab'ının tamamı tek komutta.

    uv run python -m arastirma.hat "Yeşilkent'te elektrikli scooter"
    uv run python -m arastirma.hat "konu" --onay            # insan onayı kapısı açık (ders 2.1)
    uv run python -m arastirma.hat "konu" --ajan 3 --adim 6

Akış:  orkestratör konuyu böler → araştırma ajanları PARALEL koşar → derleme ajanı raporu yazar
       → bulgu doğrulama (model dışı) → kaynak denetimi → (isteğe bağlı) insan onayı → rapor + maliyet + iz
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from . import araclar, ajan, derleme, dogrula, orkestrator
from .iz import IZ_KOK, Iz

ARASTIRMACI_SISTEM = """Sen bir araştırma ajanısın. Sana tek bir alt soru verilir.

Kesin kurallar:
- Kendi belleğinden ASLA cevap verme. Her bilgi kütüphaneden gelmeli.
- ÖNCE ara aracını çağır. Sonra ilgili belgeyi belge_getir ile tam metin olarak oku.
- Sayı alıntılayacaksan o belgeyi mutlaka tam metin olarak okumuş ol.
- Bulduğun her doğrulanmış bilgi için bulgu_kaydet aracını çağır (bulgu + kaynak belge kimliği).
- En az 1, en çok 3 bulgu kaydet. Kaydettikten sonra tek cümlelik özet yaz ve dur.
- Belgenin tarihine ve türüne dikkat et: eski bir rapor ile yeni bir rapor çelişiyorsa ikisini de kaydet.
- Bulguyu belgedeki cümleye SADIK yaz. Hesap yapma, oran türetme, iki sayıyı birleştirme, yorum ekleme.
- Sayıyı belgedeki birimiyle aynen yaz (belgede 1,5 m yazıyorsa 1,5 m yaz)."""


def kosum_adi(konu: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", konu.lower().replace("ı", "i").replace("ş", "s").replace("ğ", "g")
               .replace("ü", "u").replace("ö", "o").replace("ç", "c")).strip("-")[:40]
    return f"{datetime.now():%Y%m%d-%H%M%S}-{s or 'konu'}"


def arastir(soru: str, iz: Iz, azami_adim: int) -> tuple[str, list[dict], str]:
    bulgular: list[dict] = []
    ad = f"arastirmaci:{soru[:28]}"
    s = ajan.kos(ad, ARASTIRMACI_SISTEM, f"Alt soru: {soru}", araclar.SEMA,
                 araclar.kutu_ile(bulgular), iz, azami_adim)
    return soru, bulgular, s.durma


def main(argv: list[str] | None = None) -> int:
    a = argparse.ArgumentParser(description="Araştırma asistanı hattı")
    a.add_argument("konu")
    a.add_argument("--ajan", type=int, default=3, help="aynı anda koşacak araştırma ajanı sayısı")
    a.add_argument("--adim", type=int, default=6, help="ajan başına azami döngü adımı (ders 2.1)")
    a.add_argument("--onay", action="store_true", help="raporu teslim etmeden önce insan onayı iste (ders 2.1)")
    n = a.parse_args(argv)

    iz = Iz(kosum_adi(n.konu))
    print(f"■ koşum {iz.kosum}\n■ konu: {n.konu}\n")

    t = time.time()
    sorular, kaynak = orkestrator.bol(n.konu, iz)
    print(f"▸ orkestratör {len(sorular)} alt soru üretti ({kaynak}, {time.time()-t:.1f} sn)")
    for i, s in enumerate(sorular, 1):
        print(f"   {i}. {s}")

    print(f"\n▸ {len(sorular)} araştırma ajanı paralel koşuyor (en çok {n.ajan} aynı anda)…")
    t = time.time()
    with ThreadPoolExecutor(max_workers=n.ajan) as havuz:
        sonuclar = list(havuz.map(lambda s: arastir(s, iz, n.adim), sorular))
    tum: list[dict] = []
    for soru, bulgular, durma in sonuclar:
        print(f"   {len(bulgular)} bulgu · {durma} · {soru[:60]}")
        tum.extend(bulgular)
    print(f"   toplam {len(tum)} bulgu · {time.time()-t:.1f} sn")

    print("\n▸ bulgu doğrulama (model dışı: her sayı birimiyle kaynakta geçmeli)")
    gecen = []
    for b in tum:
        ok, neden = dogrula.denetle(b["bulgu"], b["kaynak"])
        iz.yaz("dogrulama", bulgu=b["bulgu"], kaynak=b["kaynak"], karar="geçti" if ok else "reddedildi", neden=neden)
        print(f"   {'✓' if ok else '✗'} [{b['kaynak']}] {b['bulgu'][:70]}" + ("" if ok else f"\n       → reddedildi: {neden}"))
        if ok:
            gecen.append(b)
    print(f"   {len(gecen)}/{len(tum)} bulgu geçti")
    tum = gecen

    print("\n▸ derleme ajanı raporu yazıyor…")
    rapor, uydurma = derleme.yaz(n.konu, sorular, tum, iz)
    print(f"   kaynak denetimi: {'KUSURLU — olmayan kaynak: ' + ', '.join(uydurma) if uydurma else 'GEÇTİ (bütün kaynaklar kütüphanede)'}")

    if n.onay:
        print("\n" + "─" * 70 + f"\n{rapor}\n" + "─" * 70)
        try:
            c = input("Bu rapor teslim edilsin mi? [e/h] ").strip().lower()
        except EOFError:
            c = "h"   # cevap gelmezse teslim YOK — hatada güvenli durma (ders 2.2)
        if not sys.stdin.isatty():
            print(c)   # borudan gelen cevabı ekranda göster
        iz.yaz("onay", karar=c)
        if c != "e":
            o = iz.ozet()
            print("■ teslim edilmedi — insan onayı kapısı (ders 2.1); rapor dosyası yazılmadı")
            print(f"■ {o['model_cagrisi']} model çağrısı · {o['toplam_token']} token · {o['sure_sn']} sn — iz kaydı yine de tutuldu")
            return 1

    d = IZ_KOK / iz.kosum
    (d / "rapor.md").write_text(f"# {n.konu}\n\n{rapor}\n", encoding="utf-8")
    o = iz.ozet()
    print(f"\n■ rapor: {Path(d / 'rapor.md').relative_to(Path.cwd()) if str(d).startswith(str(Path.cwd())) else d / 'rapor.md'}")
    print(f"■ {o['model_cagrisi']} model çağrısı · {o['arac_cagrisi']} araç çağrısı · {o['hata']} hata")
    print(f"■ {o['toplam_token']} token ({o['giris_token']} giriş + {o['cikis_token']} çıkış) · "
          f"{o['sure_sn']} sn · maliyet {o['maliyet_usd']} USD [{o['fiyat_etiketi']}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
