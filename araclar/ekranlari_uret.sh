#!/usr/bin/env bash
# AI Agent 101 — derslerin bütün gerçek ekranlarını üretir (lab klasöründen çalıştırın).
# Önkoşul: model sunucusu :8199 (tünel), lab sitesi :8070 (uv run python -m arastirma.site)
#   bash araclar/ekranlari_uret.sh            # hepsi
#   bash araclar/ekranlari_uret.sh 2.1 3.2    # yalnız bu dersler
set -u
cd "$(dirname "$0")/.."
T() { uv run --quiet --project araclar python araclar/terminal.py "$@"; }
B() { uv run --quiet --project araclar python araclar/tarayici.py "$@"; }
HAT="uv run --quiet python -m arastirma.hat"
KONU="Yeşilkent'te elektrikli scooter: kaza, park ve düzenleme"
ANA_DOSYA=iz/ANA_KOSUM
ILK=20260925-123658-yesilkent-te-elektrikli-scooter-kazalari   # katalogsuz orkestratörün gerçek ilk koşumu
ister() { [ $# -eq 0 ] && return 0; for d in "${SECIM[@]}"; do [ "$d" = "$1" ] && return 0; done; return 1; }
SECIM=("$@")
sec() { [ ${#SECIM[@]} -eq 0 ] && return 0; for d in "${SECIM[@]}"; do [ "$d" = "$1" ] && return 0; done; return 1; }
son() { ls -td iz/2026*/ | head -1 | xargs basename; }

if sec 1.1 || [ ! -f $ANA_DOSYA ]; then
  T 1.1 hat-kosum -- uv run python -m arastirma.hat "$KONU"
  son > $ANA_DOSYA
fi
ANA=$(cat $ANA_DOSYA)
AJAN1=$(grep -o '"ajan": "arastirmaci:[^"]*"' iz/$ANA/olaylar.jsonl | head -1 | cut -d'"' -f4 | cut -c1-24)
sec 1.1 && B 1.1 iz-kaydi "/iz/$ANA"

sec 1.2 && { T 1.2 test-dogrula -- uv run python -m arastirma.test_dogrula; B 1.2 uni-park /belge/UNI-PARK; }
sec 1.3 && { T 1.3 sema -- sed -n '14,26p' arastirma/araclar.py
             T 1.3 tool-call --goster "curl -s localhost:8199/v1/chat/completions -d @istek.json | jq .choices[0].message" -- bash -c "curl -s localhost:8199/v1/chat/completions -H 'Content-Type: application/json' -d @ornekler/istek-arac.json | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin)[\"choices\"][0][\"message\"], ensure_ascii=False, indent=2))'"
             B 1.3 kutuphane-ara "/ara?q=kaza%20say%C4%B1s%C4%B1"; }
sec 1.4 && { T 1.4 hata-mesaji -- uv run python -c "from arastirma import araclar as a; print(a.kutu_ile([])['belge_getir'](kimlik='YOK-1'))"
             T 1.4 hata-kodu -- sed -n '/^def _belge_getir/,/^$/p;/^def _bulgu_kaydet/,/^    if _kutu/p' arastirma/araclar.py; }
sec 1.5 && { B 1.5 token-buyume "/iz/$ANA?ajan=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$AJAN1")&tur=model"
             B 1.5 mesajlar "/iz/$ANA?ajan=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$AJAN1")"; }

sec 2.1 && { T 2.1 adim-siniri -- uv run python -m arastirma.hat "$KONU" --adim 2
             T 2.1 onay --goster "uv run python -m arastirma.hat \"Yeşilkent scooter park sorunu\" --onay" -- bash -c "printf 'h\n' | $HAT 'Yeşilkent scooter park sorunu' --onay --ajan 2 | tail -22"; }
sec 2.2 && { T 2.2 baglanti-hatasi -- env AJAN_MODEL_URL=http://127.0.0.1:8198/v1/chat/completions AJAN_DENEME=2 uv run python -m arastirma.hat "Yeşilkent scooter"
             T 2.2 tekrar-dene -- sed -n '/^def sor/,/^    raise/p' arastirma/istemci.py; }
sec 2.3 && { T 2.3 ozet -- cat iz/$ANA/ozet.json; B 2.3 kosumlar /kosumlar; }
sec 2.4 && { cp ornekler/ENJ-01.md kutuphane/belgeler/
             T 2.4 enjeksiyon -- uv run python -m arastirma.hat "Yeşilkent scooter güvenliği ve vatandaş görüşü"
             son > iz/ENJ_KOSUM; rm -f kutuphane/belgeler/ENJ-01.md
             T 2.4 yetki -- sed -n '1,10p' arastirma/araclar.py; }
sec 2.5 && { T 2.5 test -- uv run python -m arastirma.test_dogrula
             B 2.5 dogrulama "/iz/$ANA?tur=dogrulama"; }

sec 3.1 && B 3.1 kosum-ozet /kosumlar
sec 3.2 && { T 3.2 paralel --goster "for n in 1 3; do uv run python -m arastirma.hat \"Yeşilkent scooter park\" --ajan \$n | grep '■'; done" -- bash -c "for n in 1 3; do echo \"── --ajan \$n\"; $HAT 'Yeşilkent scooter park' --ajan \$n | grep '■ [0-9]'; done"
             B 3.2 bolme "/iz/$ANA?tur=bolme"; }
sec 3.3 && { T 3.3 istemci -- sed -n '1,20p' arastirma/istemci.py; T 3.3 saglik -- curl -s localhost:8199/saglik; }
sec 3.4 && { T 3.4 olaylar -- head -c 1400 iz/$ANA/olaylar.jsonl; B 3.4 kosumlar /kosumlar; }
sec 3.5 && T 3.5 kontrol -- bash kontrol.sh

sec 4.1 && { T 4.1 agac --goster "ls arastirma kutuphane sunucu ornekler" -- ls arastirma kutuphane sunucu ornekler
             T 4.1 kurulum --goster "uv sync && curl -s localhost:8199/saglik" -- bash -c "uv sync 2>&1 | tail -3; curl -s localhost:8199/saglik; echo"
             T 4.1 ilk-kosum -- uv run python -m arastirma.hat "Yeşilkent'te scooter park alanı ve maliyeti"; }
sec 4.2 && { T 4.2 istem -- sed -n '/^SISTEM/,/\"\"\"$/p' arastirma/orkestrator.py
             B 4.2 katalogsuz "/iz/$ILK?tur=bolme"; B 4.2 kataloglu "/iz/$ANA?tur=bolme"; }
sec 4.3 && { T 4.3 istem -- sed -n '/^ARASTIRMACI_SISTEM/,/\"\"\"$/p' arastirma/hat.py
             T 4.3 paralel-kod -- sed -n '/ThreadPoolExecutor(max_workers/,/tum.extend/p' arastirma/hat.py
             B 4.3 ic-ice "/iz/$ANA" --kaydir 420; }
sec 4.4 && { T 4.4 dogrulama --goster "uv run python -m arastirma.hat \"$KONU\" --onay" -- bash -c "printf 'e\n' | $HAT \"$KONU\" --onay | sed -n '/bulgu doğrulama/,\$p' | grep -v '^─' | head -30"
             son > iz/ONAY_KOSUM
             B 4.4 rapor "/rapor/$(cat iz/ONAY_KOSUM)"; B 4.4 kaynak-bel-2026 /belge/BEL-2026; }
sec 4.5 && { T 4.5 kontrol -- bash kontrol.sh; T 4.5 maliyet -- cat iz/$ANA/ozet.json
             T 4.5 paket -- ls -la iz/$ANA; }
echo "EKRANLAR TAMAM"
