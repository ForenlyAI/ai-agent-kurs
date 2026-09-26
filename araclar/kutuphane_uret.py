"""Kütüphane belgelerini üretir — AI Agent 101 lab'ının araştırma kaynağı.

ÖRNEK VERİ: Yeşilkent uydurma bir şehirdir, belgelerin tamamı kurs için yazılmıştır.
Gerçek bir kurum, kişi ya da ölçüm değildir. Kasıtlı olarak içerir:
  · aynı büyüklüğü farklı veren iki kaynak (BEL-2026 vs SEK-2026 filo sayısı)
  · eski tarihli, hâlâ dolaşan bir rapor (BEL-2024)
  · kaynak göstermeyen düşük kaliteli bir gönderi (FOR-01)
  · pazarlama dilli bir basın bülteni (OPR-01)
Ajanın bunları ayırt etmesi 1.2, 2.5 ve 4.4 derslerinin konusudur.

    uv run python araclar/kutuphane_uret.py
"""
from __future__ import annotations

from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
HEDEF = LAB / "kutuphane" / "belgeler"

# (kimlik, başlık, yayıncı, tür, tarih, güvenilirlik notu, gövde)
BELGELER = [
    ("BEL-2026", "Yeşilkent Mikromobilite Yıllık Raporu 2026", "Yeşilkent Belediyesi Ulaşım Daire Başkanlığı", "kurum raporu", "2026-03-14",
     "birincil kaynak — sayım belediye lisans kayıtlarından",
     """Yeşilkent'te lisanslı paylaşımlı elektrikli scooter sayısı 2026 Mart itibarıyla **4.200**'dür. Bu rakam
belediyenin verdiği filo lisanslarının toplamıdır; lisanssız araçlar sayıma girmez.
Günlük ortalama yolculuk sayısı 11.300, yolculuk başına ortalama mesafe 1,9 km'dir.
Yolculukların %62'si iş günlerinde 07:30–09:30 ve 17:00–19:00 aralığında yapılmaktadır.
2025 yılında kayda geçen scooter kaynaklı trafik kazası sayısı **318**, bu kazalarda yaralanan kişi sayısı 274'tür.
Kazaların %71'i kaldırım ya da yaya yolunda gerçekleşmiştir.
Belediye, üç merkez mahallede azami hızı 20 km/s ile sınırlayan bir pilot uygulama yürütmektedir (bkz. PIL-2026).
Park ihlali bildirimi 2025'te 9.480 adettir; bunların 3.150'si erişim engeli gerekçesiyle yapılmıştır."""),

    ("BEL-2024", "Yeşilkent Mikromobilite Durum Raporu 2024", "Yeşilkent Belediyesi Ulaşım Daire Başkanlığı", "kurum raporu", "2024-02-09",
     "ESKİ — 2026 raporu (BEL-2026) bu sayıların yerini almıştır; hâlâ sık alıntılanır",
     """Yeşilkent'te paylaşımlı elektrikli scooter sayısı **1.850**'dir. Günlük yolculuk sayısı 4.100 civarındadır.
2023 yılında kayda geçen scooter kaynaklı kaza sayısı 96'dır.
Rapor, filonun önümüzdeki iki yılda büyümesi hâlinde kaldırım kullanımının temel sorun hâline geleceğini
öngörmektedir. Azami hız sınırı o tarihte 25 km/s'dir ve mahalle bazlı bir kısıt bulunmamaktadır.
Park için ayrılmış işaretli alan sayısı 40'tır."""),

    ("SEK-2026", "Paylaşımlı Mikromobilite Sektör Değerlendirmesi 2026", "Mikromobilite Operatörleri Derneği", "sektör raporu", "2026-04-02",
     "sektör derneği — üye beyanına dayanır, belediye lisans sayısından farklıdır",
     """Derneğimizin üyesi dört operatörün Yeşilkent'te işlettiği toplam araç sayısı **5.600**'dür.
Sayı, bakımda ve depoda bekleyen araçları da içerir; sokakta aynı anda bulunan araç sayısı ortalama 3.900'dür.
Bu fark, belediye lisans kayıtlarıyla karşılaştırma yapılırken sık sık gözden kaçmaktadır.
Sektör, yolculuk başına ortalama gelirin 2025'te 18,40 TL olduğunu bildirmektedir.
Dernek, kaldırım kullanımını azaltmanın yolunun yasak değil ayrılmış şerit olduğunu savunmaktadır."""),

    ("UNI-PARK", "Kaldırımda Park: Yeşilkent Merkez Ölçümü", "Yeşilkent Teknik Üniversitesi Ulaştırma Bölümü", "akademik çalışma", "2026-01-22",
     "hakemli değil, bölüm çalışma raporu — yöntemi açık yazılmış",
     """Çalışma, merkez üç mahallede 14 gün boyunca günde iki kez sahada sayım yapmıştır (toplam 28 tur, 1.120 araç gözlemi).
Gözlenen araçların **%38'i** yaya geçişini ya da kaldırım genişliğini 1,5 m'nin altına düşürecek şekilde park edilmiştir.
İşaretli park alanı bulunan sokaklarda bu oran %11'e düşmektedir.
Çalışma, park ihlalinin cezayla değil işaretli alan yoğunluğuyla ilişkili olduğunu bulmuştur (r = -0,64).
Sınırlılık: ölçüm yalnız merkez mahallelerde ve kış aylarında yapılmıştır; yaz dönemi için genellenemez."""),

    ("UNI-KAZA", "Scooter Kazalarının Hastane Kayıtlarıyla İncelenmesi", "Yeşilkent Teknik Üniversitesi ve Yeşilkent Devlet Hastanesi", "akademik çalışma", "2026-02-18",
     "hastane kayıtlarına dayalı — trafik kaydından daha geniş, kayda geçmeyen kazaları da içerir",
     """2025 yılında acil servise scooter kaynaklı yaralanmayla başvuran hasta sayısı **512**'dir.
Bu sayı, aynı yıl trafik kaydına geçen 318 kazadan belirgin şekilde yüksektir; aradaki fark, tek taraflı
düşmelerin çoğunun trafik kaydına girmemesinden kaynaklanmaktadır.
Başvuruların %61'i 18–29 yaş aralığındadır. Kask kullandığını bildiren hasta oranı **%7**'dir.
Yaralanmaların %44'ü el, bilek ve ön kol, %19'u baş bölgesindedir.
Baş yaralanmalarının ciddiyeti kask kullananlarda belirgin biçimde düşüktür, ancak örneklem (n=36) küçüktür."""),

    ("PIL-2026", "20 km/s Hız Sınırı Pilotu — Üç Aylık Sonuç", "Yeşilkent Belediyesi Ulaşım Daire Başkanlığı", "kurum raporu", "2026-05-06",
     "birincil kaynak — pilot bölge ile kontrol bölgesi karşılaştırılmış",
     """Pilot, üç merkez mahallede azami hızı coğrafi sınırlamayla 20 km/s'ye indirmiştir (önceki sınır 25 km/s).
Üç aylık dönemde pilot bölgede kaza sayısı bir önceki yılın aynı dönemine göre **%23** azalmıştır (41'den 32'ye).
Aynı dönemde kontrol bölgesinde azalma %4'tür.
Yolculuk sayısı pilot bölgede %6 düşmüştür; operatörler bu düşüşün hız kısıtından kaynaklandığını bildirmektedir.
Rapor, üç ayın mevsim etkisini ayırmaya yetmediğini ve sonucun bir yıllık veriyle doğrulanması gerektiğini yazmaktadır."""),

    ("YON-2025", "Elektrikli Skuter Kullanım Yönetmeliği — Özet", "Yeşilkent Belediye Meclisi", "mevzuat özeti", "2025-11-30",
     "kurum metni — yürürlükteki kuralların özeti",
     """Yönetmelik, paylaşımlı elektrikli scooter işletmeciliğini lisansa bağlar. Başlıca hükümler:
azami hız 25 km/s (belediye kararıyla mahalle bazında düşürülebilir); 16 yaş sınırı; kaldırımda ve yaya
yolunda sürüş yasak; park yalnız işaretli alanlarda ya da yaya geçişini engellemeyecek biçimde;
her araçta işletmeci iletişim bilgisi ve araç kimliği görünür olmalı.
Park ihlalinde araç, bildirimden itibaren 2 saat içinde işletmeci tarafından kaldırılır; kaldırılmazsa
belediye kaldırır ve masrafı işletmeciye yansıtır.
Kask zorunluluğu yönetmelikte YOKTUR; öneri olarak yer alır."""),

    ("ANK-2026", "Yeşilkent Kent İçi Ulaşım Memnuniyet Anketi 2026", "Yeşilkent Belediyesi Strateji Müdürlüğü", "anket", "2026-04-20",
     "telefon anketi, n=1.200, ±%2,8 hata payı — yöntem açık",
     """Katılımcıların **%34'ü** paylaşımlı scooter'ı ayda en az bir kez kullandığını bildirmektedir.
Scooter'ların kentteki varlığından memnun olanların oranı %41, rahatsız olanların oranı %44'tür.
Rahatsızlığın en sık belirtilen üç nedeni: kaldırıma park (%68), yayaya yakın sürüş (%57), gece gürültüsü (%12).
Kullanıcılar arasında memnuniyet %73'tür; en sık şikâyet şarjı biten araç bulmaktır (%39).
65 yaş üstü katılımcılarda rahatsızlık oranı %61'e çıkmaktadır."""),

    ("ERS-2026", "Erişilebilirlik Denetimi: Kaldırımda Engel Raporu", "Yeşilkent Engelliler Meclisi", "sivil toplum raporu", "2026-03-02",
     "sivil toplum kuruluşu — saha gözlemi, yöntem kısmen açık",
     """14 güzergâhta yapılan denetimde, tekerlekli sandalye ya da beyaz baston kullanıcısının geçişini engelleyen
**212** engel kaydedilmiştir. Bunların **%47'si** park hâlindeki elektrikli scooter'dır; kalanı seyyar tezgâh,
yanlış park etmiş otomobil ve inşaat malzemesidir.
Rapor, engelin kaldırılması için yapılan bildirimlerin ortalama **3 saat 40 dakika** sonra sonuçlandığını,
yönetmelikteki 2 saatlik sürenin aşıldığını bildirmektedir.
Öneri: işaretli park alanlarının kavşak ve durak çevresinde zorunlu kılınması."""),

    ("MAL-2026", "Mikromobilite Altyapı Maliyet Analizi", "Yeşilkent Belediyesi Mali Hizmetler Müdürlüğü", "kurum raporu", "2026-02-28",
     "bütçe kalemlerinden — birim maliyetler gerçek ihale bedellerinden",
     """İşaretli park alanı yapım maliyeti alan başına ortalama 14.500 TL'dir (zemin işaretleme, direk, tabela).
2025'te 160 alan yapılmış, toplam 2,32 milyon TL harcanmıştır.
Ayrılmış mikromobilite şeridi maliyeti kilometre başına 480.000 TL'dir; 2025'te 6 km yapılmıştır.
Lisans gelirleri araç başına yıllık 1.200 TL'dir; 4.200 araç için yıllık gelir 5,04 milyon TL'dir.
Rapor, park alanı yatırımının lisans geliriyle karşılandığını, şerit yatırımının ise genel bütçeden
desteklenmesi gerektiğini belirtmektedir."""),

    ("KAR-2026", "Üç Şehir Karşılaştırması: Mikromobilite Düzenlemeleri", "Kent Araştırmaları Enstitüsü", "karşılaştırmalı çalışma", "2026-01-10",
     "ikincil kaynak — başka şehirlerin kendi raporlarından derlenmiştir",
     """Akdere: filo üst sınırı nüfusun binde 3'ü, azami hız 20 km/s, kask zorunlu. Kaza oranı 100 bin yolculukta 1,4.
Yeşilkent: filo üst sınırı yok, azami hız 25 km/s, kask önerilir. Kaza oranı 100 bin yolculukta 2,6.
Bozyaka: filo üst sınırı yok, azami hız 20 km/s, kask önerilir, kaldırım sürüşünde araç otomatik durur. Kaza oranı 1,9.
Çalışma, kask zorunluluğu ile kaza SAYISI arasında değil, yaralanma CİDDİYETİ arasında ilişki bulmuştur.
Uyarı: üç şehrin kaza kayıt yöntemi farklıdır; oranlar doğrudan karşılaştırılamaz."""),

    ("BAT-2026", "Batarya Ömrü ve Araç Yaşam Döngüsü", "Mikromobilite Operatörleri Derneği", "sektör raporu", "2026-03-19",
     "sektör derneği — üye beyanı, bağımsız doğrulama yok",
     """Paylaşımlı araçların ortalama hizmet ömrü **22 ay**'dır; 2021'de bu süre 9 aydı.
Batarya ortalama 620 şarj döngüsünden sonra kapasitesinin %80'ine düşmektedir.
Araç başına yıllık bakım maliyeti 3.400 TL'dir. Toplama ve şarj işlemi yolculuk başına 4,10 TL maliyet üretir.
Dernek, hizmet ömrü uzadıkça araç başına karbon ayak izinin düştüğünü, ancak toplama araçlarının
dizel olması hâlinde kazancın büyük ölçüde kaybolduğunu belirtmektedir."""),

    ("FOR-01", "Bu scooterlar yüzünden yürüyemez olduk", "Yeşilkent Mahalle Forumu — kullanıcı gönderisi", "forum gönderisi", "2026-04-28",
     "DÜŞÜK KALİTE — kaynak göstermiyor, sayılar doğrulanamıyor, kişisel gözlem",
     """Bizim sokakta her gün en az 50 tane scooter park ediyor, hiçbiri düzgün değil.
Duyduğuma göre şehirde 10 binden fazla scooter varmış, belediye saklıyormuş.
Geçen hafta üç kaza gördüm, hiçbiri kayda geçmedi. Kazaların gerçek sayısı açıklananın en az beş katıdır.
Bence tamamen yasaklanmalı. Komşum da aynı fikirde."""),

    ("OPR-01", "Yeşilkent'te 10 Milyonuncu Yolculuk", "HızlıGo Mikromobilite A.Ş. — basın bülteni", "basın bülteni", "2026-05-12",
     "PAZARLAMA DİLİ — şirketin kendi duyurusu, bağımsız doğrulama yok",
     """HızlıGo olarak Yeşilkent'te 10 milyonuncu yolculuğu gururla kutluyoruz!
Kullanıcılarımız bu yolculuklarla tahminen 1.400 ton karbon salımını önledi.
Filomuz şehrin en genç filosu; araçlarımızın %90'ı son 12 ayda yenilendi.
Güvenlik bizim için her şeyden önce geliyor: uygulamamızda sürüş öncesi güvenlik hatırlatması gösteriyoruz.
Yeşilkent'in ulaşım dönüşümüne öncülük etmekten mutluyuz."""),

    ("HAB-01", "Meclis, kaldırım düzenlemesini ikinci kez erteledi", "Yeşilkent Haber", "haber", "2026-05-20",
     "haber — meclis tutanağına dayanıyor, tek muhabir",
     """Belediye meclisi, mikromobilite şeridi düzenlemesini ikinci kez ertelemiştir.
Ulaşım Daire Başkanlığı, pilot bölge sonuçlarının bir yıllık veriyle doğrulanmasını beklediklerini bildirdi.
Engelliler Meclisi temsilcisi, erteleme kararına tepki göstererek denetim raporundaki 3 saat 40 dakikalık
müdahale süresine dikkat çekti.
Operatör temsilcileri ise filo üst sınırı getirilmesine karşı olduklarını yineledi.
Konunun eylül ayındaki oturumda yeniden ele alınması bekleniyor."""),

    ("HAV-2026", "Mikromobilitenin Yer Değiştirdiği Ulaşım Türleri", "Yeşilkent Teknik Üniversitesi Ulaştırma Bölümü", "akademik çalışma", "2026-04-11",
     "anket tabanlı (n=840) — beyana dayalı, gerçek yolculuk kaydı değil",
     """Kullanıcılara son scooter yolculuğunu scooter olmasaydı nasıl yapacakları sorulmuştur.
Cevaplar: yürüyerek %41, toplu taşıma %27, otomobil %18, taksi %9, yolculuğu yapmazdım %5.
Bu dağılım, scooter yolculuklarının çoğunlukla otomobil yerine değil YÜRÜYÜŞ yerine geçtiğini göstermektedir.
Dolayısıyla karbon kazancı, operatör duyurularında verilen rakamlardan belirgin biçimde düşüktür.
Sınırlılık: beyana dayalıdır ve kullanıcılar çevreci cevaba yönelme eğilimi gösterebilir."""),

    ("GOR-01", "Yasak değil tasarım: mikromobilite üzerine", "Kent Araştırmaları Enstitüsü — görüş yazısı", "görüş yazısı", "2026-05-02",
     "GÖRÜŞ — yazarın değerlendirmesi, yeni veri içermez",
     """Yeşilkent tartışması yanlış soruyla yürüyor: "yasaklayalım mı" değil, "nereye koyalım" sorusu sorulmalı.
Kaldırım çatışmasının kaynağı scooter'ın kendisi değil, ona ayrılmış yerin olmamasıdır.
Park ölçümü, işaretli alan bulunan sokaklarda ihlalin üçte bire düştüğünü göstermektedir.
Hız pilotunun sonucu umut vericidir ama üç ay kısa bir süredir.
Meclisin ertelediği şerit düzenlemesi, tartışmanın asıl konusudur."""),
]

SABLON = """---
kimlik: {kimlik}
baslik: {baslik}
yayinci: {yayinci}
tur: {tur}
tarih: {tarih}
guvenilirlik: {guv}
ornek_veri: true
---

# {baslik}

**{yayinci}** · {tur} · {tarih}

{govde}

---
*ÖRNEK VERİ — Yeşilkent uydurma bir şehirdir. Bu belge AI Agent 101 kursu için yazılmıştır; gerçek bir kurum, kişi ya da ölçüm değildir.*
"""


def main() -> None:
    HEDEF.mkdir(parents=True, exist_ok=True)
    for kimlik, baslik, yayinci, tur, tarih, guv, govde in BELGELER:
        (HEDEF / f"{kimlik}.md").write_text(
            SABLON.format(kimlik=kimlik, baslik=baslik, yayinci=yayinci, tur=tur, tarih=tarih, guv=guv, govde=govde.strip()),
            encoding="utf-8")
    print(f"{len(BELGELER)} belge yazıldı → {HEDEF.relative_to(LAB)}")


if __name__ == "__main__":
    main()
