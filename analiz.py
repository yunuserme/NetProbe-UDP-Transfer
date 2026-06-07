import pandas as pd
import matplotlib.pyplot as plt
import glob
import sys

# En son oluşturulan log dosyasını otomatik bul
log_dosyalari = glob.glob("client_log_*.csv")
if not log_dosyalari:
    print("HATA: CSV log dosyası bulunamadı! Önce client.py'yi çalıştırıp veri üretin.")
    sys.exit()

en_yeni_log = max(log_dosyalari)
print(f"Analiz edilen dosya: {en_yeni_log}")

# Veriyi Pandas ile oku
df = pd.read_csv(en_yeni_log)

# Temel Metriklerin Hesaplanması
toplam_gonderim = len(df[df['event_type'] == 'SEND'])
basarili_ack = len(df[df['event_type'] == 'ACK'])
timeout_sayisi = len(df[df['event_type'] == 'TIMEOUT'])
retransmission_orani = ((toplam_gonderim - basarili_ack) / toplam_gonderim) * 100 if toplam_gonderim > 0 else 0

ortalama_rtt = df[df['event_type'] == 'ACK']['rtt_seconds'].mean()

print("\n" + "="*40)
print("       AĞ PERFORMANS ANALİZİ")
print("="*40)
print(f" Toplam Gönderim Denemesi : {toplam_gonderim}")
print(f" Başarılı İletilen Paket  : {basarili_ack}")
print(f" Yaşanan Timeout (Kayıp)  : {timeout_sayisi}")
print(f" Retransmission Oranı     : %{retransmission_orani:.2f}")
print(f" Ortalama RTT (Gecikme)   : {ortalama_rtt:.4f} saniye")
print("="*40 + "\n")

# ---------------------------------------------------------
# GRAFİK 1: Paket Numarasına Göre RTT (Gecikme)
# ---------------------------------------------------------
ack_df = df[df['event_type'] == 'ACK'].copy()
if not ack_df.empty:
    plt.figure(figsize=(10, 5))
    plt.plot(ack_df['seq_no'], ack_df['rtt_seconds'], marker='o', linestyle='-', color='b')
    plt.title("Paket Numarasına Göre RTT (Gecikme) Süreleri")
    plt.xlabel("Paket Sıra Numarası (Seq No)")
    plt.ylabel("RTT (Saniye)")
    plt.grid(True)
    plt.savefig("grafik_rtt.png") # Resmi klasöre kaydet
    print("[+] grafik_rtt.png kaydedildi.")

# ---------------------------------------------------------
# GRAFİK 2: Paket İletim Durumu (Pasta Grafiği)
# ---------------------------------------------------------
plt.figure(figsize=(6, 6))
olay_sayilari = [basarili_ack, timeout_sayisi]
olay_isimleri = ['Başarılı (ACK)', 'Kayıp / Timeout']
plt.pie(olay_sayilari, labels=olay_isimleri, autopct='%1.1f%%', colors=['#4CAF50', '#F44336'])
plt.title("Genel Paket İletim Durumu")
plt.savefig("grafik_durum.png") # Resmi klasöre kaydet
print("[+] grafik_durum.png kaydedildi.")

# Grafikleri ekranda göster
plt.show()