import socket
import struct
import hashlib
import math
import time
import os
import argparse

SUNUCU_IP = "localhost"
SUNUCU_PORT = 9999
PAKET_BOYUTU = 1024
TIMEOUT = 2.0
MAX_DENEME = 5

def paket_olustur(seq_no, toplam_paket, veri):
    tip = 1
    veri_uzunlugu = len(veri)
    checksum = hashlib.md5(veri).digest()
    header = struct.pack("!BIIH", tip, seq_no, toplam_paket, veri_uzunlugu)
    return header + checksum + veri

def meta_paketi_olustur(dosya_adi, dosya_boyutu, toplam_paket):
    tip = 3
    veri = f"{dosya_adi}|{dosya_boyutu}".encode("utf-8")
    veri_uzunlugu = len(veri)
    checksum = hashlib.md5(veri).digest()
    header = struct.pack("!BIIH", tip, 0, toplam_paket, veri_uzunlugu)
    return header + checksum + veri

def _ozet_yazdir(dosya, boyut, toplam, basarili, deneme, yeniden, sure, basarisiz):
    verimlilik = (basarili / deneme * 100) if deneme > 0 else 0
    throughput = (boyut / sure) if sure > 0 else 0

    print()
    print("=" * 45)
    print("       AKTARIM ÖZETİ")
    print("=" * 45)
    print(f"  Dosya              : {dosya}")
    print(f"  Dosya boyutu       : {boyut} byte ({boyut/1024:.1f} KB)")
    print(f"  Paket boyutu       : {PAKET_BOYUTU} byte")
    print(f"  Toplam paket       : {toplam}")
    print(f"  Başarılı paket     : {basarili}")
    print("-" * 45)
    print(f"  Toplam deneme      : {deneme}")
    print(f"  Yeniden gönderim   : {yeniden}")
    print(f"  Verimlilik         : %{verimlilik:.1f}")
    print("-" * 45)
    print(f"  Toplam süre        : {sure:.3f} saniye")
    print(f"  Throughput         : {throughput:.0f} byte/s ({throughput/1024:.1f} KB/s)")
    print("=" * 45)
    if basarisiz:
        print("  DURUM: ❌ AKTARIM TAMAMLANAMADI")
    else:
        print("  DURUM: ✅ AKTARIM BAŞARILI")
    print("=" * 45)

def dosya_gonder(dosya_yolu):
    toplam_deneme = 0
    yeniden_gonderim = 0
    basarisiz_paket = 0

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    with open(dosya_yolu, "rb") as f:
        icerik = f.read()

    dosya_adi = os.path.basename(dosya_yolu)
    dosya_boyutu = len(icerik)
    toplam_paket = math.ceil(dosya_boyutu / PAKET_BOYUTU)

    print(f"Gönderiliyor: {dosya_yolu}")
    print(f"Dosya boyutu: {dosya_boyutu} byte")
    print(f"Toplam paket: {toplam_paket}")
    print()

    # ── META PAKETİ GÖNDER ──────────────────────────────
    meta = meta_paketi_olustur(dosya_adi, dosya_boyutu, toplam_paket)
    meta_basarili = False

    for deneme in range(1, MAX_DENEME + 1):
        sock.sendto(meta, (SUNUCU_IP, SUNUCU_PORT))
        print(f"META gönderildi: '{dosya_adi}' (deneme {deneme})")
        try:
            ack_paketi, _ = sock.recvfrom(65535)
            tip = struct.unpack("!B", ack_paketi[:1])[0]
            if tip == 2:
                print(f"META ACK alındı ✓\n")
                meta_basarili = True
                break
        except socket.timeout:
            print(f"  META Timeout! Tekrar deneniyor...")

    if not meta_basarili:
        print("HATA: META paketi gönderilemedi, aktarım iptal!")
        sock.close()
        return
    # ────────────────────────────────────────────────────

    baslangic = time.time()

    for i in range(toplam_paket):
        veri = icerik[i * PAKET_BOYUTU:(i + 1) * PAKET_BOYUTU]
        paket = paket_olustur(seq_no=i, toplam_paket=toplam_paket, veri=veri)

        basarili = False

        for deneme in range(1, MAX_DENEME + 1):
            sock.sendto(paket, (SUNUCU_IP, SUNUCU_PORT))
            toplam_deneme += 1

            if deneme > 1:
                yeniden_gonderim += 1
                print(f"  [YENİDEN] Paket {i+1}/{toplam_paket} — deneme {deneme}/{MAX_DENEME}")
            else:
                print(f"Paket gönderildi: {i+1}/{toplam_paket} (deneme {deneme})")

            try:
                ack_paketi, _ = sock.recvfrom(65535)
                tip = struct.unpack("!B", ack_paketi[:1])[0]
                ack_seq = struct.unpack("!I", ack_paketi[1:5])[0]

                if tip == 2 and ack_seq == i:
                    print(f"  ACK alındı: seq={i}")
                    basarili = True
                    break
                else:
                    print(f"  Beklenmeyen ACK (tip={tip}, seq={ack_seq}), tekrar deneniyor...")

            except socket.timeout:
                print(f"  Timeout! Paket {i+1}/{toplam_paket} tekrar gönderiliyor...")

        if not basarili:
            basarisiz_paket += 1
            print(f"HATA: Paket {i+1} {MAX_DENEME} denemede gönderilemedi, aktarım durduruluyor!")
            sock.close()
            _ozet_yazdir(dosya_yolu, dosya_boyutu, toplam_paket,
                         toplam_paket - basarisiz_paket, toplam_deneme,
                         yeniden_gonderim, time.time() - baslangic, basarisiz=True)
            return

    sure = time.time() - baslangic
    sock.close()

    _ozet_yazdir(dosya_yolu, dosya_boyutu, toplam_paket,
                 toplam_paket, toplam_deneme,
                 yeniden_gonderim, sure, basarisiz=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NetProbe UDP Dosya Gönderici")
    parser.add_argument("--file", type=str, required=True, help="Gönderilecek dosya yolu")
    args = parser.parse_args()
    dosya_gonder(args.file)