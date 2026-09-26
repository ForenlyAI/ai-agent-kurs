"""Ajanın araçları — ders 1.3 ve 1.4.

Kural (1.4): az ve net araç, tek iş yapan imza, anlaşılır hata mesajı, geri dönüşsüz iş yok.
Bu hattaki üç araç da OKUR; hiçbiri silmez, göndermez, para harcamaz — bu yüzden ajan
onları insan onayı olmadan çağırabilir. Onay kapısı yalnız raporu teslim ederken vardır (2.1).
"""
from __future__ import annotations

import json
from typing import Any, Callable

from . import kutuphane

SEMA = [
    {"type": "function", "function": {
        "name": "ara",
        "description": "Kütüphanede belge arar. Anahtar kelimelerle çağır. Her sonuç için belge kimliği, başlık, yayıncı, tarih ve özet döner.",
        "parameters": {"type": "object", "properties": {
            "sorgu": {"type": "string", "description": "aranacak anahtar kelimeler, cümle değil"}},
            "required": ["sorgu"]}}},
    {"type": "function", "function": {
        "name": "belge_getir",
        "description": "Bir belgenin TAM metnini kimliğiyle getirir (ör. BEL-2026). Sayı alıntılamadan önce mutlaka çağır.",
        "parameters": {"type": "object", "properties": {
            "kimlik": {"type": "string", "description": "belge kimliği, arama sonucundan alınır"}},
            "required": ["kimlik"]}}},
    {"type": "function", "function": {
        "name": "bulgu_kaydet",
        "description": "Doğrulanmış tek bir bulguyu kaynağıyla kaydeder. Araştırman bittiğinde bunu çağır.",
        "parameters": {"type": "object", "properties": {
            "bulgu": {"type": "string", "description": "tek cümlelik bulgu, sayı içeriyorsa sayıyla"},
            "kaynak": {"type": "string", "description": "belge kimliği"}},
            "required": ["bulgu", "kaynak"]}}},
]


def _ara(sorgu: str) -> str:
    sonuc = kutuphane.ara(sorgu)
    if not sonuc:
        return f"'{sorgu}' için sonuç yok. Daha genel kelimelerle yeniden dene."
    return json.dumps([{"kimlik": b.kimlik, "baslik": b.baslik, "yayinci": b.yayinci,
                        "tarih": b.tarih, "tur": b.tur, "ozet": b.ozet} for b, _ in sonuc],
                      ensure_ascii=False, indent=1)


def _belge_getir(kimlik: str) -> str:
    b = kutuphane.getir(kimlik)
    if b is None:
        mevcut = ", ".join(x.kimlik for x in kutuphane.tum_belgeler())
        return f"'{kimlik}' diye bir belge yok. Mevcut kimlikler: {mevcut}"
    return (f"# {b.baslik}\nkimlik: {b.kimlik} · yayıncı: {b.yayinci} · tür: {b.tur} · tarih: {b.tarih}\n"
            f"güvenilirlik notu: {b.guvenilirlik}\n\n{b.govde}")


def _bulgu_kaydet(bulgu: str, kaynak: str, _kutu: list | None = None) -> str:
    if kutuphane.getir(kaynak) is None:
        return f"'{kaynak}' diye bir belge yok — bulgu kaydedilmedi. Kaynağı arama sonucundaki kimlikten al."
    if _kutu is not None:
        _kutu.append({"bulgu": bulgu.strip(), "kaynak": kaynak.strip().upper()})
    return f"kaydedildi ({kaynak})"


def kutu_ile(bulgular: list) -> dict[str, Callable[..., Any]]:
    """Araç adı → fonksiyon. bulgu_kaydet çağrıları verilen listeye yazar."""
    return {"ara": _ara, "belge_getir": _belge_getir,
            "bulgu_kaydet": lambda bulgu, kaynak: _bulgu_kaydet(bulgu, kaynak, bulgular)}
