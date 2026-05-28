import os
import sys
import subprocess
import shutil

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("🚀 StokYönet - Otomatik Kurulum")
    print("================================")
    
    # Adım 2: Bağımlılıkları kur
    print("\n📦 Paketler kuruluyor...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("❌ HATA: Paketler kurulurken bir sorun oluştu.")
        print("Lütfen requirements.txt dosyasının var olduğundan emin olun.")
        sys.exit(1)
        
    # Adım 3 & 4: Firebase JSON dosyasını al ve kopyala
    print("\nFirebase servis hesabı JSON dosyasının tam yolunu girin:")
    print("(Örnek: /Users/kullanici/Downloads/serviceAccountKey.json)")
    json_path = input("Dosya yolu: ").strip()
    
    # Tirnak icinde verilirse temizle
    if json_path.startswith('"') and json_path.endswith('"'):
        json_path = json_path[1:-1]
    if json_path.startswith("'") and json_path.endswith("'"):
        json_path = json_path[1:-1]
        
    if not os.path.isfile(json_path):
        print(f"❌ HATA: Belirtilen yolda dosya bulunamadı: {json_path}")
        sys.exit(1)
        
    try:
        shutil.copy(json_path, "serviceAccountKey.json")
        print("✅ serviceAccountKey.json başarıyla proje dizinine kopyalandı.")
    except Exception as e:
        print(f"❌ HATA: Dosya kopyalanırken hata oluştu: {e}")
        sys.exit(1)

    # Adım 5: .env dosyasını oluştur
    env_content = """SECRET_KEY=stokyonet-demo-key-2026
FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json
"""
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ .env dosyası oluşturuldu.")
    except Exception as e:
        print(f"❌ HATA: .env dosyası oluşturulurken hata: {e}")
        sys.exit(1)

    # Adım 6: Firebase bağlantısını test et
    print("\n🔄 Firebase bağlantısı test ediliyor...")
    try:
        from firebase_config import test_connection
        if test_connection():
            print("✅ Firebase bağlantısı başarılı!")
        else:
            print("❌ HATA: Firebase bağlantısı başarısız oldu. Lütfen serviceAccountKey.json dosyanızı kontrol edin.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ HATA: Bağlantı testi sırasında bir hata oluştu: {e}")
        sys.exit(1)

    # Adım 7: Demo verileri yükle
    print("\n🌱 Demo verileri yükleniyor...")
    try:
        if os.path.exists("seed_data.py"):
            subprocess.check_call([sys.executable, "seed_data.py"])
            print("✅ Demo verileri başarıyla yüklendi.")
        else:
            print("⚠️ seed_data.py bulunamadı, demo verileri atlanıyor.")
    except subprocess.CalledProcessError:
        print("❌ HATA: Demo verileri yüklenirken bir sorun oluştu.")
        sys.exit(1)

    # Adım 8: Bitiş mesajı
    print("\n================================")
    print("✅ Kurulum tamamlandı!")
    print("")
    print("Uygulamayı başlatmak için:")
    print("  python app.py")
    print("")
    print("Tarayıcıda açın:")
    print("  http://localhost:5001")
    print("")
    print("Giriş bilgileri:")
    print("  Kullanıcı adı: admin")
    print("  Şifre: Admin123!")
    print("================================")

if __name__ == "__main__":
    main()
