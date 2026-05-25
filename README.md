# Quality Estimation from Restaurant Reviews (Yelp Dataset)

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.20+-orange.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5+-yellow.svg)
![NLP](https://img.shields.io/badge/NLP-NLTK%20%7C%20TextBlob-green.svg)

## Project Overview
This project aims to predict the quality/sentiment rating of restaurant experiences (Good, Neutral, Bad) strictly from the textual content of user reviews. Utilizing a massive subset of the **Yelp Open Dataset (~1.6 Million reviews)**, we process raw text into numerical features using advanced Natural Language Processing (NLP) techniques and train both traditional Machine Learning and deep Neural Network architectures from scratch.

## Technology Stack
* **Language:** Python 3.13
* **Data Processing:** Pandas, NumPy, SciPy
* **NLP & Text Mining:** NLTK, TextBlob
* **Machine Learning:** Scikit-learn (Logistic Regression, SVM, GridSearchCV)
* **Deep Learning:** TensorFlow & Keras (LSTM, BiLSTM, 1D-CNN)
* **Visualization:** Matplotlib, Seaborn, Plotly

## Model Architectures
We designed and trained 5 distinct models to comprehensively evaluate both sparse representations and dense embeddings:
1. **Logistic Regression (Baseline):** Trained on TF-IDF sparse matrices.
2. **Support Vector Machine (LinearSVC):** Calibrated SVC on TF-IDF.
3. **Long Short-Term Memory (LSTM):** Trained on padded token sequences.
4. **Bidirectional LSTM (BiLSTM):** Capturing past and future text context.
5. **CNN + LSTM Hybrid:** 1D Convolutions for local feature extraction followed by LSTM.

*(Note: Deep Learning models were trained on a 100k random subset to optimize CPU training times, whereas classical ML models digested the entire 1.14M training corpus).*

## Key Results & Metrics
Evaluated on a completely unseen test set, distinguishing between 3 highly subjective classes:
* **0 (Bad / Kötü)**
* **1 (Neutral / Orta)**
* **2 (Good / İyi)**

| Model | Accuracy | F1-Macro |
| :--- | :---: | :---: |
| **Logistic Regression** | **~80.0%** | **0.798** |
| **SVM (LinearSVC)** | ~79.5% | 0.793 |
| **LSTM** | ~76.4% | 0.767 |
| **BiLSTM** | ~74.0% | 0.738 |
| **CNN+LSTM** | ~71.5% | 0.707 |

*Achieving ~80% accuracy on a highly subjective 3-class NLP task without using pre-trained Transformer models (like BERT) is a state-of-the-art outcome for classical modeling.*

## Project Structure (Pipeline)

The project is heavily modularized into 6 sequential Jupyter Notebooks to prevent Memory leaks and allow efficient checkpointing of massive datasets:

* `01_data_preparation.ipynb` : Data ingestion, filtering for "Restaurants", and undersampling to balance classes.
* `02_eda.ipynb` : Exploratory Data Analysis, n-gram generation, and word clouds.
* `03_text_preprocessing.ipynb` : Text cleaning, lemmatization, stopword removal, and text-based feature engineering (TextBlob polarity).
* `04_feature_extraction.ipynb` : TF-IDF vectorization and Keras Tokenizer sequence padding.
* `05_model_training.ipynb` : Hyperparameter tuning via GridSearchCV and Deep Learning model architecture definitions/training.
* `06_model_evaluation.ipynb` : Multi-model comparison, ROC curves, Precision-Recall curves, Radar charts, Confusion Matrices, and qualitative Inference testing.

## Future Work
- [ ] Migrate models to Google Colab for full-scale GPU training of the LSTM architectures on the entire 1.6M dataset.
- [ ] Implement a **Web User Interface (UI)** using Streamlit or Next.js to provide real-time quality estimation for custom user text inputs.