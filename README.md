Bu proje, elma yaprağı ve şeftali yaprağı sınıflarını ayırt edebilen bir derin öğrenme modelini içermektedir. Model, Google’ın Teachable Machine
 platformu kullanılarak eğitilmiştir.
<img width="1812" height="807" alt="Ekran görüntüsü 2025-10-02 154926" src="https://github.com/user-attachments/assets/dfd94f46-1c91-4f73-aa9a-75e7971a77a8" />

Veri Seti

Elma yaprağı: 260 örnek görüntü

Şeftali yaprağı: 324 örnek görüntü

Veriler hem kamera (webcam) hem de dosya yükleme (upload) yöntemleri ile sisteme eklenmiştir.

Eğitim Süreci

Görseller sınıflara ayrılarak modele tanıtıldı.

Teachable Machine otomatik olarak CNN tabanlı bir model eğitti.

Eğitim sonucunda, model yaprak görüntülerinden sınıf tahmini yapabilmektedir.

Görsel Açıklaması

Aşağıdaki görselde eğitim sürecinden bir ekran görüntüsü yer almaktadır:

Bu ekranda:

Elma yaprağı ve Şeftali yaprağı için kullanılan örnek veriler görülmektedir.

Eğitim tamamlandığında sistem “Model Trained” bilgisi vermektedir.

Sağ kısımda, modelin test aşamasında canlı kamera ya da görsel yükleme ile nasıl tahmin yaptığı görülebilir.

Çıktılar

Model, yeni bir yaprak görüntüsü verildiğinde çıktıyı şu şekilde üretir:

elma yaprağı

şeftali yaprağı

Kullanım

Model .tflite formatında dışa aktarılmıştır ve Flask tabanlı web uygulamasında kullanılabilir.

model.tflite → eğitilmiş model

labels.txt → sınıf etiketleri
