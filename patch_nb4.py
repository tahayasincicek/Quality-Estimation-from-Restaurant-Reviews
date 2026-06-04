import json

with open('04_feature_extraction.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb.get('cells', []):
    if cell['cell_type'] == 'code':
        source = cell.get('source', [])
        for i, line in enumerate(source):
            if "del sequences\n" in line or "del sequences" in line:
                source[i] = "# del sequences (removed due to NameError)\n"

with open('04_feature_extraction.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print('Notebook 4 successfully patched!')
