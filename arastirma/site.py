"""Lab'ın tarayıcı yüzü — kütüphane, iz kaydı ve rapor (standart kitaplık, bağımlılık yok).

    uv run python -m arastirma.site            # http://localhost:8070

  /                 kütüphane kataloğu (17 belge, tür ve tarih)
  /ara?q=…          ajanın ara aracıyla AYNI arama (kutuphane.ara)
  /belge/<kimlik>   belgenin tam metni — ajanın belge_getir ile okuduğu metin
  /kosumlar         iz klasöründeki koşumlar
  /iz/<koşum>       koşumun adım adım iz kaydı (model / araç / doğrulama / hata)
  /rapor/<koşum>    derlenmiş rapor + özet
"""
from __future__ import annotations

import html
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from . import kutuphane
from .iz import IZ_KOK

FONT = Path(__file__).resolve().parent.parent / "araclar" / "fonts"
CSS = """
@font-face{font-family:M;src:url(/font/jetbrains-mono-400-latin.woff2) format("woff2");unicode-range:U+0000-00FF,U+0131,U+2000-206F}
@font-face{font-family:M;src:url(/font/jetbrains-mono-400-latin-ext.woff2) format("woff2");unicode-range:U+0100-024F}
*{box-sizing:border-box}body{margin:0;background:#f5f3ee;color:#1d2230;font:18px/1.5 system-ui,"DejaVu Sans",sans-serif}
header{background:#1d2230;color:#f5f3ee;padding:12px 24px;display:flex;gap:28px;align-items:center}
header b{font-size:18px;letter-spacing:.2px}header a{color:#c9d1e3;text-decoration:none;font-size:15px}
.ornek{margin-left:auto;background:#e8b84a;color:#1d2230;font:600 12px/1 M,monospace;padding:6px 9px;border-radius:4px}
main{max-width:1180px;margin:0 auto;padding:18px 24px}h1{font-size:27px;margin:0 0 6px}h2{font-size:19px;margin:22px 0 8px}
.alt{color:#5b6275;font-size:16px;margin-bottom:14px}
table{border-collapse:collapse;width:100%;background:#fff;border:1px solid #dcd8cf;font-size:16px}
th,td{text-align:left;padding:8px 11px;border-bottom:1px solid #ebe7de;vertical-align:top}th{background:#ece8df;font-weight:600}
td.m,span.m{font-family:M,monospace;font-size:15px}.r{text-align:right}
.tur{display:inline-block;padding:2px 7px;border-radius:3px;font-size:12px;font-weight:600;background:#e3e7f0}
.t-model{background:#dde8ff}.t-arac{background:#dff3e6}.t-dogrulama{background:#fff1cc}.t-hata{background:#ffd9d4}.t-bolme{background:#efe0ff}
.kutu{background:#fff;border:1px solid #dcd8cf;padding:18px 22px;border-radius:4px}
form{display:flex;gap:8px;margin:0 0 18px}input{flex:1;font:16px system-ui;padding:9px 12px;border:1px solid #bbb;border-radius:4px}
button{font:600 15px system-ui;padding:9px 18px;border:0;border-radius:4px;background:#1d2230;color:#fff}
.uyari{background:#fff1cc;border-left:4px solid #e8b84a;padding:8px 12px;font-size:14px;margin:10px 0}
.red{color:#b3261e}.ok{color:#1e7a44}pre{white-space:pre-wrap;font:14px/1.5 M,monospace;margin:0}
"""


ETIKET = {"model": "model", "arac": "araç", "bolme": "bölme", "dogrulama": "doğrulama", "hata": "hata", "onay": "onay"}


def sayfa(baslik: str, govde: str) -> bytes:
    return (f'<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8"><title>{html.escape(baslik)}</title>'
            f'<style>{CSS}</style></head><body><header><b>Araştırma Hattı · Lab</b>'
            f'<a href="/">Kütüphane</a><a href="/kosumlar">Koşumlar</a><span class="ornek">ÖRNEK VERİ</span></header>'
            f'<main>{govde}</main></body></html>').encode()


def e(s) -> str:
    return html.escape(str(s))


def katalog() -> str:
    satir = "".join(f'<tr><td class="m"><a href="/belge/{b.kimlik}">{b.kimlik}</a></td><td>{e(b.baslik)}</td>'
                    f'<td>{e(b.tur)}</td><td class="m">{b.tarih}</td></tr>' for b in kutuphane.tum_belgeler())
    return (f'<h1>Kütüphane</h1><div class="alt">Ajanların araştırdığı {len(kutuphane.tum_belgeler())} belge · '
            f'arama, ajanın <span class="m">ara</span> aracıyla aynı işlevi kullanır</div>'
            f'<form action="/ara"><input name="q" placeholder="ör. kaza sayısı"><button>Ara</button></form>'
            f'<table><tr><th>Kimlik</th><th>Başlık</th><th>Tür</th><th>Tarih</th></tr>{satir}</table>')


def ara(q: str) -> str:
    sonuc = kutuphane.ara(q)
    satir = "".join(f'<tr><td class="m r">{p}</td><td class="m"><a href="/belge/{b.kimlik}">{b.kimlik}</a></td>'
                    f'<td><b>{e(b.baslik)}</b><br><span style="color:#5b6275">{e(b.ozet)}…</span></td><td class="m">{b.tarih}</td></tr>'
                    for b, p in sonuc)
    return (f'<h1>Arama</h1><form action="/ara"><input name="q" value="{e(q)}"><button>Ara</button></form>'
            f'<div class="alt">{len(sonuc)} sonuç · puan: başlıkta geçen kelime 3, metinde geçen 1</div>'
            f'<table><tr><th class="r">Puan</th><th>Kimlik</th><th>Başlık ve özet</th><th>Tarih</th></tr>{satir}</table>')


def belge(k: str) -> str:
    b = kutuphane.getir(k)
    if not b:
        return f"<h1>Belge yok</h1><p>'{e(k)}' kimliğiyle bir belge yok.</p>"
    govde = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", e(b.govde)).replace("\n", "<br>")
    return (f'<div class="alt m">{b.kimlik} · {e(b.tur)} · {b.tarih}</div><h1>{e(b.baslik)}</h1>'
            f'<div class="alt">{e(b.yayinci)}</div><div class="uyari">Güvenilirlik notu: {e(b.guvenilirlik)}</div>'
            f'<div class="kutu" style="font-size:17px;line-height:1.7">{govde}</div>')


def kosumlar() -> str:
    ds = sorted([d for d in IZ_KOK.iterdir() if (d / "ozet.json").exists()], reverse=True)
    satir = ""
    for d in ds:
        o = json.loads((d / "ozet.json").read_text())
        satir += (f'<tr><td class="m"><a href="/iz/{d.name}">{d.name}</a></td><td class="r">{o["model_cagrisi"]}</td>'
                  f'<td class="r">{o["arac_cagrisi"]}</td><td class="r">{o["hata"]}</td><td class="r m">{o["toplam_token"]:,}</td>'
                  f'<td class="r">{o["sure_sn"]} sn</td><td><a href="/rapor/{d.name}">rapor</a></td></tr>').replace(",", ".")
    return (f'<h1>Koşumlar</h1><div class="alt">lab/iz/ klasörü · her koşum bir klasör</div>'
            f'<table><tr><th>Koşum</th><th class="r">Model</th><th class="r">Araç</th><th class="r">Hata</th>'
            f'<th class="r">Token</th><th class="r">Süre</th><th></th></tr>{satir}</table>')


def iz(k: str, q: dict) -> str:
    d = IZ_KOK / k
    if not (d / "olaylar.jsonl").exists():
        return "<h1>Koşum yok</h1>"
    olaylar = [json.loads(x) for x in (d / "olaylar.jsonl").read_text().splitlines() if x.strip()]
    suz = q.get("ajan", [""])[0]
    tur = q.get("tur", [""])[0]
    if suz:
        olaylar = [o for o in olaylar if suz in o.get("ajan", "")]
    if tur:
        olaylar = [o for o in olaylar if o["tur"] == tur]
    satir = ""
    for o in olaylar:
        if o["tur"] == "model":
            ayr = f'giriş <b>{o["giris"]:,}</b> · çıkış {o["cikis"]} token · {o["gecikme_sn"]} sn'.replace(",", ".")
        elif o["tur"] == "arac":
            sinir = 400 if o["ad"] == "bulgu_kaydet" else 90   # bulgunun tamamı görünsün (ders 1.2, 2.5)
            ayr = f'<span class="m">{e(o["ad"])}({e(json.dumps(o["girdi"], ensure_ascii=False))[:sinir]})</span><br><span style="color:#5b6275">→ {e(o["sonuc"][:120])}</span>'
        elif o["tur"] == "dogrulama":
            c = "ok" if o["karar"] == "geçti" else "red"
            ayr = f'<span class="{c}"><b>{o["karar"]}</b></span> [{o["kaynak"]}] {e(o["bulgu"][:90])}' + ("" if c == "ok" else f'<br><span class="red">{e(o["neden"])}</span>')
        elif o["tur"] == "bolme":
            ayr = "<br>".join(f"{i}. {e(s)}" for i, s in enumerate(o["sorular"], 1))
        elif o["tur"] == "hata":
            ayr = f'<span class="red">{e(o["mesaj"])}</span>'
        else:
            ayr = e(json.dumps({k: v for k, v in o.items() if k not in ("t", "tur")}, ensure_ascii=False))
        satir += (f'<tr><td class="m r">{o["t"]:.1f}</td><td><span class="tur t-{o["tur"]}">{ETIKET.get(o["tur"], o["tur"])}</span></td>'
                  f'<td class="m">{e(o.get("ajan", ""))[:34]}</td><td>{ayr}</td></tr>')
    baslik = f"İz kaydı" + (f" · {e(suz)}" if suz else "") + (f" · yalnız {ETIKET.get(tur, e(tur))}" if tur else "")
    return (f'<h1>{baslik}</h1><div class="alt m">{e(k)} · olaylar.jsonl · {len(olaylar)} olay</div>'
            f'<table><tr><th class="r">sn</th><th>tür</th><th>ajan</th><th>ayrıntı</th></tr>{satir}</table>')


def rapor(k: str) -> str:
    d = IZ_KOK / k
    if not (d / "rapor.md").exists():
        return "<h1>Rapor yok</h1><p>Bu koşum rapor üretmeden bitti.</p>"
    o = json.loads((d / "ozet.json").read_text())
    md = e((d / "rapor.md").read_text())
    md = re.sub(r"^# (.+)$", r"<h1>\1</h1>", md, flags=re.M)
    md = re.sub(r"^## (.+)$", r"<h2>\1</h2>", md, flags=re.M)
    md = re.sub(r"^- (.+)$", r"<li>\1</li>", md, flags=re.M)
    md = re.sub(r"\[([A-Z0-9\-]{3,})\]", r'<a class="m" href="/belge/\1">[\1]</a>', md)
    ozet = (f'{o["model_cagrisi"]} model çağrısı · {o["arac_cagrisi"]} araç çağrısı · {o["hata"]} hata · '
            f'{o["toplam_token"]:,} token · {o["sure_sn"]} sn').replace(",", ".")
    return f'<div class="alt m">{e(k)} · {ozet}</div><div class="kutu">{md}</div>'


class Islem(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        yol = unquote(u.path)
        if yol.startswith("/font/"):
            f = FONT / Path(yol).name
            if f.exists():
                self.send_response(200); self.send_header("Content-Type", "font/woff2"); self.end_headers()
                self.wfile.write(f.read_bytes()); return
        if yol == "/":
            g = sayfa("Kütüphane", katalog())
        elif yol == "/ara":
            g = sayfa("Arama", ara(q.get("q", [""])[0]))
        elif yol.startswith("/belge/"):
            g = sayfa("Belge", belge(yol[7:]))
        elif yol == "/kosumlar":
            g = sayfa("Koşumlar", kosumlar())
        elif yol.startswith("/iz/"):
            g = sayfa("İz", iz(yol[4:], q))
        elif yol.startswith("/rapor/"):
            g = sayfa("Rapor", rapor(yol[7:]))
        else:
            self.send_response(404); self.end_headers(); return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(g)


def main() -> None:
    print("Araştırma Hattı · Lab → http://localhost:8070", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 8070), Islem).serve_forever()


if __name__ == "__main__":
    main()
