"""Orkestratör — konuyu alt sorulara bölen ajan (ders 3.2 ve 4.2).

Kendi başına araştırma yapmaz; işi bölmek ve bölümleri araştırma ajanlarına dağıtmaktır.
Çıktısı yapılandırılmıştır (JSON dizisi) ve doğrulanır — model şemayı bozarsa yedek bölme devreye girer.
"""
from __future__ import annotations

import json
import re

from . import istemci, kutuphane
from .iz import Iz

SISTEM = """Sen bir araştırma orkestratörüsün. Sana verilen konuyu, birbirinden farklı yönleri
araştıran ALT SORULARA bölersin. Kendin araştırma yapmazsın, cevap yazmazsın.

Kurallar:
- 3 ile 5 arası alt soru üret.
- Her alt soru tek bir yönü sorsun; sorular birbirini tekrarlamasın.
- Her soru KISA ve TEK parçalı olsun (en çok 15 kelime). "ve", "ayrıca" ile iki şeyi birden sorma.
- Soru bir ölçüyü sorabilir ama ölçünün ne çıkacağını varsaymasın (yüzde, süre, sayı uydurma).
- Alt soruları SANA VERİLEN KATALOĞA dayandır. Katalogda karşılığı olmayan bir veriyi sorma
  (ör. katalogda yaş dağılımı yoksa yaş sorma). Uydurulmuş bir soru, cevapsız bir ajan demektir.
- YALNIZ bir JSON dizisi yaz, başka hiçbir şey yazma. Biçim:
["birinci alt soru", "ikinci alt soru", "üçüncü alt soru"]"""


def _ayikla(ham: str) -> list[str]:
    m = re.search(r"\[.*\]", ham, re.S)
    if not m:
        return []
    try:
        v = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    return [str(x).strip() for x in v if isinstance(x, str) and x.strip()][:5]


def katalog() -> str:
    """Kütüphanenin içindekiler listesi — orkestratör neyin var olduğunu bilmeden bölemez (ders 3.2)."""
    return "\n".join(f"- {b.kimlik} · {b.baslik} · {b.tur} · {b.tarih}" for b in kutuphane.tum_belgeler())


def bol(konu: str, iz: Iz) -> tuple[list[str], str]:
    """(alt sorular, kaynak) — kaynak 'model' ya da 'yedek bölme' (ders 2.2: şema bozulunca)."""
    try:
        y = istemci.sor([{"role": "system", "content": SISTEM}, {"role": "user", "content": f"Kütüphane kataloğu:\n{katalog()}\n\nKonu: {konu}"}],
                        azami_token=400)
    except istemci.ModelHatasi as ex:
        iz.sorun("orkestrator", str(ex))
        return _yedek(konu), "yedek bölme (model yanıt vermedi)"
    iz.model("orkestrator", y["usage"], y["gecikme"])
    sorular = _ayikla(y["mesaj"].get("content") or "")
    if len(sorular) < 3:
        iz.sorun("orkestrator", f"şema bozuk ya da az soru ({len(sorular)}) — yedek bölme")
        return _yedek(konu), "yedek bölme (şema bozuk)"
    iz.yaz("bolme", sorular=sorular)
    return sorular, "model"


def _yedek(konu: str) -> list[str]:
    """Model bozulursa hat durmaz: konuyu sabit üç yönden sorar (ders 2.2 — hatada güvenli davranış)."""
    return [f"{konu} hakkında sayısal büyüklükler ve ölçümler nelerdir?",
            f"{konu} konusunda hangi sorunlar ve şikâyetler bildirilmiştir?",
            f"{konu} için hangi düzenleme, çözüm ya da öneriler vardır?"]
