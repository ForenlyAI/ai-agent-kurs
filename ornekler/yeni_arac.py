"""Ders 4.3 — kendi aracını eklemek için iskelet.

1. Aşağıdaki fonksiyonu ve şemayı arastirma/araclar.py dosyasına kopyalayın.
2. SEMA listesine şemayı, kutu_ile() sözlüğüne fonksiyonu ekleyin.
3. Hattı koşturun ve iz kaydında (localhost:8070/kosumlar) ajanın aracı çağırıp çağırmadığına bakın.
"""
from arastirma import kutuphane

SEMA_TURE_GORE = {"type": "function", "function": {
    "name": "ture_gore_listele",
    "description": "Kütüphanedeki belgeleri türüne göre listeler (ör. 'kurum raporu', 'akademik çalışma'). Güvenilir kaynağı seçmek için kullan.",
    "parameters": {"type": "object", "properties": {
        "tur": {"type": "string", "description": "belge türü"}}, "required": ["tur"]}}}


def ture_gore_listele(tur: str) -> str:
    bulunan = [b for b in kutuphane.tum_belgeler() if tur.lower() in b.tur.lower()]
    if not bulunan:
        turler = sorted({b.tur for b in kutuphane.tum_belgeler()})
        return f"'{tur}' türünde belge yok. Mevcut türler: {', '.join(turler)}"
    return "\n".join(f"{b.kimlik} · {b.baslik} · {b.tarih}" for b in bulunan)
