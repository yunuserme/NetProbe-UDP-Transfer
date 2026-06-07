# NetProbe: UDP Tabanlı Güvenilir Dosya Aktarım ve Performans Analiz Platformu

NetProbe, taşıma katmanının bağlantısız ve güvenilmez (unreliable) protokolü olan UDP üzerinde, uygulama katmanında durum takibi yapan kararlı bir iletişim mimarisi (RDT - Reliable Data Transfer) inşa etmek amacıyla geliştirilmiş özgün bir platformdur. Proje kapsamında, kayıplı ağ koşullarında verilerin bit düzeyinde hatasız iletilmesini sağlamak adına **Stop-and-Wait ARQ** akış kontrol protokolü hayata geçirilmiştir.

## 🚀 Öne Çıkan Özellikler

* **Özgün Paket Başlığı (Custom Header):** Heterojen mimariler arasında yorumlanabilir tutarlılık sağlamak adına ağ bayt sıralamasına (Big-Endian) uygun, `struct` mimarisiyle paketlenmiş 11 baytlık özelleştirilmiş başlık yapısı.
* **Kriptografik Bütünlük Kontrolü (MD5 Checksum):** İletim esnasında fiziksel veya elektriksel gürültülerden kaynaklanabilecek bit bozulmalarını engellemek amacıyla segment bazlı MD5 özet doğrulama sistemi.
* **Hata ve Akış Kontrol Mekanizmaları:** Soket kilitlenmelerini önleyen statik zaman aşımı yönetimi (Timeout: 100ms), maksimum tekrar deneme sınırı (Max Attempt: 5) ve mükerrer (Duplicate) paket filtreleme algoritması.
* **Ağ Kayıp Simülasyon Modülü:** Gerçek ağ omurgasındaki yönlendirici kuyruk taşmalarını laboratuvar ortamında simüle edebilen, sunucu tarafında parametrik olarak ayarlanabilir ağ kayıp simülatörü.
* **Gelişmiş İzleme ve Analiz:** Her ağ olayını (`SEND`, `ACK`, `TIMEOUT`) milisaniye hassasiyetinde `.csv` formatında kayıt altına alan trafik loglama motoru ve bu verileri Pandas/Matplotlib ile işleyerek RTT ve dağılım grafiklerini otomatik üreten analiz aracı.

## 📂 Proje Dizin Yapısı

```text
├── alinan_dosyalar/      # Sunucu tarafından başarıyla birleştirilen dosyaların kaydedildiği dizin
├── client.py             # Dosyayı segmentlere ayırıp Stop-and-Wait ARQ ile gönderen istemci kodu
├── server.py             # Paketleri kabul eden, bütünlük kontrolü yapan ve ağ kaybını simüle eden sunucu kodu
├── analiz.py             # İstemci loglarını işleyerek performans grafiklerini (`.png`) üreten analiz modülü
├── server_log.txt        # Sunucu tarafı transfer istatistiklerinin geçmiş özet kayıtları
└── README.md             # Proje genel dökümantasyonu ve kullanım kılavuzu
```

## 🛠️ Kurulum ve Bağımlılıklar

Projenin temel ağ iletişimi Python standart kütüphaneleriyle (`socket`, `struct`, `hashlib`) gerçekleştirildiğinden ek bir kurulum gerektirmez. Ancak `analiz.py` performans görselleştirme modülünün çalışabilmesi için `pandas` ve `matplotlib` kütüphanelerinin yüklü olması gerekmektedir:

```bash
pip install pandas matplotlib
```

## 💻 Kullanım Kılavuzu

### 1. Sunucuyu Başlatma

Sunucu, ağ katmanındaki paket düşme senaryolarını test etmek amacıyla varsayılan olarak %30 yapay paket kaybı olasılığı ile çalışır. İsteğe bağlı olarak `--loss` parametresiyle bu oran değiştirilebilir (Örn: `0.1` girilerek %10 kayıp simüle edilebilir):

```bash
# Varsayılan senaryo (%30 yapay paket kaybı ile) başlatma
python server.py

# Alternatif senaryo (%10 paket kaybı ile) başlatma
python server.py --loss 0.1
```

### 2. İstemciden Dosya Gönderme

Sunucu `localhost:9999` portu üzerinde dinleme moduna geçtikten sonra, istemci terminalinden gönderilmek istenen dosya yolu `--file` parametresiyle belirtilerek transfer başlatılır:

```bash
python client.py --file test.txt
```

### 3. Ağ Performans Analizini Çalıştırma

Dosya transferi başarıyla tamamlandıktan veya kritik hata ile kesildikten sonra, istemci dizininde anlık zaman damgasıyla üretilen en güncel `.csv` log dosyasını işlemek ve ağ performans grafiklerini (`grafik_durum.png`, `grafik_rtt.png`) üretmek için:

```bash
python analiz.py
```

## 📊 Örnek Performans Özet Çıktısı

`analiz.py` çalıştırıldığında terminale basılan örnek ağ analiz verileri şu şekildedir:

```
========================================
        AĞ PERFORMANS ANALİZİ
========================================
 Toplam Gönderim Denemesi : 3418
 Başarılı İletilen Paket  : 3100
 Yaşanan Timeout (Kayıp)  : 318
 Retransmission Oranı     : %9.30
 Ortalama RTT (Gecikme)   : 0.0031 saniye
========================================
[+] grafik_rtt.png kaydedildi.
[+] grafik_durum.png kaydedildi.
```

## 👥 Proje Ekibi ve Görev Dağılımı

**Ahmet Can Yarba (21360859076):** Uçtan uca sistem entegrasyon testleri, karşılaştırmalı deney senaryolarının kurgulanması, akademik dökümantasyon/teknik rapor yazımı, kod kalitesi denetimi ve README mimarisinin oluşturulması. Sunum dosyası.

**Ali Deveci (22360859026):** İstemci ve sunucu soket programlama altyapısının kurulması, özel paket başlığı mimarisi, segment parçalama/birleştirme algoritmaları ve MD5 bütünlük doğrulama fonksiyonları.

**Yunus Emre Erkuş (23360859036):** Milisaniye hassasiyetli CSV trafik loglama motoru, yapay ağ kayıp simülasyon modülü, mükerrer (duplicate) paket filtreleme mimarisi ve Pandas/Matplotlib tabanlı performans analiz aracı.

## GitHub Repo Linki
https://github.com/yunuserme/NetProbe-UDP-Transfer.git
