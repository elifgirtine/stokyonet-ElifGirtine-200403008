"""
Firebase Firestore bağlantı yapılandırması.
Servis hesabı bilgileri .env ve serviceAccountKey.json üzerinden okunur.
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Projenin kök dizinini bul ve .env dosyasını mutlak yol ile yükle
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)


def init_firebase():
    """
    Firebase Admin SDK'yı başlatır ve Firestore istemcisini döndürür.
    Uygulama zaten başlatılmışsa tekrar başlatmaz (idempotent).

    Returns:
        google.cloud.firestore.Client: Firestore veritabanı istemcisi.

    Raises:
        RuntimeError: Servis hesabı dosyası bulunamazsa veya SDK başlatılamazsa.
    """
    try:
        if not firebase_admin._apps:
            # Servis hesabı JSON dosyasının yolunu .env'den oku
            service_account_path = (
                os.getenv("FIREBASE_CREDENTIALS_PATH")
                or os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
                or "serviceAccountKey.json"
            )

            # Göreceli yolları proje kök dizinine göre mutlak yola çevir
            if not os.path.isabs(service_account_path):
                service_account_path = os.path.join(base_dir, service_account_path)

            if not os.path.exists(service_account_path):
                raise FileNotFoundError(
                    f"Firebase servis hesabı dosyası bulunamadı: {service_account_path}\n"
                    "Lütfen .env dosyasında FIREBASE_CREDENTIALS_PATH veya "
                    "FIREBASE_SERVICE_ACCOUNT_PATH değişkenini ayarlayın."
                )

            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)

        return firestore.client()
    except Exception as e:
        # Teknik detayı loglamadan anlamlı Türkçe hata mesajıyla fırlat
        raise RuntimeError(
            f"Firebase bağlantısı kurulurken bir hata oluştu: {str(e)}"
        ) from e


# Modül genelinde tek bir Firestore istemcisi tutan değişken
_db = None


def get_db():
    """
    Uygulama genelinde kullanılacak Firestore istemcisini döndürür.
    İlk çağrıda Firebase'i başlatır; sonraki çağrılarda önbelleği kullanır.

    Returns:
        google.cloud.firestore.Client: Firestore veritabanı istemcisi.
    """
    global _db
    if _db is None:
        _db = init_firebase()
    return _db
