Flask Quiz & Yaprak Sınıflandırma Projesi

Bu repo iki ana çalışmayı içermektedir:

🎯 Flask Quiz Uygulaması

🌿 Elma & Şeftali Yaprakları Sınıflandırma Modeli

1. 🎯 Flask Quiz Uygulaması

Bu uygulama, Flask framework ile hazırlanmış basit bir quiz sistemidir.

Kullanıcıya sorular sorulur.

Cevaplara göre doğru/yanlış geri bildirimi verilir.

Sonuçlar ekranda görüntülenir.

📂 Dosyalar

app.py → Flask uygulaması

templates/ → HTML şablonları

requirements.txt → Gerekli bağımlılıklar

🚀 Çalıştırmak için
pip install -r requirements.txt
python app.py


Tarayıcıda şu adresten uygulamaya erişebilirsin:
👉 http://127.0.0.1:5000/

2. 🌿 Yaprak Sınıflandırma Modeli

Bu model, elma yaprağı ve şeftali yaprağı sınıflarını ayırt edebilmektedir.
Google’ın Teachable Machine
 platformu kullanılarak eğitilmiştir.

<img width="1812" height="807" alt="Ekran görüntüsü 2025-10-02 154926" src="https://github.com/user-attachments/assets/dfd94f46-1c91-4f73-aa9a-75e7971a77a8" />
📊 Veri Seti

Elma yaprağı: 260 görüntü

Şeftali yaprağı: 324 görüntü

🧠 Eğitim Süreci

Görseller sınıflara ayrıldı.

CNN tabanlı model Teachable Machine üzerinde otomatik olarak eğitildi.

Eğitim sonrası model, yüklenen yaprak görüntülerini elma veya şeftali olarak tahmin edebilmektedir.

📦 Çıktılar

model/model.tflite → Eğitilmiş model dosyası

model/labels.txt → Sınıf etiketleri

model/README.txt → Model hakkında kısa bilgi

🔗 Entegrasyon

Bu repo sayesinde hem quiz tabanlı eğitim uygulaması hem de görüntü tabanlı yaprak sınıflandırma modeli aynı projede bir araya getirilmiştir.

Quiz kısmı → Teorik bilgi ölçümü

Yaprak sınıflandırma kısmı → Pratik uygulama (AI ile sınıflandırma)

📌 Özet

Flask tabanlı quiz uygulaması ile kullanıcıya interaktif bir öğrenme ortamı sunulur.

Teachable Machine ile eğitilmiş CNN modeli sayesinde yaprak sınıflandırması yapılır.

Proje, hem eğitim hem de tarımsal yapay zeka uygulamaları için temel bir örnek teşkil etmektedir.
