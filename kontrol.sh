#!/usr/bin/env bash
# AI Agent 101 lab — bütün parçaları dener, her adım için GEÇTİ / KALDI yazar (ders 3.5, 4.5).
#   bash kontrol.sh            # tam (uçtan uca kısa koşum dahil, ~1-2 dk)
#   bash kontrol.sh --hizli    # model çağırmadan
cd "$(dirname "$0")"
URL="${AJAN_MODEL_URL:-http://127.0.0.1:8199/v1/chat/completions}"
SAGLIK="${URL%/v1/chat/completions}/saglik"
gecen=0; kalan=0
adim() { if eval "$2" >/dev/null 2>&1; then echo "GEÇTİ  $1"; gecen=$((gecen+1)); else echo "KALDI  $1"; kalan=$((kalan+1)); fi; }

adim "ortam kilitli (uv sync --frozen)"                "uv sync --frozen --quiet"
adim "kütüphane 17 belge"                               "[ \$(ls kutuphane/belgeler/*.md | wc -l) -ge 17 ]"
adim "doğrulayıcı testi 12/12"                          "uv run --quiet python -m arastirma.test_dogrula"
adim "araçlar: olmayan belge anlaşılır hata verir"      "uv run --quiet python -c \"from arastirma import araclar as a; assert 'Mevcut kimlikler' in a.kutu_ile([])['belge_getir'](kimlik='YOK-1')\""
adim "araçlar: yalnız okuyan araçlar (en az yetki)"     "uv run --quiet python -c \"from arastirma import araclar as a; assert {x['function']['name'] for x in a.SEMA} == {'ara','belge_getir','bulgu_kaydet'}\""
if [ "$1" != "--hizli" ]; then
  adim "model sunucusu sağlık ($SAGLIK)"                "curl -sf -m 10 $SAGLIK | grep -q hazir || curl -sf -m 10 ${URL%/v1/chat/completions}/api/tags | grep -q yerel"   # GPU sunucusu ya da Ollama (Codespaces)
  adim "model araç çağırıyor (tool_calls)"              "uv run --quiet python -c \"
from arastirma import istemci, araclar, hat
y = istemci.sor([{'role':'system','content':hat.ARASTIRMACI_SISTEM},{'role':'user','content':'Alt soru: 2025 kaza sayısı'}], araclar.SEMA)
assert y['mesaj'].get('tool_calls')\""
  adim "hat uçtan uca (rapor + kaynak denetimi)"        "uv run --quiet python -m arastirma.hat 'Yeşilkent scooter park sorunu' --ajan 2 --adim 5 | grep -q 'kaynak denetimi: GEÇTİ'"
fi
echo "────────────"
echo "$gecen GEÇTİ · $kalan KALDI"
[ "$kalan" -eq 0 ]
