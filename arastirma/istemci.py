"""Model istemcisi — ajanın konuştuğu tek kapı (ders 3.3).

AJAN_MODEL_URL ortam değişkeni sağlayıcıyı belirler; arayüz OpenAI uyumludur, dolayısıyla
ücretli bir sağlayıcıya geçmek için hattın geri kalanında tek satır değişmez.
Dayanıklılık (ders 2.2): zaman aşımı, üstel bekleyişle tekrar deneme, denemeler bitince açık hata.
"""
from __future__ import annotations

import os
import time

import httpx

URL = os.environ.get("AJAN_MODEL_URL", "http://127.0.0.1:8199/v1/chat/completions")
ZAMAN_ASIMI = float(os.environ.get("AJAN_ZAMAN_ASIMI", "180"))
DENEME = int(os.environ.get("AJAN_DENEME", "3"))


class ModelHatasi(RuntimeError):
    pass


def sor(mesajlar: list[dict], araclar: list[dict] | None = None, sicaklik: float = 0.0,
        azami_token: int = 900) -> dict:
    """Modele bir tur sorar. Dönen sözlük: {"mesaj": {...}, "usage": {...}, "gecikme": float}."""
    govde = {"model": "yerel", "messages": mesajlar, "temperature": sicaklik, "max_tokens": azami_token}
    if araclar:
        govde["tools"] = araclar
    son = ""
    for deneme in range(1, DENEME + 1):
        try:
            y = httpx.post(URL, json=govde, timeout=ZAMAN_ASIMI)
            if y.status_code >= 500:
                son = f"sunucu {y.status_code}: {y.text[:200]}"
            else:
                y.raise_for_status()
                d = y.json()
                return {"mesaj": d["choices"][0]["message"], "usage": d.get("usage", {}),
                        "gecikme": d.get("gecikme_sn", 0.0)}
        except (httpx.TimeoutException, httpx.TransportError) as ex:
            son = f"{type(ex).__name__}: {ex}"
        if deneme < DENEME:
            time.sleep(2 ** deneme)   # üstel bekleyiş — ders 2.2
    raise ModelHatasi(f"{DENEME} denemede yanıt alınamadı ({son})")
