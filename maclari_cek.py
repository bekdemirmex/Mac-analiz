import requests
import json
from datetime import datetime

# 1. Tüm lig kodlarını ESPN'den al
def tum_ligleri_getir():
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer"
    response = requests.get(url, timeout=15)
    if response.status_code != 200:
        print("Lig listesi alınamadı!")
        return []
    
    data = response.json()
    ligler = []
    for sport in data.get("sports", []):
        for league in sport.get("leagues", []):
            slug = league.get("slug")
            if slug:
                ligler.append(slug)
    return ligler

# 2. Belirli bir lig için o günkü maçları çek
def lig_maclarini_getir(lig_kodu):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{lig_kodu}/scoreboard"
    maclar = []
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for event in data.get("events", []):
                comp = event["competitions"][0]
                mac = {
                    "lig": lig_kodu,
                    "takim1": comp["competitors"][0]["team"]["displayName"],
                    "takim2": comp["competitors"][1]["team"]["displayName"],
                    "skor1": comp["competitors"][0].get("score", "?"),
                    "skor2": comp["competitors"][1].get("score", "?"),
                    "durum": event["status"]["type"]["description"],
                    "canli_mi": event["status"]["type"]["state"] == "in",
                    "baslangic_saati": event.get("date", "")
                }
                maclar.append(mac)
    except Exception as e:
        print(f"Hata ({lig_kodu}): {e}")
    return maclar

# 3. Ana çalıştırıcı
def calistir():
    print(f"{datetime.now()} - Tüm ligler taranıyor...")
    ligler = tum_ligleri_getir()
    print(f"{len(ligler)} lig bulundu.")
    
    tum_maclar = []
    for lig in ligler:
        maclar = lig_maclarini_getir(lig)
        if maclar:
            tum_maclar.extend(maclar)
            print(f"{lig}: {len(maclar)} maç eklendi.")
    
    dosya_adi = f"maclar_{datetime.now().strftime('%Y%m%d')}.json"
    with open(dosya_adi, "w", encoding="utf-8") as f:
        json.dump(tum_maclar, f, indent=2, ensure_ascii=False)
    
    print(f"TOPLAM {len(tum_maclar)} maç '{dosya_adi}' dosyasına kaydedildi.")

if __name__ == "__main__":
    calistir()
