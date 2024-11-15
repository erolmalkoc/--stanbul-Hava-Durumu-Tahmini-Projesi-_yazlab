import requests
import pandas as pd
from datetime import datetime, timedelta
import time

def get_hourly_weather(api_key, city_id="745044", hours=10000):
    """
    Belirtilen saat sayısı kadar saatlik hava durumu verilerini çeker
    """
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    weather_data = []
    
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=hours)
    
    print(f"\nSon {hours} saatin verileri çekiliyor...")
    print("İşlem başladı...")
    
    total_hours = hours
    current_hour = 0
    
    current_datetime = end_date
    while current_datetime >= start_date:
        params = {
            'id': city_id,
            'appid': api_key,
            'units': 'metric',
            'dt': int(current_datetime.timestamp())
        }
        
        try:
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                weather_data.append({
                    'tarih': current_datetime.strftime('%Y-%m-%d'),
                    'saat': current_datetime.strftime('%H:00'),
                    'sicaklik': round(data['list'][0]['main']['temp'], 1),
                    'hissedilen': round(data['list'][0]['main']['feels_like'], 1),
                    'nem_yuzdesi': data['list'][0]['main']['humidity'],
                    'basinc': data['list'][0]['main']['pressure'],
                    'ruzgar_hizi': round(data['list'][0]['wind']['speed'], 1),
                    'bulut_yuzdesi': data['list'][0]['clouds']['all']
                })
                
                current_hour += 1
                progress = (current_hour / total_hours) * 100
                print(f"\rİlerleme: %{progress:.1f} tamamlandı", end="")
                
                time.sleep(1)  # API limit kontrolü
                
        except Exception as e:
            print(f"\nHata: {e}")
        
        current_datetime -= timedelta(hours=1)
    
    print("\n✅ Veri çekme tamamlandı!")
    return pd.DataFrame(weather_data)

def save_to_excel(df, filename="saatlik_hava_durumu.xlsx"):
    """
    Verileri Excel'e kaydeder ve özet gösterir
    """
    try:
        # Tarih ve saate göre sırala
        df['datetime'] = pd.to_datetime(df['tarih'] + ' ' + df['saat'])
        df = df.sort_values(by='datetime')
        df = df.drop('datetime', axis=1)
        
        # Excel'e kaydet
        df.to_excel(filename, index=False)
        
        print(f"\n✅ Veriler {filename} dosyasına kaydedildi")
        print("\nÖzet Bilgiler:")
        print(f"Toplam saat sayısı: {len(df)}")
        print(f"Tarih aralığı: {df['tarih'].iloc[-1]} {df['saat'].iloc[-1]} - {df['tarih'].iloc[0]} {df['saat'].iloc[0]}")
        print(f"Maximum sıcaklık: {df['sicaklik'].max()}°C")
        print(f"Minimum sıcaklık: {df['sicaklik'].min()}°C")
        print(f"Ortalama sıcaklık: {df['sicaklik'].mean():.1f}°C")
        print(f"Ortalama nem: %{df['nem_yuzdesi'].mean():.1f}")
        print(f"Ortalama bulut oranı: %{df['bulut_yuzdesi'].mean():.1f}")
        
        return True
    except Exception as e:
        print(f"❌ Excel'e kaydetme hatası: {e}")
        return False

# API key ile veri çekme işlemi
API_KEY = "a73029070b2e60b905377a6d9d44f865"
CITY_ID = "745044"  # İstanbul

print("Hava durumu verileri çekiliyor...")
df = get_hourly_weather(API_KEY, CITY_ID)

if df is not None:
    save_to_excel(df)
    
    print("\nÖrnek veriler (ilk 5 kayıt):")
    print(df.head().to_string())
else:
    print("Veri çekme işlemi başarısız oldu!")