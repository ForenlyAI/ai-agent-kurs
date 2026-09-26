"""Kütüphane — ajanın araştırdığı belge havuzu (lab/kutuphane/belgeler/*.md).

Gerçek bir arama motoru yerine yerel, belirlenimli bir arama: aynı sorgu hep aynı sonucu verir.
Kurs 3.3'te bu katmanın ücretli bir arama API'siyle değiştirilebileceği anlatılır — ajan tarafı değişmez.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent / "kutuphane" / "belgeler"
ETKISIZ = {"ve", "ile", "bir", "bu", "için", "olarak", "daha", "çok", "en", "de", "da", "mi", "mı", "ne",
           "kaç", "nedir", "nasıl", "var", "yok", "the", "and", "of"}


@dataclass(frozen=True)
class Belge:
    kimlik: str
    baslik: str
    yayinci: str
    tur: str
    tarih: str
    guvenilirlik: str
    govde: str

    @property
    def ozet(self) -> str:
        return " ".join(self.govde.split())[:220]


def _sadelestir(s: str) -> str:
    """Türkçe küçültme + aksan ayırma — 'İ' ve 'I' tuzağına düşmeden eşleştirmek için."""
    s = s.replace("I", "ı").replace("İ", "i").lower()
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _kelimeler(s: str) -> list[str]:
    return [k for k in re.findall(r"\w+", _sadelestir(s)) if len(k) > 2 and k not in ETKISIZ]


@lru_cache(maxsize=1)
def tum_belgeler() -> tuple[Belge, ...]:
    out = []
    for f in sorted(KOK.glob("*.md")):
        ham = f.read_text(encoding="utf-8")
        bas, _, govde = ham.partition("---\n\n")
        alan = dict(re.findall(r"^(\w+):\s*(.+)$", bas, re.M))
        out.append(Belge(kimlik=alan.get("kimlik", f.stem), baslik=alan.get("baslik", ""),
                         yayinci=alan.get("yayinci", ""), tur=alan.get("tur", ""),
                         tarih=alan.get("tarih", ""), guvenilirlik=alan.get("guvenilirlik", ""),
                         govde=govde.split("---\n*ÖRNEK VERİ")[0].strip()))
    return tuple(out)


def getir(kimlik: str) -> Belge | None:
    return next((b for b in tum_belgeler() if b.kimlik.upper() == kimlik.strip().upper()), None)


def ara(sorgu: str, adet: int = 5) -> list[tuple[Belge, int]]:
    """Kelime örtüşmesine dayalı puanlama: başlıkta geçen 3, gövdede geçen 1 puan. Belirlenimli."""
    ks = _kelimeler(sorgu)
    puanli = []
    for b in tum_belgeler():
        bas, gov = _kelimeler(b.baslik + " " + b.yayinci), _kelimeler(b.govde)
        p = sum(3 for k in ks if k in bas) + sum(1 for k in ks if k in gov)
        if p:
            puanli.append((b, p))
    puanli.sort(key=lambda x: (-x[1], x[0].kimlik))
    return puanli[:adet]
