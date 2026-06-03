import socket
import struct
import hashlib
import os
import random
import time
import argparse

KAYIP_OLASILIGI = 0.3
PORT = 9999
HEDEF_KLASOR = "alinan_dosyalar"

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

def sunucu_ozet_yazdir(dosya_adi, dosya_boyutu, toplam_alinan, toplam_duplicate, toplam_bozuk, toplam_dusurlen, sure):
    throughput = (dosya_boyutu / sure) if sure > 0 else 0
    toplam_gelen = toplam_alinan + toplam_duplicate + toplam_bozuk + toplam_dusurlen

    ozet = f"""
=============================================
       SUNUCU ALIM ÖZETİ
=============================================
  Dosya              : {dosya_adi}
  Dosya boyutu       : {dosya_boyutu} byte ({dosya_boyutu/1024:.1f} KB)
---------------------------------------------
  Toplam gelen paket : {toplam_gelen}
  Başarılı alınan    : {toplam_alinan}
  Duplicate          : {toplam_duplicate}
  Bozuk              : {toplam_bozuk}
  Simülasyonla düşen : {toplam_dusurlen}
---------------------------------------------
  Toplam süre        : {sure:.3f} saniye
  Throughput         : {throughput:.0f} byte/s ({throughput/1024:.1f} KB/s)
=============================================
"""
    print(ozet)

    with open("server_log.txt", "a", encoding="utf-8") as log:
        log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]\n")
        log.write(ozet)
        log.write("\n")

def ack_gonder(sock, seq_no, adres):
    ack = struct.pack("!BIIH", 2, seq_no, 0, 0) + b'\x00' * 16
    sock.sendto(ack, adres)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NetProbe UDP Sunucu")
    parser.add_argument("--loss", type=float, default=0.3, help="Paket kayıp oranı (0.0 - 1.0, varsayılan: 0.3)")
    args = parser.parse_args()
    KAYIP_OLASILIGI = args.loss

    os.makedirs(HEDEF_KLASOR, exist_ok=True)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("localhost", PORT))
    print(f"Sunucu başladı, port {PORT} dinleniyor... (kayıp oranı: %{KAYIP_OLASILIGI*100:.0f})")

toplam_alinan = 0
toplam_duplicate = 0
toplam_bozuk = 0
toplam_dusurlen = 0
baslangic = None
dosya_boyutu = 0

parcalar = {}
toplam_paket = None
hedef_dosya_adi = "alinan_dosya.txt"

while True:
    paket, adres = sock.recvfrom(65535)
    bilgi = paket_ac(paket)

    if not bilgi["butunluk_ok"]:
         toplam_bozuk += 1
         print(f"HATA: Paket {bilgi['seq_no']} bozuk, atlanıyor!")
         continue

    # ── META PAKETİ ─────────────────────────────────────
    if bilgi["tip"] == 3:
        meta_veri = bilgi["veri"].decode("utf-8")
        dosya_adi, dosya_boyutu = meta_veri.split("|")
        hedef_dosya_adi = dosya_adi
        print(f"META alındı: '{dosya_adi}', {dosya_boyutu} byte")
        ack_gonder(sock, 0, adres)
        print(f"META ACK gönderildi ✓\n")
        continue
    # ────────────────────────────────────────────────────

    # Yapay paket kaybı simülasyonu
    if random.random() < KAYIP_OLASILIGI:
        toplam_dusurlen += 1
        print(f"[SİMÜLASYON] Paket {bilgi['seq_no']} düşürüldü!")
        continue

    seq_no = bilgi["seq_no"]
    toplam_paket = bilgi["toplam_paket"]

    if seq_no in parcalar:
        toplam_duplicate += 1
        print(f"Duplicate paket {seq_no}, ACK tekrar gönderiliyor")
        ack_gonder(sock, seq_no, adres)
        continue

    if baslangic is None:
        baslangic = time.time()
    toplam_alinan += 1
    parcalar[seq_no] = bilgi["veri"]
    ack_gonder(sock, seq_no, adres)
    print(f"Paket alındı ve ACK gönderildi: {seq_no + 1}/{toplam_paket}")

    if len(parcalar) == toplam_paket:
        sure = time.time() - baslangic
        print("\nTüm paketler alındı! Dosya birleştiriliyor...")
        icerik = b""
        for i in sorted(parcalar.keys()):
            icerik += parcalar[i]
        kayit_yolu = os.path.join(HEDEF_KLASOR, hedef_dosya_adi)
        with open(kayit_yolu, "wb") as f:
            f.write(icerik)
        print(f"Dosya kaydedildi: {kayit_yolu}")
        sunucu_ozet_yazdir(hedef_dosya_adi, len(icerik), toplam_alinan,
                        toplam_duplicate, toplam_bozuk, toplam_dusurlen, sure)
        # Sayaçları sıfırla (sonraki aktarım için)
        parcalar = {}
        hedef_dosya_adi = "alinan_dosya.txt"
        toplam_alinan = 0
        toplam_duplicate = 0
        toplam_bozuk = 0
        toplam_dusurlen = 0
        baslangic = None
        dosya_boyutu = 0