import struct
import hashlib

def paket_olustur(seq_no, toplam_paket, veri):
    tip = 1  # 1 = veri paketi
    veri_uzunlugu = len(veri)
    
    # Önce checksum hesapla (verinin MD5'i)
    checksum = hashlib.md5(veri).digest()  # 16 byte
    
    # Header'ı paketle
    header = struct.pack("!BIIH", tip, seq_no, toplam_paket, veri_uzunlugu)
    
    # Header + checksum + veri birleştir
    paket = header + checksum + veri
    
    return paket

def paket_ac(paket):
    # Header'ı ayır (ilk 27 byte)
    header_boyut = struct.calcsize("!BIIH") + 16  # 11 + 16 = 27
    header = paket[:11]
    checksum_gelen = paket[11:27]
    veri = paket[27:]
    
    # Header'ı aç
    tip, seq_no, toplam_paket, veri_uzunlugu = struct.unpack("!BIIH", header)
    
    # Checksum doğrula
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

# Test edelim
veri = b"Bu bir test verisidir."
paket = paket_olustur(seq_no=3, toplam_paket=10, veri=veri)

print(f"Paket boyutu: {len(paket)} byte")
print(f"Header: {len(paket) - len(veri)} byte")
print(f"Veri: {len(veri)} byte")
print()

# Paketi aç
sonuc = paket_ac(paket)
print(f"tip: {sonuc['tip']}")
print(f"seq_no: {sonuc['seq_no']}")
print(f"toplam_paket: {sonuc['toplam_paket']}")
print(f"veri: {sonuc['veri'].decode()}")
print(f"Bütünlük kontrolü: {sonuc['butunluk_ok']}")