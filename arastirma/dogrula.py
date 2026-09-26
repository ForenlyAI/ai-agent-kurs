"""Bulgu doğrulama — modelin DIŞINDA koşan denetim (ders 2.5 ve 4.4).

Kaynak kimliğinin var olması yetmez: model doğru belgeyi gösterip yanlış sayı yazabilir
(lab'ın ilk koşumunda "1,5 m kaldırım genişliği" → "günde 1,5 saat park" oldu).
Kural: bulgudaki her sayı, hemen ardındaki birimle birlikte kaynak belgede birebir geçmelidir.
Geçmeyen bulgu rapora girmez; iz kaydına "reddedildi" olarak yazılır.
Bu denetim belirlenimlidir — aynı girdi hep aynı kararı verir, model çağırmaz.
"""
from __future__ import annotations

import re

from . import kutuphane

BIRIM = r"(?:%|km/s|km|m\b|TL|milyon|saat|dakika|ay\b)"   # gerçek ölçü birimleri; "kaza", "araç" gibi sayılan isimler cümlede yer değiştirir, denetlenmez
SAYI = re.compile(r"(%\s?)?(\d{1,3}(?:[.\s]\d{3})+|\d+(?:,\d+)?)\s*(" + BIRIM + r")?", re.I)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("**", "")).lower()


def sayilar(metin: str) -> list[tuple[str, str]]:
    """[(sayı, birim)] — yıl gibi 4 haneli yalın sayılar (2026) tarih sayılır ve denetlenmez."""
    out = []
    for yuzde, sayi, birim in SAYI.findall(metin):
        if re.fullmatch(r"(19|20)\d\d", sayi) and not yuzde and not birim:
            continue
        out.append((sayi, "%" if yuzde else (birim or "").lower()))
    return out


def denetle(bulgu: str, kaynak: str) -> tuple[bool, str]:
    b = kutuphane.getir(kaynak)
    if b is None:
        return False, f"kaynak yok: {kaynak}"
    belge = _norm(b.govde)
    for sayi, birim in sayilar(bulgu):
        if sayi not in belge:
            return False, f"'{sayi}' kaynakta ({kaynak}) geçmiyor"
        if birim == "%":
            if not re.search(r"%\s?" + re.escape(sayi) + r"(?!\d)", belge):
                return False, f"'%{sayi}' kaynakta ({kaynak}) yüzde olarak geçmiyor"
        elif birim and not re.search(re.escape(sayi) + r"\s*" + re.escape(birim), belge):
            return False, f"'{sayi} {birim}' kaynakta ({kaynak}) bu birimle geçmiyor"
    return True, "geçti"
