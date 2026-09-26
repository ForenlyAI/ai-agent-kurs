#!/usr/bin/env bash
# Codespaces kurulumu: uv + hattın bağımlılıkları + Ollama + kursun modeli (Qwen3-4B-Instruct-2507, 4 bit, ~2,5 GB).
# Model GPU'suz, işlemcide koşar; model adı "yerel" olarak kopyalanır, istemci.py'de değişiklik gerekmez.
set -e
pip install --user --quiet uv
uv sync
sudo apt-get update -qq && sudo apt-get install -y -qq zstd >/dev/null
curl -fsSL https://ollama.com/install.sh | sh
(ollama serve > /tmp/ollama.log 2>&1 &)
until curl -sf localhost:11434/api/tags >/dev/null; do sleep 1; done
ollama pull qwen3:4b-instruct
ollama cp qwen3:4b-instruct yerel
echo "Hazır: bash kontrol.sh"
