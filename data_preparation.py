import os
import json
import pandas as pd
from sklearn.utils import resample
from tqdm import tqdm
import config

def main():
    print("=== Başlangıç: Klasörleri Oluşturma ===")
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("features", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    # Dosya yolları
    business_file = os.path.join("data", "yelp_academic_dataset_business.json")
    review_file = os.path.join("data", "yelp_academic_dataset_review.json")
    output_file = os.path.join("data", "reviews_cleaned.csv")

    print("\n=== ADIM 1: İşletme Verilerini Okuma ve Restoranları Filtreleme ===")
    restaurant_ids = set()
    try:
        # business.json için chunk işlem
        for chunk in tqdm(pd.read_json(business_file, lines=True, chunksize=10000), desc="Business JSON Okunuyor"):
            # 'categories' null olan satırları atlamak veya boş string ile doldurmak
            mask = chunk['categories'].fillna('').str.contains('Restaurants', case=False, na=False)
            restaurants = chunk[mask]
            restaurant_ids.update(restaurants['business_id'].tolist())
            
        print(f"Toplam bulunan restoran sayısı: {len(restaurant_ids)}")
    except FileNotFoundError:
        print(f"HATA: {business_file} bulunamadı. Lütfen dosyanın data/ klasöründe olduğundan emin olun.")
        return
    except Exception as e:
        print(f"HATA: business.json okunurken hata oluştu: {str(e)}")
        return

    print("\n=== ADIM 2: Yorumları Okuma ve Sadece Restoranları Filtreleme ===")
    filtered_reviews = []
    columns_to_keep = ['review_id', 'business_id', 'stars', 'text', 'useful', 'funny', 'cool', 'date']
    
    try:
        for chunk in tqdm(pd.read_json(review_file, lines=True, chunksize=10000), desc="Review JSON Okunuyor"):
            # Sadece restoran business_id'leri
            chunk_filtered = chunk[chunk['business_id'].isin(restaurant_ids)]
            # İstenen sütunlar
            chunk_filtered = chunk_filtered[columns_to_keep]
            filtered_reviews.append(chunk_filtered)
            
        # Tüm listeyi DataFrame'e dönüştür
        if len(filtered_reviews) == 0:
            print("HATA: Hiç yorum bulunamadı. Dosya boş veya restoran yorumu yok.")
            return
            
        df = pd.concat(filtered_reviews, ignore_index=True)
        toplam_ilk_yorum = len(df)
        print(f"Filtrelenen toplam restoran yorumu sayısı: {toplam_ilk_yorum}")
    except FileNotFoundError:
        print(f"HATA: {review_file} bulunamadı. Lütfen dosyanın data/ klasöründe olduğundan emin olun.")
        return
    except Exception as e:
        print(f"HATA: review.json okunurken hata oluştu: {str(e)}")
        return

    print("\n=== ADIM 3: Veri Temizliği ===")
    try:
        # Boş veya None text at
        df = df.dropna(subset=['text'])
        df = df[df['text'].astype(str).str.strip() != '']
        
        # 10 karakterden kısa yorumları at
        df = df[df['text'].str.len() >= 10]
        
        # Duplicate review_id'leri at
        df = df.drop_duplicates(subset=['review_id'])
        
        print(f"Temizlik sonrası kalan yorum sayısı: {len(df)}")
    except Exception as e:
        print(f"HATA: Veri temizliği sırasında hata oluştu: {str(e)}")
        return

    print("\n=== ADIM 4: Yıldız -> Sınıf Dönüşümü ===")
    try:
        def map_stars(star):
            if star in [1, 2]:
                return 0  # Kötü
            elif star == 3:
                return 1  # Orta
            elif star in [4, 5]:
                return 2  # İyi
            return -1

        df['label'] = df['stars'].apply(map_stars)
        # Sadece geçerli etiketleri tut
        df = df[df['label'] != -1]
    except Exception as e:
        print(f"HATA: Sınıf dönüşümü sırasında hata oluştu: {str(e)}")
        return

    print("\n=== ADIM 5: Sınıf Dengesizliğini Kontrol Etme ve Undersampling ===")
    try:
        print("Dengeleme Öncesi Sınıf Dağılımı:")
        class_counts = df['label'].value_counts()
        for label_val, count in class_counts.items():
            print(f"  {config.CLASS_NAMES[label_val]} (Sınıf {label_val}): {count} (%{count/len(df)*100:.2f})")
            
        # En az olan sınıfın sayısını bul
        min_class_count = class_counts.min()
        print(f"\nEn az sınıf sayısı ({min_class_count}) baz alınarak undersampling yapılıyor...")
        
        # Her sınıf için resampling
        dfs_to_concat = []
        for label_val in class_counts.index:
            class_df = df[df['label'] == label_val]
            resampled_df = resample(
                class_df, 
                replace=False, 
                n_samples=min_class_count, 
                random_state=config.RANDOM_STATE
            )
            dfs_to_concat.append(resampled_df)
            
        df_balanced = pd.concat(dfs_to_concat)
        # Sınıfların karışması için shuffle yapıyoruz
        df_balanced = df_balanced.sample(frac=1, random_state=config.RANDOM_STATE).reset_index(drop=True)
        
        print("\nDengeleme Sonrası Sınıf Dağılımı:")
        class_counts_balanced = df_balanced['label'].value_counts()
        for label_val, count in class_counts_balanced.items():
            print(f"  {config.CLASS_NAMES[label_val]} (Sınıf {label_val}): {count} (%{count/len(df_balanced)*100:.2f})")
            
    except Exception as e:
        print(f"HATA: Undersampling sırasında hata oluştu: {str(e)}")
        return

    print("\n=== ADIM 6: Veriyi CSV Olarak Kaydetme ===")
    try:
        df_balanced.to_csv(output_file, index=False)
        print(f"Dengelenmiş veri seti başarıyla kaydedildi: {output_file}")
    except Exception as e:
        print(f"HATA: Dosya kaydedilirken hata oluştu: {str(e)}")
        return

    print("\n=== ADIM 7: Konsola İstatistik Raporu Yazdırma ===")
    try:
        # Tarih string ise datetime'a çevir
        df_balanced['date'] = pd.to_datetime(df_balanced['date'])
        
        print("\n" + "=" * 50)
        print("VERİ SETİ İSTATİSTİK RAPORU".center(50))
        print("=" * 50)
        print(f"Toplam yorum sayısı (Temizlik Öncesi Filtrelenen): {toplam_ilk_yorum}")
        print(f"Toplam yorum sayısı (Dengelenmiş Son Hali)       : {len(df_balanced)}")
        
        print("\nSınıf Dağılımı:")
        for label_val in sorted(class_counts_balanced.index):
            print(f"  - {config.CLASS_NAMES[label_val]}: {class_counts_balanced[label_val]} yorum")
            
        # Yorum uzunluğu
        df_balanced['text_len'] = df_balanced['text'].str.len()
        avg_len = df_balanced['text_len'].mean()
        min_len = df_balanced['text_len'].min()
        max_len = df_balanced['text_len'].max()
        
        print(f"\nYorum Uzunluğu (Karakter):")
        print(f"  - Ortalama : {avg_len:.2f}")
        print(f"  - Minimum  : {min_len}")
        print(f"  - Maksimum : {max_len}")
        
        min_date = df_balanced['date'].min()
        max_date = df_balanced['date'].max()
        print(f"\nTarih Aralığı:")
        print(f"  - En eski yorum: {min_date}")
        print(f"  - En yeni yorum: {max_date}")
        
        unique_businesses = df_balanced['business_id'].nunique()
        print(f"\nBenzersiz İşletme Sayısı: {unique_businesses} restoran")
        print("=" * 50)
        
    except Exception as e:
        print(f"HATA: İstatistikler hesaplanırken hata oluştu: {str(e)}")
        return

if __name__ == "__main__":
    main()
