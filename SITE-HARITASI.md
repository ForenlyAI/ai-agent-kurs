# Lab sözleşmesi — AI Agent 101 (2026-09-25)

Derslerde görünen her ekran bu lab'ın gerçek çalıştırmasıdır (spec §2 E1). Ekran dosyaları: `ekran/<ders>/<ad>.png` (+ terminal için ham `.txt`).

| Parça | Dosya | Derslerde |
|---|---|---|
| ajan döngüsü | arastirma/ajan.py | 1.1, 2.1 |
| araçlar (3, hepsi okur) | arastirma/araclar.py | 1.3, 1.4, 2.4, 4.3 |
| model istemcisi (tekrar deneme, zaman aşımı) | arastirma/istemci.py | 2.2, 3.3 |
| orkestratör (katalog, JSON, yedek bölme) | arastirma/orkestrator.py | 3.2, 4.2 |
| bulgu doğrulama (model dışı) + testi | arastirma/dogrula.py, test_dogrula.py | 1.2, 2.5, 4.4 |
| derleme + kaynak denetimi | arastirma/derleme.py | 4.4 |
| iz kaydı ve özet | arastirma/iz.py → iz/<koşum>/ | 1.1, 1.5, 2.3, 3.4, 4.5 |
| tarayıcı yüzü :8070 | arastirma/site.py | 1.1, 1.3, 1.5, 2.3, 3.4, 4.4 |
| model sunucusu :8199 | sunucu/model_sunucu.py | 3.3, 4.1 |
| kontrol | kontrol.sh | 3.5, 4.5 |

## Adresler (arastirma.site)
`/` katalog · `/ara?q=` arama · `/belge/<KİMLİK>` · `/kosumlar` · `/iz/<koşum>?ajan=&tur=` · `/rapor/<koşum>`

## Kütüphanedeki kasıtlı tuzaklar
BEL-2024 (eski, 1.850 araç) ↔ BEL-2026 (4.200 lisans) ↔ SEK-2026 (5.600 üye beyanı, sokakta 3.900) · FOR-01 (kaynaksız) · OPR-01 (pazarlama) · UNI-KAZA 512 hastane başvurusu ↔ BEL-2026 318 trafik kaydı
