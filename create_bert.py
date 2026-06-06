import json

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# 8. BERT Model ile Yüksek Başarılı Sınıflandırma (English DistilBERT)\n",
    "\n",
    "Bu notebook'ta, geleneksel Makine Öğrenmesi (Lojistik Regresyon, SVM) ve standart Derin Öğrenme (TextCNN, FastText) modellerinin de ötesine geçerek günümüzün State-of-the-Art (SOTA) mimarisi olan **Transformer (BERT)** tabanlı bir model kullanacağız.\n",
    "\n",
    "**ÖNEMLİ NOT:** Veri setimiz 1.6 milyon yorum gibi devasa bir boyutta olduğu için, standart bir bilgisayar ekran kartında (GPU) bu verinin tamamıyla BERT eğitmek günlerce sürebilir. Bu nedenle:\n",
    "- Daha hafif ve hızlı olan **`distilbert-base-uncased`** modelini kullanacağız.\n",
    "- 1.140.000 eğitim verisinin tamamı yerine, **dengeli seçilmiş 50.000 veya 100.000 yorumluk bir alt küme** (subset) üzerinde fine-tuning (hassas ayar) yapacağız.\n",
    "\n",
    "Gerekli kütüphaneler yüklü değilse aşağıdaki hücreyi çalıştırabilirsiniz:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "source": [
    "!pip install transformers datasets accelerate evaluate"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import torch\n",
    "import evaluate\n",
    "import joblib\n",
    "from sklearn.model_selection import train_test_split\n",
    "from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer\n",
    "from datasets import Dataset\n",
    "\n",
    "# Ekran kartı kontrolü\n",
    "device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')\n",
    "print(f\"Kullanılan Cihaz: {device}\")\n",
    "if torch.cuda.is_available():\n",
    "    print(f\"GPU: {torch.cuda.get_device_name(0)}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Veri Yükleme ve Alt Küme (Subset) Oluşturma\n",
    "1.6 Milyonluk devasa verimizi RAM ve GPU dostu boyutlara indirgiyoruz. Alt kümeyi oluştururken sınıfların (İyi, Orta, Kötü) dağılımının dengeli kalmasına dikkat edeceğiz."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "source": [
    "print(\"Veri yükleniyor...\")\n",
    "# Sadece gereken sütunları yükleyerek RAM tasarrufu yapalım\n",
    "df = pd.read_csv('data/reviews_preprocessed.csv', usecols=['text', 'label'])\n",
    "df = df.dropna(subset=['text'])\n",
    "\n",
    "# Etiketleri sayısallaştırma (Eğer henüz yapılmadıysa)\n",
    "label_map = {'Bad': 0, 'Middle': 1, 'Good': 2}\n",
    "df['label_num'] = df['label'].map(label_map)\n",
    "\n",
    "# --- SUBSET (ALT KÜME) OLUŞTURMA ---\n",
    "# Eğitim için 90.000, Test için 15.000 veri seçelim (Toplam 105.000)\n",
    "SUBSET_SIZE = 105000\n",
    "\n",
    "if len(df) > SUBSET_SIZE:\n",
    "    # Stratify ile sınıfların dağılımını koruyarak rastgele örneklem alıyoruz\n",
    "    df_subset, _ = train_test_split(df, train_size=SUBSET_SIZE, stratify=df['label_num'], random_state=42)\n",
    "else:\n",
    "    df_subset = df\n",
    "\n",
    "print(f\"Oluşturulan alt küme boyutu: {len(df_subset)}\")\n",
    "print(df_subset['label'].value_counts())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "source": [
    "# Eğitim ve test kümelerine ayırma\n",
    "train_df, test_df = train_test_split(df_subset, test_size=0.15, stratify=df_subset['label_num'], random_state=42)\n",
    "\n",
    "# HuggingFace Dataset formatına dönüştürme\n",
    "train_dataset = Dataset.from_pandas(train_df[['text', 'label_num']].reset_index(drop=True))\n",
    "test_dataset = Dataset.from_pandas(test_df[['text', 'label_num']].reset_index(drop=True))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Tokenizasyon (Metni BERT'in Anlayacağı Şekle Çevirme)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "source": [
    "model_name = \"distilbert-base-uncased\"\n",
    "tokenizer = AutoTokenizer.from_pretrained(model_name)\n",
    "\n",
    "def tokenize_function(examples):\n",
    "    return tokenizer(examples['text'], padding=\"max_length\", truncation=True, max_length=128)\n",
    "\n",
    "print(\"Eğitim seti tokenize ediliyor...\")\n",
    "tokenized_train = train_dataset.map(tokenize_function, batched=True)\n",
    "print(\"Test seti tokenize ediliyor...\")\n",
    "tokenized_test = test_dataset.map(tokenize_function, batched=True)\n",
    "\n",
    "# HuggingFace modelinin beklediği sütun ismine 'labels' olarak ayarlıyoruz\n",
    "tokenized_train = tokenized_train.rename_column(\"label_num\", \"labels\")\n",
    "tokenized_test = tokenized_test.rename_column(\"label_num\", \"labels\")\n",
    "\n",
    "# PyTorch tensör formatına dönüştürme\n",
    "tokenized_train.set_format('torch', columns=['input_ids', 'attention_mask', 'labels'])\n",
    "tokenized_test.set_format('torch', columns=['input_ids', 'attention_mask', 'labels'])"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Model Kurulumu ve Eğitim (Fine-Tuning)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "source": [
    "# Doğruluk (Accuracy) ve F1 Skoru hesaplamak için evaluate kütüphanesi metrikleri\n",
    "accuracy_metric = evaluate.load(\"accuracy\")\n",
    "f1_metric = evaluate.load(\"f1\")\n",
    "\n",
    "def compute_metrics(eval_pred):\n",
    "    logits, labels = eval_pred\n",
    "    predictions = np.argmax(logits, axis=-1)\n",
    "    acc = accuracy_metric.compute(predictions=predictions, references=labels)[\"accuracy\"]\n",
    "    f1 = f1_metric.compute(predictions=predictions, references=labels, average=\"macro\")[\"f1\"]\n",
    "    return {\"accuracy\": acc, \"f1_macro\": f1}\n",
    "\n",
    "# Modeli yükleme (3 Sınıf: Bad, Middle, Good)\n",
    "model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)\n",
    "model.to(device)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "source": [
    "training_args = TrainingArguments(\n",
    "    output_dir=\"./bert_results\",\n",
    "    evaluation_strategy=\"epoch\",\n",
    "    save_strategy=\"epoch\",\n",
    "    learning_rate=2e-5,\n",
    "    per_device_train_batch_size=16,\n",
    "    per_device_eval_batch_size=16,\n",
    "    num_train_epochs=3,\n",
    "    weight_decay=0.01,\n",
    "    load_best_model_at_end=True,\n",
    "    metric_for_best_model=\"f1_macro\",\n",
    "    logging_dir=\"./bert_logs\",\n",
    "    logging_steps=500,\n",
    "    fp16=torch.cuda.is_available(), # GPU varsa 16-bit hassasiyet ile eğitimi hızlandırır\n",
    ")\n",
    "\n",
    "trainer = Trainer(\n",
    "    model=model,\n",
    "    args=training_args,\n",
    "    train_dataset=tokenized_train,\n",
    "    eval_dataset=tokenized_test,\n",
    "    compute_metrics=compute_metrics,\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "source": [
    "# Eğitimi başlat\n",
    "print(\"BERT Modeli eğitimi başlıyor...\")\n",
    "trainer.train()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Değerlendirme ve Kaydetme"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "source": [
    "# Test seti üzerindeki nihai performansı\n",
    "results = trainer.evaluate()\n",
    "print(\"Test Seti Sonuçları:\", results)\n",
    "\n",
    "# En iyi modeli kaydetme\n",
    "trainer.save_model(\"models/distilbert_sentiment_model\")\n",
    "tokenizer.save_pretrained(\"models/distilbert_sentiment_model\")\n",
    "print(\"Model 'models/distilbert_sentiment_model' klasörüne başarıyla kaydedildi!\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

with open("08_bert_model.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)
