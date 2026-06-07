# Restaurant Review Quality Mining with Yelp

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5+-yellow.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.20+-orange.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.3+-red.svg)
![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-yellow.svg)
![Flask](https://img.shields.io/badge/Flask-Web_App-black.svg)

This project is a full text-mining pipeline for restaurant review quality prediction on the Yelp Open Dataset. It covers data preparation, exploratory analysis, preprocessing, feature extraction, model training, model evaluation, explainability, aspect-based sentiment analysis, DistilBERT fine-tuning, and a Flask web application for interactive inference.

The main prediction task is 3-class review quality classification:

- `0` Poor / Bad
- `1` Average / Neutral
- `2` Good

## Project Scope

The project includes:

- Yelp restaurant review filtering and class balancing.
- Exploratory data analysis with class distributions, length analysis, time trends, word clouds, top words, bigrams, and correlation plots.
- Leakage-safe train/validation/test splitting before feature fitting.
- TF-IDF word features, optional character TF-IDF, numeric text features, scaling, and Keras sequence tokenization.
- Classical ML models: Logistic Regression, Linear SVM, SGD Classifier, and LightGBM.
- Deep learning models: TextCNN, FastText-style model, LSTM, BiLSTM, CNN-LSTM, and MLP artifacts.
- Transformer model: DistilBERT fine-tuned on a hardware-friendly subset and evaluated on the official test split.
- Model evaluation with confusion matrices, ROC curves, PR curves, training histories, radar/bar comparisons, error analysis, and feature ablation.
- LIME explanation output for local interpretability.
- Rule-based ABSA for food, service, ambience, and price dimensions.
- Flask web app with single-review analysis, all-model comparison, bulk CSV prediction, EDA pages, sarcasm detection, reviewer useful-vote profiling, and text decoding helpers.

## Repository Layout

```text
.
|-- 01_data_preparation.ipynb
|-- 02_eda.ipynb
|-- 03_text_preprocessing.ipynb
|-- 04_feature_extraction.ipynb
|-- 05_model_training.ipynb
|-- 06_model_evaluation.ipynb
|-- 07_aspect_based_sentiment.ipynb
|-- 08_bert_model.ipynb
|-- app/
|   |-- app.py
|   |-- aspect_analyzer.py
|   |-- reviewer_profiler.py
|   |-- sarcasm_detector.py
|   |-- text_decoder.py
|   |-- templates/
|   `-- static/
|-- report/
|   |-- main.tex
|   `-- figures/
|-- requirements.txt
`-- README.md
```

Large generated artifacts are intentionally ignored by Git:

- `data/`
- `features/`
- `models/`
- `results/`
- `bert_results/`
- `Yelp JSON/`
- `Yelp-JSON.zip`

Run the notebooks in order to regenerate them.

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

The project was developed with Python 3.13. Some ML libraries may be easier to install on Python 3.11 or 3.12 depending on the local machine, CUDA setup, and wheel availability.

## Data

The pipeline expects the Yelp Open Dataset files locally. The raw dataset is not committed because it is large.

Typical source layout:

```text
Yelp JSON/
└── yelp_academic_dataset_review.json
```

`01_data_preparation.ipynb` filters restaurant reviews, maps star ratings into the 3 target classes, balances the dataset, and writes prepared data under `data/`.

## Notebook Pipeline

Run notebooks in this order:

1. `01_data_preparation.ipynb`
   - Loads Yelp review data.
   - Filters and balances classes.
   - Creates the prepared review dataset.

2. `02_eda.ipynb`
   - Produces class distribution, review length, word count, time trend, top-word, bigram, word-cloud, and statistical EDA outputs.

3. `03_text_preprocessing.ipynb`
   - Cleans text.
   - Preserves negation words.
   - Applies tokenization, lemmatization, and text feature engineering.

4. `04_feature_extraction.ipynb`
   - Creates official train/validation/test indices.
   - Fits TF-IDF, scaler, and tokenizer only on the training split.
   - Saves feature artifacts under `features/` and reusable preprocessing artifacts under `models/`.

5. `05_model_training.ipynb`
   - Trains classical ML models and neural models.
   - Saves trained model artifacts into `models/`.

6. `06_model_evaluation.ipynb`
   - Evaluates models on the official test split.
   - Generates comparison tables, confusion matrices, ROC/PR curves, history plots, error analysis, LIME output, and feature ablation results.

7. `07_aspect_based_sentiment.ipynb`
   - Runs rule-based aspect detection.
   - Splits reviews into sentence/clause-level opinion units for mixed-aspect reviews.
   - Produces food/service/ambience/price sentiment summaries.

8. `08_bert_model.ipynb`
   - Fine-tunes `distilbert-base-uncased`.
   - Uses a subset of the official training split for hardware practicality.
   - Evaluates on the same official test split.
   - Saves BERT weights as `pytorch_model.bin` to avoid Windows `model.safetensors` file-locking issues.

## Models

The project trains and compares:

- Logistic Regression
- Linear SVM
- LightGBM
- SGD Classifier
- TextCNN
- FastText-style neural baseline
- LSTM
- BiLSTM
- CNN-LSTM
- MLP artifact
- DistilBERT

The best classical models reach roughly 80% accuracy/F1 on the subjective 3-class task. Exact metrics are written to `results/final_evaluation.csv`, `results/model_comparison.csv`, and `results/bert_test_evaluation.csv` after running the evaluation notebooks.

## Flask Web App

Start the local app:

```bash
cd app
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

Main app features:

- Single-review prediction with selectable model.
- Confidence bars and word impact visualization.
- ABSA insights for food, service, ambience, and price.
- Sarcasm warning for suspicious positive wording around negative experiences.
- Reviewer useful-vote input and trusted/fake-risk profiling.
- Random dataset review loading.
- All-model prediction table for quick comparison.
- Bulk CSV prediction.
- EDA and model comparison pages.

The app automatically disables model buttons when the required artifact is missing from `models/`.

## ABSA Behavior

The ABSA module is intentionally rule-based and interpretable. It detects aspect keywords, then assigns sentiment to the local opinion unit rather than always using the whole review. This prevents mixed text such as:

```text
service is bad, soup is delicious
```

from assigning the same sentiment to both aspects. The expected ABSA output is:

- Service: Poor
- Food: Good

## Generated Outputs

After running the notebooks, the project can generate:

- Model artifacts in `models/`
- TF-IDF/scaler/tokenizer artifacts
- Evaluation CSV files
- Confusion matrices
- ROC and PR curves
- Training history plots
- EDA plots and word clouds
- LIME HTML explanation
- ABSA plot
- LaTeX report figures

## Report

The academic report is in:

```text
report/main.tex
```

Figures used by the report are stored under:

```text
report/figures/
```

## Notes

- Keep the Flask app closed while overwriting large model files if Windows reports file-lock errors.
- `08_bert_model.ipynb` saves DistilBERT weights as `pytorch_model.bin`; the Flask app prefers that file when it exists.
- Because large artifacts are ignored, a fresh clone requires rerunning the notebooks or manually placing generated artifacts into `data/`, `features/`, `models/`, and `results/`.
