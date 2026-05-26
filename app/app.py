import os
import re
import time
import json
import warnings
from flask import Flask, render_template, request, jsonify, send_from_directory
import numpy as np
import pandas as pd
import joblib
import scipy.sparse
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences

warnings.filterwarnings('ignore')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Ensure NLTK resources are available
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')

# Global variables to hold models
models = {}
vectorizer = None
scaler = None
tokenizer = None
models_status = {
    'lr': 'err', 'svm': 'err', 'lstm': 'err', 'bilstm': 'err', 'cnnlstm': 'err'
}

def load_resources():
    global vectorizer, scaler, tokenizer
    try:
        if os.path.exists(os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')):
            vectorizer = joblib.load(os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl'))
        if os.path.exists(os.path.join(MODELS_DIR, 'scaler.pkl')):
            scaler = joblib.load(os.path.join(MODELS_DIR, 'scaler.pkl'))
        if os.path.exists(os.path.join(MODELS_DIR, 'tokenizer.pkl')):
            tokenizer = joblib.load(os.path.join(MODELS_DIR, 'tokenizer.pkl'))
            
        # Load models
        if os.path.exists(os.path.join(MODELS_DIR, 'lr_model.pkl')):
            models['lr'] = joblib.load(os.path.join(MODELS_DIR, 'lr_model.pkl'))
            models_status['lr'] = 'ok'
            
        if os.path.exists(os.path.join(MODELS_DIR, 'svm_model.pkl')):
            models['svm'] = joblib.load(os.path.join(MODELS_DIR, 'svm_model.pkl'))
            models_status['svm'] = 'ok'
            
        if os.path.exists(os.path.join(MODELS_DIR, 'lstm_model.h5')):
            models['lstm'] = tf.keras.models.load_model(os.path.join(MODELS_DIR, 'lstm_model.h5'))
            models_status['lstm'] = 'ok'
            
        if os.path.exists(os.path.join(MODELS_DIR, 'bilstm_model.h5')):
            models['bilstm'] = tf.keras.models.load_model(os.path.join(MODELS_DIR, 'bilstm_model.h5'))
            models_status['bilstm'] = 'ok'
            
        if os.path.exists(os.path.join(MODELS_DIR, 'cnn_lstm_model.h5')):
            models['cnnlstm'] = tf.keras.models.load_model(os.path.join(MODELS_DIR, 'cnn_lstm_model.h5'))
            models_status['cnnlstm'] = 'ok'
            
    except Exception as e:
        print(f"Error loading models: {e}")

# Call immediately
load_resources()

def extract_features(text):
    tb = TextBlob(text)
    review_length = len(text)
    word_count = len(text.split())
    exclamation_count = text.count('!')
    question_count = text.count('?')
    avg_word_length = review_length / word_count if word_count > 0 else 0
    uppercase_ratio = sum(1 for c in text if c.isupper()) / review_length if review_length > 0 else 0
    sentiment_polarity = tb.sentiment.polarity
    sentiment_subjectivity = tb.sentiment.subjectivity
    
    return [review_length, word_count, exclamation_count, question_count, 
            avg_word_length, uppercase_ratio, sentiment_polarity, sentiment_subjectivity]

def clean_text(text):
    text = text.lower()
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return " ".join(words)

def get_prediction(text, model_name='lr'):
    start_t = time.time()
    
    num_feats = extract_features(text)
    cleaned = clean_text(text)
    
    tb = TextBlob(text)
    stats = {
        'word_count': num_feats[1],
        'char_count': num_feats[0],
        'sentiment': round(num_feats[6], 2)
    }
    
    top_words = []
    
    pred_idx = 1
    conf_dict = {'poor': 0, 'average': 0, 'good': 0}
    
    if model_name in ['lr', 'svm'] and vectorizer and scaler:
        tfidf_mat = vectorizer.transform([cleaned])
        
        # Simple top words based on tfidf
        feature_names = vectorizer.get_feature_names_out()
        coo = tfidf_mat.tocoo()
        sorted_items = sorted(zip(coo.col, coo.data), key=lambda x: x[1], reverse=True)[:5]
        for col, score in sorted_items:
            # assign positive/negative polarity via textblob
            pol = TextBlob(feature_names[col]).sentiment.polarity
            pol = pol if pol != 0 else (1 if num_feats[6] > 0 else -1)
            top_words.append({'word': str(feature_names[col]), 'score': float(round(score * pol * 100, 1))})
            
        num_mat = scaler.transform([num_feats])
        combined = scipy.sparse.hstack([tfidf_mat, scipy.sparse.csr_matrix(num_mat)])
        
        model = models[model_name]
        if hasattr(model, 'predict_proba'):
            probs = model.predict_proba(combined)[0]
            pred_idx = np.argmax(probs)
            conf_dict = {'poor': float(probs[0]*100), 'average': float(probs[1]*100), 'good': float(probs[2]*100)}
        else:
            # SVM doesn't always have predict_proba depending on calibration
            pred_idx = model.predict(combined)[0]
            # fake confidence
            conf_dict = {'poor': 100 if pred_idx==0 else 0, 'average': 100 if pred_idx==1 else 0, 'good': 100 if pred_idx==2 else 0}
            
    elif model_name in ['lstm', 'bilstm', 'cnnlstm'] and tokenizer:
        seq = tokenizer.texts_to_sequences([cleaned])
        padded = pad_sequences(seq, maxlen=200, padding='post', truncating='post')
        
        model = models[model_name]
        probs = model.predict(padded, verbose=0)[0]
        pred_idx = np.argmax(probs)
        conf_dict = {'poor': float(probs[0]*100), 'average': float(probs[1]*100), 'good': float(probs[2]*100)}
        
    labels = {0: 'Poor', 1: 'Average', 2: 'Good'}
    label = labels.get(pred_idx, 'Average')
    
    elapsed = int((time.time() - start_t) * 1000)
    
    return {
        'prediction': int(pred_idx),
        'label': label,
        'confidence': conf_dict,
        'top_words': top_words,
        'stats': stats,
        'elapsed_ms': elapsed
    }

@app.route('/')
def index():
    return render_template('index.html', models_status=models_status)

@app.route('/comparison')
def comparison():
    return render_template('comparison.html', models_status=models_status)

@app.route('/eda')
def eda():
    return render_template('eda.html', models_status=models_status)

@app.route('/bulk')
def bulk():
    return render_template('bulk.html', models_status=models_status)

@app.route('/about')
def about():
    return render_template('about.html', models_status=models_status)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    text = data.get('text', '')
    model_name = data.get('model_name', 'lr')
    if not text:
        return jsonify({'error': 'No text provided'})
    if model_name not in models:
        return jsonify({'error': 'Model not loaded'})
        
    res = get_prediction(text, model_name)
    
    # Run all models quickly for the "All Models" table
    all_models_res = []
    for m in ['lr', 'svm', 'lstm', 'bilstm', 'cnnlstm']:
        if m in models:
            m_res = get_prediction(text, m)
            type_str = 'Deep' if m in ['lstm', 'bilstm', 'cnnlstm'] else 'Classical'
            all_models_res.append({
                'name': m.upper(),
                'type': type_str,
                'label': m_res['label'],
                'conf': max(m_res['confidence'].values()),
                'time': m_res['elapsed_ms']
            })
    res['all_models'] = all_models_res
    
    return jsonify(res)

@app.route('/bulk_predict', methods=['POST'])
def bulk_predict():
    data = request.json
    texts = data.get('texts', [])
    model_name = data.get('model_name', 'lr')
    if not texts:
        return jsonify({'error': 'No texts provided'})
    if model_name not in models:
        return jsonify({'error': 'Model not loaded'})
        
    results = []
    for t in texts:
        r = get_prediction(t, model_name)
        results.append({
            'text': t,
            'prediction': r['prediction'],
            'label': r['label'],
            'confidence': max(r['confidence'].values())
        })
        
    return jsonify({'results': results})

@app.route('/confusion/<model>')
def get_confusion(model):
    cmap = {
        'lr': 'confusion_matrix_Logistic_Regression.png',
        'svm': 'confusion_matrix_SVM.png',
        'lstm': 'confusion_matrix_LSTM.png',
        'bilstm': 'confusion_matrix_BiLSTM.png',
        'cnnlstm': 'confusion_matrix_CNN_LSTM.png'
    }
    filename = cmap.get(model, f'cm_{model}.png')
    return send_from_directory(RESULTS_DIR, filename)

@app.route('/history/<model>')
def get_history(model):
    hmap = {
        'lstm': 'history_lstm.png',
        'bilstm': 'history_bilstm.png',
        'cnnlstm': 'history_cnn_lstm.png'
    }
    filename = hmap.get(model, f'history_{model}.png')
    return send_from_directory(RESULTS_DIR, filename)

@app.route('/eda_img/<chart>')
def get_eda(chart):
    emap = {
        'roc_curves': 'roc_curves_all.png',
        'pr_curves': 'pr_curves_all.png',
        'eda_wordcloud_kotu': 'eda_wordcloud_kotü.png'
    }
    filename = emap.get(chart, f'{chart}.png')
    return send_from_directory(RESULTS_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
