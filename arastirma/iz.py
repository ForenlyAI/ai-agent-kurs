"""İz kaydı ve maliyet muhasebesi — ders 2.3 ve 3.4.

Her koşum lab/iz/<koşum>/ altına yazılır:
  olaylar.jsonl  her adım (model çağrısı, araç çağrısı, hata) tek satır
  ozet.json      token, süre, maliyet, adım sayısı

Token sayıları GERÇEKTİR (model sunucusunun usage alanı). Para tutarı bir VARSAYIMDIR:
yerel model ücretsiz koşar, fiyat tablosu 3.3'te anlatılan ücretli sağlayıcı fiyatlarının
yerine konabilsin diye burada durur. Ekranda her zaman "varsayılan fiyat" etiketiyle gösterilir.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

IZ_KOK = Path(__file__).resolve().parent.parent / "iz"

# varsayılan fiyat: milyon token başına USD — yerel model 0, ücretli sağlayıcı örneği 3.3'te
FIYAT = {"giris_usd_myon": 0.0, "cikis_usd_myon": 0.0, "etiket": "yerel model (sim GPU) — ücretsiz"}


@dataclass
class Iz:
    kosum: str
    t0: float = field(default_factory=time.time)
    giris_token: int = 0
    cikis_token: int = 0
    model_cagrisi: int = 0
    arac_cagrisi: int = 0
    hata: int = 0
    _dosya: Path | None = None

    def __post_init__(self) -> None:
        d = IZ_KOK / self.kosum
        d.mkdir(parents=True, exist_ok=True)
        self._dosya = d / "olaylar.jsonl"
        self._dosya.write_text("", encoding="utf-8")

    def yaz(self, tur: str, **alan) -> None:
        with self._dosya.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"t": round(time.time() - self.t0, 2), "tur": tur} | alan, ensure_ascii=False) + "\n")

    def model(self, ajan: str, usage: dict, gecikme: float) -> None:
        self.model_cagrisi += 1
        self.giris_token += usage.get("prompt_tokens", 0)
        self.cikis_token += usage.get("completion_tokens", 0)
        self.yaz("model", ajan=ajan, giris=usage.get("prompt_tokens", 0), cikis=usage.get("completion_tokens", 0), gecikme_sn=gecikme)

    def arac(self, ajan: str, ad: str, girdi: dict, sonuc_ozet: str) -> None:
        self.arac_cagrisi += 1
        self.yaz("arac", ajan=ajan, ad=ad, girdi=girdi, sonuc=sonuc_ozet[:200])

    def sorun(self, ajan: str, mesaj: str) -> None:
        self.hata += 1
        self.yaz("hata", ajan=ajan, mesaj=mesaj[:300])

    def ozet(self) -> dict:
        usd = (self.giris_token * FIYAT["giris_usd_myon"] + self.cikis_token * FIYAT["cikis_usd_myon"]) / 1_000_000
        o = {"kosum": self.kosum, "sure_sn": round(time.time() - self.t0, 1),
             "model_cagrisi": self.model_cagrisi, "arac_cagrisi": self.arac_cagrisi, "hata": self.hata,
             "giris_token": self.giris_token, "cikis_token": self.cikis_token,
             "toplam_token": self.giris_token + self.cikis_token,
             "maliyet_usd": round(usd, 6), "fiyat_etiketi": FIYAT["etiket"]}
        (IZ_KOK / self.kosum / "ozet.json").write_text(json.dumps(o, ensure_ascii=False, indent=2), encoding="utf-8")
        return o
