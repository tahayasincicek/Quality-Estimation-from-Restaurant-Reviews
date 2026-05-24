import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.image as mpimg

def main():
    print("=== EDA Başlıyor ===")
    os.makedirs("results", exist_ok=True)
    
    print("Veri yükleniyor (data/reviews_cleaned.csv)...")
    try:
        df = pd.read_csv("data/reviews_cleaned.csv")
    except Exception as e:
        print(f"HATA: Veri okunamadı. {str(e)}")
        return
        
    print("Özellikler hesaplanıyor...")
    df['text'] = df['text'].astype(str)
    df['review_length'] = df['text'].str.len()
    df['word_count'] = df['text'].apply(lambda x: len(x.split()))
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    
    class_names = {0: 'Kötü', 1: 'Orta', 2: 'İyi'}
    df['class_name'] = df['label'].map(class_names)
    
    # Grafik ayarları
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({'figure.figsize': (12, 8), 'figure.dpi': 150})
    
    # BÖLÜM 1
    print("\nBÖLÜM 1: Genel Dağılım Grafikleri Çiziliyor...")
    
    # 1. Class distribution
    plt.figure()
    sns.countplot(data=df, x='class_name', order=['Kötü', 'Orta', 'İyi'], palette='Set2', hue='class_name', legend=False)
    plt.title('Sınıf Dağılımı')
    plt.xlabel('Sınıf')
    plt.ylabel('Yorum Sayısı')
    plt.tight_layout()
    plt.savefig('results/eda_class_distribution.png')
    plt.close()
    print("[OK] Kaydedildi: results/eda_class_distribution.png")
    
    # 2. Star distribution
    plt.figure()
    sns.countplot(data=df, x='stars', palette='viridis', hue='stars', legend=False)
    plt.title('Yıldız Dağılımı (Orijinal)')
    plt.xlabel('Yıldız Puanı')
    plt.ylabel('Yorum Sayısı')
    plt.tight_layout()
    plt.savefig('results/eda_star_distribution.png')
    plt.close()
    print("[OK] Kaydedildi: results/eda_star_distribution.png")
    
    # 3. Review length distribution (overlapping)
    plt.figure()
    sns.histplot(data=df, x='review_length', hue='class_name', bins=50, kde=True, palette='Set2', alpha=0.5)
    plt.xlim(0, 3000) # Aykırı değerleri kesmek ve daha iyi görünüm için
    plt.title('Yorum Uzunluğu Dağılımı (Karakter)')
    plt.xlabel('Karakter Sayısı')
    plt.ylabel('Frekans')
    plt.tight_layout()
    plt.savefig('results/eda_review_length.png')
    plt.close()
    print("[OK] Kaydedildi: results/eda_review_length.png")
    
    # 4. Word count box plot
    plt.figure()
    sns.boxplot(data=df, x='class_name', y='word_count', palette='Set2', showfliers=False, hue='class_name', legend=False)
    plt.title('Sınıflara Göre Kelime Sayısı Dağılımı (Aykırı Değerler Hariç)')
    plt.xlabel('Sınıf')
    plt.ylabel('Kelime Sayısı')
    plt.tight_layout()
    plt.savefig('results/eda_word_count.png')
    plt.close()
    print("[OK] Kaydedildi: results/eda_word_count.png")
    
    # BÖLÜM 2 - Metin Analizi
    print("\nBÖLÜM 2: Metin Analizi Başlıyor...")
    print("(Not: Büyük veri setlerinde bellek ve zaman sorunu olmaması için 100.000 örneklik rastgele alt küme kullanılıyor)")
    sample_size = min(100000, len(df))
    df_sample = df.sample(n=sample_size, random_state=42)
    
    stopwords = set(STOPWORDS)
    stopwords.update(['food', 'place', 'good', 'great', 'restaurant', 'one', 'go', 'will', 'time', 'really', 'back', 'just', 'like', 'even'])
    
    # 5. WordCloud
    for label, name in class_names.items():
        text_data = " ".join(df_sample[df_sample['label'] == label]['text'].tolist())
        
        wc = WordCloud(width=800, height=400, background_color='white', stopwords=stopwords, max_words=150)
        wc.generate(text_data)
        
        plt.figure()
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'WordCloud - {name}', fontsize=20)
        plt.tight_layout()
        
        file_name = f'eda_wordcloud_{name.lower().replace("ö", "o").replace("i̇", "i").replace("ı", "i")}.png'
        path = os.path.join('results', file_name)
        plt.savefig(path)
        plt.close()
        print(f"[OK] Kaydedildi: {path}")
        
    # 6. Top 20 words
    plt.figure(figsize=(18, 6))
    for i, (label, name) in enumerate(class_names.items(), 1):
        plt.subplot(1, 3, i)
        vectorizer = CountVectorizer(stop_words='english', max_features=20)
        text_list = df_sample[df_sample['label'] == label]['text']
        
        try:
            word_counts = vectorizer.fit_transform(text_list).sum(axis=0)
            words_freq = [(word, word_counts[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
            words_freq = sorted(words_freq, key=lambda x: x[1], reverse=False)
            
            words = [w[0] for w in words_freq]
            counts = [w[1] for w in words_freq]
            
            plt.barh(words, counts, color=sns.color_palette("Set2")[i-1])
            plt.title(f'En Sık 20 Kelime - {name}')
            plt.xlabel('Frekans')
        except ValueError:
            plt.title(f'Yeterli kelime yok - {name}')
    plt.tight_layout()
    plt.savefig('results/eda_top_words.png')
    plt.close()
    print("[OK] Kaydedildi: results/eda_top_words.png")
    
    # 7. Bigrams
    plt.figure(figsize=(18, 6))
    for i, (label, name) in enumerate(class_names.items(), 1):
        plt.subplot(1, 3, i)
        vectorizer = CountVectorizer(stop_words='english', ngram_range=(2, 2), max_features=10)
        text_list = df_sample[df_sample['label'] == label]['text']
        
        try:
            word_counts = vectorizer.fit_transform(text_list).sum(axis=0)
            words_freq = [(word, word_counts[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
            words_freq = sorted(words_freq, key=lambda x: x[1], reverse=False)
            
            words = [w[0] for w in words_freq]
            counts = [w[1] for w in words_freq]
            
            plt.barh(words, counts, color=sns.color_palette("Set2")[i-1])
            plt.title(f'En Sık 10 Bigram - {name}')
            plt.xlabel('Frekans')
        except ValueError:
            plt.title(f'Yeterli bigram yok - {name}')
    plt.tight_layout()
    plt.savefig('results/eda_bigrams.png')
    plt.close()
    print("[OK] Kaydedildi: results/eda_bigrams.png")
    
    # BÖLÜM 3 - Statistical Analysis
    print("\nBÖLÜM 3: İstatistiksel Analiz Çiziliyor...")
    
    # 8. Social features
    plt.figure()
    social_cols = ['useful', 'funny', 'cool']
    df_social = df.groupby('class_name')[social_cols].mean().reset_index()
    df_social_melted = df_social.melt(id_vars='class_name', var_name='Etkileşim Türü', value_name='Ortalama Skor')
    
    sns.barplot(data=df_social_melted, x='class_name', y='Ortalama Skor', hue='Etkileşim Türü', palette='Set1', order=['Kötü', 'Orta', 'İyi'])
    plt.title('Sınıflara Göre Ortalama Useful, Funny, Cool Puanları')
    plt.xlabel('Sınıf')
    plt.ylabel('Ortalama Skor')
    plt.tight_layout()
    plt.savefig('results/eda_social_features.png')
    plt.close()
    print("[OK] Kaydedildi: results/eda_social_features.png")
    
    # 9. Length vs Stars
    plt.figure()
    df_scatter = df.sample(min(10000, len(df)), random_state=42) # Çok fazla nokta olmaması için sample
    sns.regplot(data=df_scatter, x='stars', y='review_length', scatter_kws={'alpha':0.1}, line_kws={'color':'red'})
    plt.title('Yorum Uzunluğu ile Yıldız Puanı Korelasyonu')
    plt.xlabel('Yıldız Puanı')
    plt.ylabel('Yorum Uzunluğu (Karakter)')
    plt.tight_layout()
    plt.savefig('results/eda_length_vs_stars.png')
    plt.close()
    print("[OK] Kaydedildi: results/eda_length_vs_stars.png")
    
    # 10. Time trend
    plt.figure()
    yearly_counts = df.groupby(['year', 'class_name']).size().reset_index(name='count')
    sns.lineplot(data=yearly_counts, x='year', y='count', hue='class_name', marker='o', palette='Set2')
    plt.title('Yıllara Göre Yorum Sayısı Trendi')
    plt.xlabel('Yıl')
    plt.ylabel('Yorum Sayısı')
    plt.xticks(yearly_counts['year'].unique(), rotation=45)
    plt.tight_layout()
    plt.savefig('results/eda_time_trend.png')
    plt.close()
    print("[OK] Kaydedildi: results/eda_time_trend.png")
    
    # BÖLÜM 4 - Summary
    print("\nBÖLÜM 4: 4x3 Grid Rapor Oluşturuluyor...")
    
    image_files = [
        'results/eda_class_distribution.png',
        'results/eda_star_distribution.png',
        'results/eda_review_length.png',
        'results/eda_word_count.png',
        'results/eda_wordcloud_kotu.png',
        'results/eda_wordcloud_orta.png',
        'results/eda_wordcloud_iyi.png',
        'results/eda_top_words.png',
        'results/eda_bigrams.png',
        'results/eda_social_features.png',
        'results/eda_length_vs_stars.png',
        'results/eda_time_trend.png'
    ]
    
    fig, axes = plt.subplots(4, 3, figsize=(36, 32), dpi=150)
    fig.suptitle('Yelp Restoran Yorumları - Keşifsel Veri Analizi (EDA) Raporu', fontsize=40, y=0.98)
    axes = axes.flatten()
    
    for i, img_path in enumerate(image_files):
        if os.path.exists(img_path):
            img = mpimg.imread(img_path)
            axes[i].imshow(img)
            axes[i].axis('off')
        else:
            axes[i].text(0.5, 0.5, 'Resim Bulunamadı', ha='center', va='center', fontsize=20)
            axes[i].axis('off')
            
    plt.tight_layout()
    # tight_layout sonrasında suptitle'ın üstte kalması için:
    plt.subplots_adjust(top=0.95) 
    plt.savefig('results/eda_full_report.png')
    plt.close()
    print("[OK] Kaydedildi: results/eda_full_report.png")
    
    print("\n" + "=" * 50)
    print("SINIFLARA GÖRE ÖZET İSTATİSTİKLER (Kelime Sayısı)".center(50))
    print("=" * 50)
    summary = df.groupby('class_name')['word_count'].agg(['mean', 'std', 'min', 'max'])
    print(summary)
    print("=" * 50)
    
if __name__ == "__main__":
    main()
