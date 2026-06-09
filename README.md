# Yelp Restoran Yorumlarından Metin Madenciliği ile Kalite Tahmini 
*(Quality Prediction Using Text Mining on Yelp Restaurant Reviews)*

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5+-yellow.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.20+-orange.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.3+-red.svg)
![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-yellow.svg)
![Flask](https://img.shields.io/badge/Flask-Web_App-black.svg)

Bu proje, Yelp Açık Veri Seti'ndeki (Yelp Open Dataset) restoran yorumlarını kullanarak müşteri deneyimlerinin kalitesini tahmin etmeyi amaçlayan kapsamlı bir metin madenciliği (text mining) ve doğal dil işleme (NLP) boru hattıdır. Proje, veri hazırlama, keşifsel veri analizi (EDA), metin ön işleme, öznitelik çıkarımı, model eğitimi, model değerlendirme, yön-bazlı duygu analizi (ABSA), açıklanabilir yapay zeka (LIME) ve etkileşimli bir Flask web uygulamasını içermektedir.

Temel tahmin görevi, yorumların kalite/duygu açısından 3 sınıfa ayrılmasıdır:
- `0` Kötü (Poor / Bad) - 1 ve 2 Yıldız
- `1` Orta (Average / Neutral) - 3 Yıldız
- `2` İyi (Good) - 4 ve 5 Yıldız

## Proje Kapsamı ve Öne Çıkan Özellikler

- **Veri Sızıntısını Önleyen Tasarım (Data Leakage Prevention):** Eğitim, doğrulama ve test ayrımı, TF-IDF, tokenizer ve ölçekleyiciler uygulanmadan önce yapılmış; böylece test seti hiçbir şekilde eğitim aşamasına sızmamıştır.
- **Dengeli Veri Seti:** Azınlık sınıflarına göre (Orta sınıfı) alt-örnekleme yapılarak her sınıftan 543.093 örnek olacak şekilde toplam ~1.62 milyon yorumla dengeli bir veri seti oluşturulmuştur.
- **Kapsamlı Klasik ve Derin Öğrenme Modelleri:** Lojistik Regresyon, Destek Vektör Makineleri (SVM), SGD, LightGBM gibi klasik modeller ile TextCNN, FastText, LSTM, BiLSTM, CNN-LSTM gibi derin öğrenme mimarileri kıyaslanmıştır.
- **DistilBERT Entegrasyonu:** Orijinal eğitim bölütü üzerinde `distilbert-base-uncased` modeli kullanılarak Transformer tabanlı ince ayar (fine-tuning) yapılmıştır.
- **LIME ile Açıklanabilir Yapay Zeka (XAI):** Modellerin tahmin kararlarının hangi kelimelere ve köklere bağlı olduğu kelime ağırlıklarıyla görselleştirilmiştir.
- **Yön-Bazlı Duygu Analizi (ABSA):** Yorumlar cümle bazlı ayrıştırılıp *Yemek, Servis, Ambiyans* ve *Fiyat* gibi spesifik boyutlarda değerlendirilmiştir.
- **Gelişmiş Web Uygulaması:** Eğitilen tüm modellerin entegre edildiği etkileşimli bir arayüz geliştirilmiştir.

## Web Uygulaması Gelişmiş Modülleri

Flask tabanlı web uygulaması (`app/app.py`), temel çıkarım işlemlerine ek olarak yenilikçi analiz katmanları içermektedir:
1. **Alaycılık (Sarcasm) Tespiti:** Kural tabanlı stratejilerle (örneğin olumlu sıfatların ünlemle birlikte olumsuz bir bağlamda kullanılması) alaycı yorumları tespit edip kullanıcıyı uyarır.
2. **Metin Kod Çözümü (Text Decoder):** Emojileri ve internet argosunu (örn. tbh, ngl) NLP dostu kelimelere çevirerek modele besler.
3. **Yorumcu Profilleme (Reviewer Profiler):** Kullanıcıların "faydalı" (useful) oy sayılarını inceleyerek, çok düşük oylu ancak aşırı uçlarda yorum yapan hesaplar için spam/sahte yorum riski uyarısı verir.
4. **Olumsuzluk İşleme (Negation Handling):** Ön işleme sırasında "not bad" ifadesini "good" olarak, "not expensive" ifadesini "cheap" olarak dönüştüren özel bir modül kullanır.

## Deneysel Sonuçlar

Modeller aynı resmi test indeksleri üzerinde değerlendirilmiştir. Klasik modeller arasında en iyi sonucu Lojistik Regresyon vermiştir:

| Model | Doğruluk (Accuracy) | Kesinlik (Precision) | Duyarlılık (Recall) | F1-Makro Skoru |
|-------|--------------------|----------------------|---------------------|----------------|
| **Lojistik Regresyon** | **%80,41** | **%80,39** | **%80,41** | **%80,40** |
| **SVM** | %80,12 | %79,96 | %80,12 | %80,02 |
| **TextCNN** | %76,24 | %76,27 | %76,24 | %76,24 |
| **FastText** | %75,82 | %75,82 | %75,82 | %75,76 |
| **SGD** | %75,52 | %75,23 | %75,52 | %75,30 |

*Not: DistilBERT gibi Transformer mimarileri ve diğer derin öğrenme sonuçları ilgili rapor/notebook'larda mevcuttur.*

## Repozitörü ve Notebook Boru Hattı (Pipeline)

Sistemi baştan uca çalıştırmak ve çıktıları yeniden üretmek için notebook'ları aşağıdaki sırayla çalıştırınız:

1. `01_data_preparation.ipynb`: Yelp veri setinden restoranları süzer, 3 sınıfa eşleştirir ve veriyi dengeler.
2. `02_eda.ipynb`: Kelime bulutları, yorum uzunluğu trendleri, N-gram ve sosyal metrik analizlerini (Kruskal-Wallis, Spearman) gerçekleştirir.
3. `03_text_preprocessing.ipynb`: Metin temizliği, emoji çıkarımı (Eğitim seti için), stopword temizliği (olumsuzluklar korunarak) ve TextBlob üzerinden ek öznitelik çıkarımı yapar.
4. `04_feature_extraction.ipynb`: Eğitim, doğrulama, test ayrımını yapar. Sadece eğitim verisi üzerinde TF-IDF ve Tokenizer'ı *fit* eder.
5. `05_model_training.ipynb`: Klasik makine öğrenmesi ve sinir ağları modellerini eğitir ve `models/` altına kaydeder.
6. `06_model_evaluation.ipynb`: Modelleri test seti üzerinde değerlendirir; ROC/PR eğrileri, karışıklık matrisleri ve hata analizi çıktılarını üretir.
7. `07_aspect_based_sentiment.ipynb`: ABSA kural setlerini çalıştırarak duygu yönlerini (Yemek, Servis vs.) belirler.
8. `08_bert_model.ipynb`: `distilbert-base-uncased` modelini PyTorch ile ince ayardan geçirerek değerlendirir.

## Kurulum ve Çalıştırma

**1. Gerekli kütüphaneleri yükleyin:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
*(Proje Python 3.13 ile geliştirilmiştir. Derin öğrenme paketleri için donanımınıza uygun tekerlekleri (wheels) veya Python 3.11/3.12 kullanabilirsiniz.)*

**2. Web Uygulamasını Başlatma:**
Tüm modeller eğitildikten veya `models/` klasörüne ilgili dosyalar (örn: `pytorch_model.bin`, `tfidf_vectorizer.pkl`) koyulduktan sonra:
```bash
cd app
python app.py
```
Uygulamaya tarayıcınızdan `http://127.0.0.1:5000` adresinden erişebilirsiniz. Arayüzde tekil tahmin, toplu CSV tahmini, EDA panoları ve model karşılaştırma ekranları yer alır.

## Dosya ve Klasör Yapısı

* **`app/`**: Flask web uygulaması, şablonlar (HTML/CSS), kod çözücü (decoder), alaycılık tespiti (sarcasm) modülleri.
* **`report/`**: LaTeX formatında hazırlanmış, figürlerle desteklenmiş kapsamlı akademik rapor (`main.tex`).
* **`data/`, `features/`, `models/`, `results/`, `bert_results/`**: Model ağırlıkları, indeksler, ön işlenmiş veri dosyaları ve sonuç çıktıları (Boyutlarından ötürü repoya dahil edilmemiştir, notebook'larla baştan üretilmelidir).
* **`Yelp JSON/`**: Yelp orijinal verisinin atılması gereken klasör dizini.
