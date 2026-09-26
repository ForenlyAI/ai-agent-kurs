# AI Agent 101 · Lab — Araştırma Asistanı Hattı

Bir konuyu alt sorulara bölen **orkestratör**, bu soruları **paralel** araştıran **ajanlar**, bulguları
**model dışında doğrulayan** bir denetim, kaynak göstererek rapor yazan bir **derleme ajanı** ve
isteğe bağlı **insan onayı**. Her koşum adım adım **iz kaydı**, token ve süre özeti bırakır.

> **ÖRNEK VERİ:** Kütüphanedeki 17 belge uydurma bir şehir (Yeşilkent) için yazılmıştır. Gerçek kurum, kişi ya da ölçüm değildir.

## En kolay yol: GitHub Codespaces

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ForenlyAI/ai-agent-kurs?quickstart=1)

Tarayıcıda hazır bir ortam açılır. İlk açılışta kurulum kendiliğinden yapılır (~5 dk): `uv sync`, [Ollama](https://ollama.com)
ve kursun modeli **Qwen3-4B-Instruct-2507** (4 bit, ~2,5 GB). Model GPU'suz, işlemcide koşar ve `yerel` adıyla hazır bekler;
`AJAN_MODEL_URL` önceden ayarlıdır. Kurulum bitince:

```bash
bash kontrol.sh            # 8 adım · GEÇTİ / KALDI (uçtan uca koşum dahil, ~5 dk)
```

- Ortam 4 çekirdekli makine ister; GitHub'ın ücretsiz kotası bu makinede ayda ~30 saattir. İşiniz bitince Codespace'i durdurun.
- Videolardaki koşumlar GPU'da yapıldı. İşlemcide aynı model birkaç kat yavaştır: `--ajan 2 --adim 5` ile tam hat ~4–5 dk sürer.
  4 bitlik sürüm aynı konuda birebir aynı bulguları üretmeyebilir; doğrulayıcı ve iz kaydı aynı çalışır.
- Rapor sitesi: `uv run python -m arastirma.site` → açılan 8070 portu.

## Kurulum (tek komut)

```bash
uv sync
```

Python 3.12+ ve [uv](https://docs.astral.sh/uv/) gerekir. Tek bağımlılık `httpx`.

## Model

Hat OpenAI uyumlu bir uç noktayla konuşur; adresi `AJAN_MODEL_URL` belirler.

| Yol | Ne yaparsınız |
|---|---|
| **A · kendi GPU'nuz** (kursun ekranları bu yoldan) | GPU'lu makinede `pip install torch transformers` sonra `python sunucu/model_sunucu.py --port 8199`. Model: Qwen3-4B-Instruct-2507, ~8 GB GPU belleği |
| **C · işlemci (Codespaces'ta hazır)** | `ollama pull qwen3:4b-instruct && ollama cp qwen3:4b-instruct yerel`, sonra `export AJAN_MODEL_URL=http://127.0.0.1:11434/v1/chat/completions`. Aynı model, 4 bit, GPU gerekmez, daha yavaş |
| **B · bir sağlayıcı** | `export AJAN_MODEL_URL=https://…/v1/chat/completions` — sağlayıcının anahtarını istemci.py'ye başlık olarak ekleyin (ders 3.3). **Anahtarı dosyaya yazıp paylaşmayın.** |

Sağlık denetimi: `curl localhost:8199/saglik` → `{"durum": "hazir", …}`

## Çalıştırma

```bash
uv run python -m arastirma.hat "Yeşilkent'te elektrikli scooter"      # tam hat
uv run python -m arastirma.hat "konu" --onay                           # rapordan önce insan onayı (2.1)
uv run python -m arastirma.hat "konu" --ajan 1                         # tek ajan — süreyi karşılaştırın (3.2)
uv run python -m arastirma.hat "konu" --adim 2                         # adım sınırı deneyi (2.1)
uv run python -m arastirma.site                                        # tarayıcı: http://localhost:8070
uv run python -m arastirma.test_dogrula                                # doğrulayıcının kendi testi (2.5)
bash kontrol.sh                                                        # her şeyi dene: GEÇTİ / KALDI
```

## Derslerdeki deneyler

| Ders | Komut |
|---|---|
| 1.4 · olmayan belge | `uv run python -c "from arastirma import araclar as a; print(a.kutu_ile([])['belge_getir'](kimlik='YOK-1'))"` |
| 2.2 · bozuk bağlantı | `AJAN_MODEL_URL=http://127.0.0.1:8198/v1/chat/completions AJAN_DENEME=2 uv run python -m arastirma.hat "Yeşilkent scooter"` |
| 2.4 · istem enjeksiyonu | `cp ornekler/ENJ-01.md kutuphane/belgeler/` → hattı koşturun → `rm kutuphane/belgeler/ENJ-01.md` |
| 4.1 · kendi belgen | `kutuphane/belgeler/` içine aynı üst bilgiyle (kimlik, baslik, yayinci, tur, tarih, guvenilirlik) bir `.md` ekleyin |
| 4.3 · kendi aracın | `ornekler/yeni_arac.py` içindeki adımları izleyin |

## Klasörler

```
arastirma/   hattın kodu — hat, orkestrator, ajan, araclar, dogrula, derleme, istemci, iz, kutuphane, site
kutuphane/   ajanların araştırdığı belgeler (ÖRNEK VERİ)
iz/          her koşum: olaylar.jsonl (iz), ozet.json (token, süre), rapor.md
sunucu/      yerel model sunucusu (GPU)
.devcontainer/  Codespaces ortamı (Ollama + model, işlemci)
ornekler/    ders deneyleri
araclar/     ders ekran görüntüsü araçları (öğrenci için gerekmez)
```
