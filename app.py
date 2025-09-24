import os
import uuid
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

TF_VAR = False
try:
    import numpy as np
    from PIL import Image
    import tensorflow as tf
    TF_VAR = True
except Exception:
    import numpy as np
    from PIL import Image

TABAN = os.path.abspath(os.path.dirname(__file__))

uygulama = Flask(__name__, static_folder='static', template_folder='templates')
uygulama.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gizli-anahtar')
uygulama.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(TABAN, 'veri.db')}")
uygulama.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
uygulama.config['UPLOAD_FOLDER'] = os.path.join(TABAN, 'yuklemeler')
os.makedirs(uygulama.config['UPLOAD_FOLDER'], exist_ok=True)

vt = SQLAlchemy(uygulama)

class Kullanici(vt.Model):
    id = vt.Column(vt.Integer, primary_key=True)
    ad = vt.Column(vt.String(120), unique=True, nullable=False)
    en_iyi = vt.Column(vt.Float, default=0.0)
    olusma = vt.Column(vt.DateTime, default=datetime.datetime.utcnow)

class Soru(vt.Model):
    id = vt.Column(vt.Integer, primary_key=True)
    yazi = vt.Column(vt.String(500), nullable=False)
    konu = vt.Column(vt.String(120), nullable=False)
    secenekler = vt.relationship('Secenek', backref='soru', cascade="all, delete-orphan")

class Secenek(vt.Model):
    id = vt.Column(vt.Integer, primary_key=True)
    soru_id = vt.Column(vt.Integer, vt.ForeignKey('soru.id'), nullable=False)
    yazi = vt.Column(vt.String(300), nullable=False)
    dogru = vt.Column(vt.Boolean, default=False)

class Deneme(vt.Model):
    id = vt.Column(vt.Integer, primary_key=True)
    kullanici_id = vt.Column(vt.Integer, vt.ForeignKey('kullanici.id'), nullable=False)
    skor = vt.Column(vt.Float, nullable=False)
    toplam = vt.Column(vt.Integer, nullable=False)
    dogru_sayisi = vt.Column(vt.Integer, nullable=False)
    zaman = vt.Column(vt.DateTime, default=datetime.datetime.utcnow)
    kullanici = vt.relationship('Kullanici', backref='denemeler')

class GorselTahmin(vt.Model):
    id = vt.Column(vt.Integer, primary_key=True)
    kullanici_id = vt.Column(vt.Integer, vt.ForeignKey('kullanici.id'), nullable=True)
    dosya = vt.Column(vt.String(300), nullable=False)
    etiket = vt.Column(vt.String(200), nullable=False)
    guven = vt.Column(vt.Float, nullable=False)
    zaman = vt.Column(vt.DateTime, default=datetime.datetime.utcnow)
    kullanici = vt.relationship('Kullanici', backref='tahminler')

@uygulama.context_processor
def puanlar():
    genel = vt.session.query(vt.func.max(Kullanici.en_iyi)).scalar() or 0.0
    kisisel = 0.0
    ad = session.get('ad')
    if ad:
        k = Kullanici.query.filter_by(ad=ad).first()
        if k and k.en_iyi is not None:
            kisisel = k.en_iyi
    return dict(genel_en_yuksek=round(genel,2), kisisel_en_yuksek=round(kisisel,2))

class TMModel:
    def __init__(self):
        self.model = None
        self.etiketler = None
        self.boyut = (224, 224)
        self.hazir = False
        self.yukle()

    def yukle(self):
        m = os.path.join(TABAN, 'model', 'keras_model.h5')
        l = os.path.join(TABAN, 'model', 'labels.txt')
        if os.path.exists(m) and os.path.exists(l) and TF_VAR:
            try:
                self.model = tf.keras.models.load_model(m, compile=False)
                with open(l, 'r', encoding='utf-8') as f:
                    self.etiketler = [x.strip() for x in f if x.strip()]
                self.hazir = True
            except Exception as e:
                print('Model yuklenemedi:', e)

    def tahmin(self, pil):
        if self.hazir and TF_VAR:
            g = pil.convert("RGB").resize(self.boyut)
            d = np.asarray(g, dtype=np.float32)
            d = (d/127.5) - 1.0
            d = np.expand_dims(d, axis=0)
            c = self.model.predict(d)[0]
            i = int(np.argmax(c))
            et = self.etiketler[i] if self.etiketler and i < len(self.etiketler) else f"sinif_{i}"
            gv = float(c[i])
            return et, gv
        g = pil.convert("L").resize((64,64))
        ort = float(np.array(g).mean())/255.0
        et = "acik" if ort>=0.5 else "koyu"
        gv = round(abs(ort-0.5)*2, 3)
        return et, gv

tm = TMModel()

@uygulama.route('/')
def ana():
    return redirect(url_for('sinav'))

@uygulama.route('/quiz', methods=['GET'])
def sinav():
    sorular = Soru.query.all()
    if not sorular:
        tohum()
        sorular = Soru.query.all()
    return render_template('quiz.html', sorular=sorular)

@uygulama.route('/submit', methods=['POST'])
def gonder():
    ad = (request.form.get('ad') or '').strip()
    if not ad:
        flash("Ad gerekli.", "danger")
        return redirect(url_for('sinav'))
    session['ad'] = ad
    k = Kullanici.query.filter_by(ad=ad).first()
    if not k:
        k = Kullanici(ad=ad)
        vt.session.add(k)
        vt.session.commit()
    toplam = Soru.query.count()
    dogru_sayisi = 0
    for s in Soru.query.all():
        secim = request.form.get(f"s_{s.id}")
        if not secim:
            continue
        o = Secenek.query.filter_by(id=int(secim), soru_id=s.id).first()
        if o and o.dogru:
            dogru_sayisi += 1
    skor = (dogru_sayisi / max(toplam,1)) * 100.0
    d = Deneme(kullanici_id=k.id, skor=skor, toplam=toplam, dogru_sayisi=dogru_sayisi)
    vt.session.add(d)
    if skor > (k.en_iyi or 0.0):
        k.en_iyi = skor
    vt.session.commit()
    return redirect(url_for('sonuc', deneme_id=d.id))

@uygulama.route('/results/<int:deneme_id>')
def sonuc(deneme_id):
    d = Deneme.query.get_or_404(deneme_id)
    son = round(d.skor,2)
    kisisel = round(d.kullanici.en_iyi or 0.0, 2)
    genel = round(vt.session.query(vt.func.max(Kullanici.en_iyi)).scalar() or 0.0, 2)
    return render_template('results.html', son=son, kisisel=kisisel, genel=genel, dogru=d.dogru_sayisi, toplam=d.toplam)

@uygulama.route('/history')
def gecmis():
    ad = session.get('ad')
    denemeler = []
    if ad:
        k = Kullanici.query.filter_by(ad=ad).first()
        if k:
            denemeler = Deneme.query.filter_by(kullanici_id=k.id).order_by(Deneme.zaman.desc()).all()
    return render_template('history.html', denemeler=denemeler)

@uygulama.route('/image', methods=['GET','POST'])
def gorsel():
    tahmin = None
    yol = None
    if request.method == 'POST':
        if 'gorsel' not in request.files:
            flash("Görsel seçiniz.", "warning")
            return redirect(url_for('gorsel'))
        f = request.files['gorsel']
        if f.filename == '':
            flash("Dosya yok.", "warning")
            return redirect(url_for('gorsel'))
        ad = secure_filename(f"{uuid.uuid4().hex}_{f.filename}")
        tam = os.path.join(uygulama.config['UPLOAD_FOLDER'], ad)
        f.save(tam)
        pil = Image.open(tam)
        et, gv = tm.tahmin(pil)
        k = None
        if session.get('ad'):
            k = Kullanici.query.filter_by(ad=session['ad']).first()
        kayit = GorselTahmin(kullanici_id=k.id if k else None, dosya=ad, etiket=et, guven=float(gv))
        vt.session.add(kayit)
        vt.session.commit()
        yol = url_for('yuklenen', isim=ad)
        tahmin = {'etiket': et, 'guven': float(gv)}
        flash("Görsel algılama tamamlandı.", "success")
    hazir = tm.hazir
    return render_template('image.html', tahmin=tahmin, yol=yol, hazir=hazir)

@uygulama.route('/uploads/<path:isim>')
def yuklenen(isim):
    return send_from_directory(uygulama.config['UPLOAD_FOLDER'], isim)

@uygulama.route('/about')
def hakkinda():
    return render_template('about.html')

def tohum():
    if Soru.query.count()>0:
        return
    veri = [
        {"yazi":"Discord.py ile bir botta mesajları dinlemek için hangi olay kullanılır?","konu":"Discord.py","sec": [("on_message",True),("on_text",False),("on_send",False),("message_event",False)]},
        {"yazi":"Flask uygulamasında rotalar hangi dekoratör ile tanımlanır?","konu":"Flask","sec": [("@app.route",True),("@flask.path",False),("@app.endpoint",False),("@route.app",False)]},
        {"yazi":"Yapay zekâ eğitiminde aşırı öğrenmeyi azaltmak için hangisi etkilidir?","konu":"Yapay Zekâ","sec":[("Dropout",True),("Veriyi azaltmak",False),("Rastgele etiketlemek",False),("Oranı sınırsız artırmak",False)]},
        {"yazi":"Computer Vision'da çok sınıflı sınıflandırmada çıkış aktivasyonu genelde hangisidir?","konu":"Computer Vision","sec":[("Softmax",True),("ReLU",False),("Tanh",False),("Sigmoid",False)]},
        {"yazi":"NLTK ne için kullanılır?","konu":"NLP / NLTK","sec":[("Doğal Dil İşleme",True),("3D Oyun",False),("Sürücü yazmak",False),("Veritabanı çekirdeği",False)]},
        {"yazi":"BeautifulSoup genellikle hangi amaçla kullanılır?","konu":"BeautifulSoup","sec":[("HTML ayrıştırma ve web kazıma",True),("GPU hızlandırma",False),("Ses sentezi",False),("JSON şeması",False)]},
    ]
    for k in veri:
        s = Soru(yazi=k["yazi"], konu=k["konu"])
        vt.session.add(s)
        vt.session.flush()
        for y, d in k["sec"]:
            vt.session.add(Secenek(soru_id=s.id, yazi=y, dogru=d))
    vt.session.commit()

@uygulama.cli.command('veritabani')
def veritabani():
    vt.create_all()
    tohum()
    print("Hazır.")

if __name__ == "__main__":
    with uygulama.app_context():
        vt.create_all()
        tohum()
    uygulama.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
