"""
Firebase Firestore bağlantı yapılandırması.
Servis hesabı bilgileri .env ve serviceAccountKey.json üzerinden okunur.
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

def init_firebase():
    """
    Firebase Admin SDK'yı başlatır ve Firestore istemcisini döndürür.
    Uygulama zaten başlatılmışsa tekrar başlatmaz.
    """
    if not firebase_admin._apps:
        # Servis hesabı JSON dosyasının yolunu .env'den oku
        service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")

        if not os.path.exists(service_account_path):
            raise FileNotFoundError(
                f"Firebase servis hesabı dosyası bulunamadı: {service_account_path}\n"
                "Lütfen .env dosyasında FIREBASE_SERVICE_ACCOUNT_PATH değişkenini ayarlayın."
            )

        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)

    return firestore.client()


# Uygulama genelinde kullanılacak Firestore istemcisi
db = init_firebase()
