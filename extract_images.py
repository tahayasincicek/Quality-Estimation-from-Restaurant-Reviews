import json
import re
import os
import base64

def extract_images(notebook_path):
    print(f"Extracting from {notebook_path}...")
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    for cell in nb.get('cells', []):
        if cell.get('cell_type') != 'code':
            continue
            
        source = ''.join(cell.get('source', []))
        
        # Find all savefig paths in this cell
        paths = re.findall(r'savefig\([\'"](.*?\.png)[\'"]', source)
        if not paths:
            paths = re.findall(r'fig\.write_image\([\'"](.*?\.png)[\'"]', source)
            
        if not paths:
            continue
            
        # We assume one image output per cell that has savefig, or matches sequentially
        png_outputs = [out for out in cell.get('outputs', []) 
                       if out.get('data', {}).get('image/png')]
                       
        for i, path in enumerate(paths):
            if i < len(png_outputs):
                b64_data = png_outputs[i]['data']['image/png']
                
                # Write to file
                filepath = os.path.join('.', path)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'wb') as img_f:
                    img_f.write(base64.b64decode(b64_data))
                print(f"Saved {filepath}")

notebooks = ['02_eda.ipynb', '03_text_preprocessing.ipynb', '05_model_training.ipynb', '06_model_evaluation.ipynb', '07_aspect_based_sentiment.ipynb']
for nb in notebooks:
    if os.path.exists(nb):
        extract_images(nb)
