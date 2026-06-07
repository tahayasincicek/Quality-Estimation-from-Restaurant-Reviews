import json
import base64
import os
import re

nb_paths = ['02_eda.ipynb', '06_model_evaluation.ipynb']
for path in nb_paths:
    print(f'Extracting {path}')
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    for cell in nb.get('cells', []):
        if cell.get('cell_type') != 'code': continue
        
        source = ''.join(cell.get('source', []))
        pngs = [out['data']['image/png'] for out in cell.get('outputs', []) if out.get('data', {}).get('image/png')]
        if not pngs:
            continue
            
        static_matches = re.findall(r'savefig\([\'"](.*?\.png)[\'"]', source)
        if len(static_matches) == len(pngs):
            for m, b64 in zip(static_matches, pngs):
                filepath = os.path.join('.', m)
                with open(filepath, 'wb') as f: f.write(base64.b64decode(b64))
                print(f'Saved {filepath}')
            continue
            
        if 'eda_wordcloud' in source:
            names = ['kotü', 'orta', 'iyi'] if 'Kötü' in source else ['poor', 'average', 'good']
            for i, name in enumerate(['kotu', 'orta', 'iyi'][:len(pngs)]):
                filepath = f'results/eda_wordcloud_{name}.png'
                with open(filepath, 'wb') as f: f.write(base64.b64decode(pngs[i]))
                print(f'Saved {filepath}')
                
        elif 'eda_top_words' in source:
            for i, name in enumerate(['bad', 'middle', 'good'][:len(pngs)]):
                filepath = f'results/eda_top_words_{name}.png'
                with open(filepath, 'wb') as f: f.write(base64.b64decode(pngs[i]))
                print(f'Saved {filepath}')
                
        elif 'eda_bigrams' in source:
            for i, name in enumerate(['bad', 'middle', 'good'][:len(pngs)]):
                filepath = f'results/eda_bigrams_{name}.png'
                with open(filepath, 'wb') as f: f.write(base64.b64decode(pngs[i]))
                print(f'Saved {filepath}')
                
        elif 'confusion_matrix_' in source and 'for' in source:
            m_names = ['Logistic_Regression', 'SVM', 'SGD', 'TextCNN', 'FastText']
            for i, b64 in enumerate(pngs):
                if i < len(m_names):
                    filepath = f'results/confusion_matrix_{m_names[i]}.png'
                    with open(filepath, 'wb') as f: f.write(base64.b64decode(b64))
                    print(f'Saved {filepath}')
                    
        elif 'roc_curve_class_' in source:
            m_names = ['Bad', 'Middle', 'Good']
            for i, b64 in enumerate(pngs):
                if i < len(m_names):
                    filepath = f'results/roc_curve_class_{m_names[i]}.png'
                    with open(filepath, 'wb') as f: f.write(base64.b64decode(b64))
                    print(f'Saved {filepath}')
                    
        elif 'pr_curve_class_' in source:
            m_names = ['Bad', 'Middle', 'Good']
            for i, b64 in enumerate(pngs):
                if i < len(m_names):
                    filepath = f'results/pr_curve_class_{m_names[i]}.png'
                    with open(filepath, 'wb') as f: f.write(base64.b64decode(b64))
                    print(f'Saved {filepath}')
