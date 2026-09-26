"""Ajan döngüsü — kursun 1.1'de çizilen çemberin kodu.

    amaç → düşün (model) → araç çağır → gözlem (araç sonucu) → dur

Durma kuralları (ders 2.1): model araç çağırmayı bıraktığında, adım sınırına gelindiğinde
ya da bitirme aracı çağrıldığında durur. Sınırsız döngü yoktur.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from . import istemci
from .iz import Iz


@dataclass
class Sonuc:
    metin: str
    adim: int
    durma: str   # "model bitirdi" | "adım sınırı" | "hata"


def kos(ad: str, sistem: str, gorev: str, araclar_semasi: list[dict],
        araclar: dict[str, Callable[..., Any]], iz: Iz, azami_adim: int = 6) -> Sonuc:
    mesajlar = [{"role": "system", "content": sistem}, {"role": "user", "content": gorev}]
    for adim in range(1, azami_adim + 1):
        try:
            y = istemci.sor(mesajlar, araclar_semasi)
        except istemci.ModelHatasi as ex:
            iz.sorun(ad, str(ex))
            return Sonuc("", adim, "hata")
        iz.model(ad, y["usage"], y["gecikme"])
        mesaj = y["mesaj"]
        mesajlar.append(mesaj)

        cagrilar = mesaj.get("tool_calls") or []
        if not cagrilar:
            return Sonuc((mesaj.get("content") or "").strip(), adim, "model bitirdi")

        for c in cagrilar:
            isim = c["function"]["name"]
            try:
                girdi = json.loads(c["function"]["arguments"] or "{}")
            except json.JSONDecodeError:
                sonuc = "Araç girdisi geçerli JSON değil. Şemaya uyan bir çağrı yap."
                girdi = {}
            else:
                fn = araclar.get(isim)
                if fn is None:
                    sonuc = f"'{isim}' diye bir araç yok. Kullanabileceklerin: {', '.join(araclar)}"
                else:
                    try:
                        sonuc = fn(**girdi)
                    except TypeError as ex:
                        sonuc = f"Araç girdisi eksik ya da fazla: {ex}"
                    except Exception as ex:   # araç patlarsa ajan görsün, hat çökmesin (ders 2.2)
                        sonuc = f"Araç hata verdi: {type(ex).__name__}: {ex}"
            iz.arac(ad, isim, girdi, str(sonuc))
            mesajlar.append({"role": "tool", "tool_call_id": c["id"], "name": isim, "content": str(sonuc)})

    iz.sorun(ad, f"adım sınırına ({azami_adim}) gelindi")
    son = next((m.get("content") for m in reversed(mesajlar) if m.get("role") == "assistant" and m.get("content")), "")
    return Sonuc((son or "").strip(), azami_adim, "adım sınırı")
