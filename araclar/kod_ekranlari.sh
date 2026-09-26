#!/usr/bin/env bash
# Model çağırmayan terminal ekranları (kod, dosya, test) — hızlı yeniden çekim. ekranlari_uret.sh ile aynı komutlar.
cd "$(dirname "$0")/.."
T() { uv run --quiet --project araclar python araclar/terminal.py "$@"; }
ANA=$(cat iz/ANA_KOSUM)
T 1.2 test-dogrula -- uv run python -m arastirma.test_dogrula
T 1.3 sema -- sed -n '14,26p' arastirma/araclar.py
T 1.3 tool-call --goster "curl -s localhost:8199/v1/chat/completions -H 'Content-Type: application/json' -d @ornekler/istek-arac.json | jq .choices[0].message" -- bash -c "curl -s localhost:8199/v1/chat/completions -H 'Content-Type: application/json' -d @ornekler/istek-arac.json | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin)[\"choices\"][0][\"message\"], ensure_ascii=False, indent=2))'"
T 1.4 hata-mesaji -- uv run python -c "from arastirma import araclar as a; print(a.kutu_ile([])['belge_getir'](kimlik='YOK-1'))"
T 1.4 hata-kodu -- sed -n '/^def _belge_getir/,/^$/p;/^def _bulgu_kaydet/,/^    if _kutu/p' arastirma/araclar.py
T 2.2 tekrar-dene -- sed -n '/^def sor/,/^    raise/p' arastirma/istemci.py
T 2.3 ozet -- cat iz/$ANA/ozet.json
T 2.4 yetki -- sed -n '1,6p' arastirma/araclar.py
T 2.5 test -- uv run python -m arastirma.test_dogrula
T 3.3 istemci -- sed -n '1,17p' arastirma/istemci.py
T 3.3 saglik -- curl -s localhost:8199/saglik
T 3.4 olaylar -- head -n 6 iz/$ANA/olaylar.jsonl
T 4.1 agac -- ls arastirma kutuphane sunucu ornekler
T 4.2 istem -- sed -n '/^SISTEM/,/"""$/p' arastirma/orkestrator.py
T 4.3 istem -- sed -n '/^ARASTIRMACI_SISTEM/,/"""$/p' arastirma/hat.py
T 4.3 paralel-kod -- sed -n '/ThreadPoolExecutor(max_workers/,/tum.extend/p' arastirma/hat.py
T 4.5 maliyet -- cat iz/$ANA/ozet.json
T 4.5 paket -- ls -la iz/$ANA
echo KOD EKRANLARI TAMAM
