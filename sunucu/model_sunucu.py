"""AI Agent 101 lab — yerel model sunucusu (sim, NVIDIA L4).

OpenAI uyumlu tek uç nokta: POST /v1/chat/completions  {model, messages, tools?, temperature?, max_tokens?}
Yanıt, araç çağrısı varsa message.tool_calls, yoksa message.content taşır; usage token sayılarını verir.

Bu dosya kursun 3.3 dersinin konusudur: ajanın konuştuğu servis. Öğrenci aynı arayüzü
ücretli bir sağlayıcıya çevirdiğinde hattın geri kalanı değişmez (AJAN_MODEL_URL).

    ~/vision/.venv/bin/python model_sunucu.py --port 8199
"""
from __future__ import annotations

import argparse
import json
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "Qwen/Qwen3-4B-Instruct-2507"
KILIT = threading.Lock()
TOK = MOD = None
ARAC_DESEN = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.S)


def yukle() -> None:
    global TOK, MOD
    bos = torch.cuda.mem_get_info()[0] // 1024**2
    if bos < 11000:
        raise SystemExit(f"GPU'da boş bellek {bos} MB < 11000 — başka iş koşuyor, sunucu açılmadı")
    print(f"yükleniyor… (GPU boş {bos} MB)", flush=True)
    TOK = AutoTokenizer.from_pretrained(MODEL)
    MOD = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="cuda")
    MOD.eval()
    print(f"hazır · {MODEL} · {torch.cuda.mem_get_info()[0] // 1024**2} MB boş kaldı", flush=True)


def uret(mesajlar: list[dict], araclar: list[dict] | None, sicaklik: float, azami: int) -> dict:
    metin = TOK.apply_chat_template(mesajlar, tools=araclar, tokenize=False, add_generation_prompt=True)
    giris = TOK([metin], return_tensors="pt").to(MOD.device)
    with torch.inference_mode():
        cikis = MOD.generate(**giris, max_new_tokens=azami, do_sample=sicaklik > 0,
                             temperature=sicaklik or None, top_p=0.8 if sicaklik else None,
                             pad_token_id=TOK.eos_token_id)
    yeni = cikis[0][giris.input_ids.shape[1]:]
    ham = TOK.decode(yeni, skip_special_tokens=True).strip()

    cagrilar = []
    for i, m in enumerate(ARAC_DESEN.finditer(ham)):
        try:
            c = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue   # bozuk JSON: araç çağrısı sayılmaz, metin olarak kalır (ders 2.2)
        cagrilar.append({"id": f"call_{int(time.time()*1000)}_{i}", "type": "function",
                         "function": {"name": c.get("name", ""), "arguments": json.dumps(c.get("arguments", {}), ensure_ascii=False)}})
    icerik = ARAC_DESEN.sub("", ham).strip()

    mesaj = {"role": "assistant", "content": icerik or None}
    if cagrilar:
        mesaj["tool_calls"] = cagrilar
    return {"choices": [{"index": 0, "message": mesaj, "finish_reason": "tool_calls" if cagrilar else "stop"}],
            "model": MODEL,
            "usage": {"prompt_tokens": int(giris.input_ids.shape[1]), "completion_tokens": int(yeni.shape[0]),
                      "total_tokens": int(giris.input_ids.shape[1] + yeni.shape[0])}}


class Islem(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):   # sessiz
        pass

    def _yaz(self, kod: int, govde: dict) -> None:
        g = json.dumps(govde, ensure_ascii=False).encode()
        self.send_response(kod)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(g)))
        self.end_headers()
        self.wfile.write(g)

    def do_GET(self):
        if self.path == "/saglik":
            self._yaz(200, {"durum": "hazir", "model": MODEL})
        else:
            self._yaz(404, {"hata": "yok"})

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            return self._yaz(404, {"hata": "yok"})
        try:
            istek = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        except json.JSONDecodeError:
            return self._yaz(400, {"hata": "gövde JSON değil"})
        t0 = time.time()
        try:
            with KILIT:   # tek GPU, tek üretim; paralel ajanlar burada sıraya girer (ders 3.2)
                y = uret(istek.get("messages", []), istek.get("tools"),
                         float(istek.get("temperature", 0.0)), int(istek.get("max_tokens", 1024)))
        except Exception as ex:
            return self._yaz(500, {"hata": f"{type(ex).__name__}: {ex}"})
        y["gecikme_sn"] = round(time.time() - t0, 2)
        self._yaz(200, y)


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--port", type=int, default=8199)
    n = a.parse_args()
    yukle()
    print(f"dinliyor :{n.port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", n.port), Islem).serve_forever()


if __name__ == "__main__":
    main()
