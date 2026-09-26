"""Derleme ajanı — bulguları kaynak göstererek tek rapora çeviren adım (ders 4.4).

Rapor yalnız kaydedilmiş bulgulardan yazılır; ajanın kendi belleğinden sayı eklemesi yasaktır.
Kaynak gösterimi zorunludur: her madde [KİMLİK] ile biter. Rapor yazıldıktan sonra
kaynak denetimi koşar — uydurulmuş kimlik varsa rapor KUSURLU işaretlenir (ders 2.5).
"""
from __future__ import annotations

import re

from . import istemci, kutuphane
from .iz import Iz

SISTEM = """Sen bir derleme editörüsün. Sana alt sorular ve başka ajanların topladığı BULGULAR verilir.
Tek işin bu bulguları düzenli bir rapora çevirmektir.

Kesin kurallar:
- YALNIZ verilen bulgulardaki bilgiyi kullan. Kendi bilginden tek bir sayı bile ekleme.
- Her maddenin sonuna kaynağını köşeli parantezle yaz: [BEL-2026]
- İki kaynak aynı şeyi farklı söylüyorsa bunu ayrı bir maddede belirt ve iki kaynağı da göster.
- Türkçe yaz. Biçim:

## Özet
2-3 cümle.

## Bulgular
- madde [KAYNAK]

## Çelişkiler ve boşluklar
- madde [KAYNAK] (çelişki yoksa: "Bulgular arasında çelişki görülmedi.")"""


def yaz(konu: str, sorular: list[str], bulgular: list[dict], iz: Iz) -> tuple[str, list[str]]:
    """(rapor metni, uydurulmuş kaynak kimlikleri)."""
    if not bulgular:
        return "## Özet\nAraştırma ajanları hiçbir bulgu kaydedemedi; rapor üretilmedi.\n", []
    liste = "\n".join(f"- {b['bulgu']} [{b['kaynak']}]" for b in bulgular)
    gorev = f"Konu: {konu}\n\nAlt sorular:\n" + "\n".join(f"- {s}" for s in sorular) + f"\n\nBulgular:\n{liste}"
    try:
        y = istemci.sor([{"role": "system", "content": SISTEM}, {"role": "user", "content": gorev}], azami_token=1200)
    except istemci.ModelHatasi as ex:
        iz.sorun("derleme", str(ex))
        return "## Özet\nDerleme ajanı yanıt vermedi.\n\n## Bulgular\n" + liste + "\n", []
    iz.model("derleme", y["usage"], y["gecikme"])
    rapor = (y["mesaj"].get("content") or "").strip()

    gecerli = {b.kimlik.upper() for b in kutuphane.tum_belgeler()}
    kullanilan = {k.upper() for k in re.findall(r"\[([A-ZÇĞİÖŞÜ0-9\-]{3,})\]", rapor)}
    uydurma = sorted(kullanilan - gecerli)
    if uydurma:
        iz.sorun("derleme", f"raporda olmayan kaynak: {', '.join(uydurma)}")
    return rapor, uydurma
