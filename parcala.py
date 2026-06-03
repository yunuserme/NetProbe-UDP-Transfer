import struct
import hashlib
import os

PAKET_BOYUTU = 1024  # her pakette maksimum 1024 byte veri

def dosyayi_parcala(dosya_yolu):
    # Dosyayı oku
    with open(dosya_yolu, "rb") as f:
        icerik = f.read()
    
    dosya_boyutu = len(icerik)
    paketler = []
    
    # Kaç parçaya bölüneceğini hesapla
    import math
    toplam_paket = math.ceil(dosya_boyutu / PAKET_BOYUTU)
    
    print(f"Dosya boyutu: {dosya_boyutu} byte")
    print(f"Paket boyutu: {PAKET_BOYUTU} byte")
    print(f"Toplam paket sayısı: {toplam_paket}")
    print()
    
    # Dosyayı parçala ve her parçayı paketle
    for i in range(toplam_paket):
        baslangic = i * PAKET_BOYUTU
        bitis = baslangic + PAKET_BOYUTU
        veri = icerik[baslangic:bitis]
        
        # Paketi oluştur
        paket = paket_olustur(
            seq_no=i,
            toplam_paket=toplam_paket,
            veri=veri
        )
        paketler.append(paket)
        
        print(f"Paket {i}: {len(veri)} byte veri, toplam {len(paket)} byte")
    
    return paketler

def paket_olustur(seq_no, toplam_paket, veri):
    tip = 1
    veri_uzunlugu = len(veri)
    checksum = hashlib.md5(veri).digest()
    header = struct.pack("!BIIH", tip, seq_no, toplam_paket, veri_uzunlugu)
    return header + checksum + veri

def paket_ac(paket):
    header = paket[:11]
    checksum_gelen = paket[11:27]
    veri = paket[27:]
    tip, seq_no, toplam_paket, veri_uzunlugu = struct.unpack("!BIIH", header)
    checksum_hesap = hashlib.md5(veri).digest()
    butunluk = checksum_gelen == checksum_hesap
    return {
        "tip": tip,
        "seq_no": seq_no,
        "toplam_paket": toplam_paket,
        "veri_uzunlugu": veri_uzunlugu,
        "veri": veri,
        "butunluk_ok": butunluk
    }

def parcalari_birlestir(paketler):
    # Paketleri seq_no'ya göre sırala
    parcalar = {}
    
    for paket in paketler:
        bilgi = paket_ac(paket)
        
        if not bilgi["butunluk_ok"]:
            print(f"HATA: Paket {bilgi['seq_no']} bozuk!")
            continue
        
        parcalar[bilgi["seq_no"]] = bilgi["veri"]
    
    # Sıralı birleştir
    icerik = b""
    for i in sorted(parcalar.keys()):
        icerik += parcalar[i]
    
    return icerik

# Test edelim
paketler = dosyayi_parcala("test.txt")

print()
print("--- Birleştirme ---")
orijinal = open("test.txt", "rb").read()
yeniden = parcalari_birlestir(paketler)

print(f"Orijinal boyut:     {len(orijinal)} byte")
print(f"Birleştirilen boyut: {len(yeniden)} byte")
print(f"Eşleşiyor mu: {orijinal == yeniden}")
print(f"İçerik: {yeniden.decode()}")