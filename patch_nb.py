import json

with open('03_text_preprocessing.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb.get('cells', []):
    if cell['cell_type'] == 'code':
        source = cell.get('source', [])
        for i, line in enumerate(source):
            if "stop_words = set(stopwords.words('english'))\n" in line:
                source[i] = "negations = {'not', 'no', 'nor', 'none', \"isn't\", \"aren't\", \"wasn't\", \"weren't\", \"haven't\", \"hasn't\", \"hadn't\", \"won't\", \"wouldn't\", \"don't\", \"doesn't\", \"didn't\", \"can't\", \"couldn't\", \"shouldn't\", \"mightn't\", \"mustn't\", 'isn', 'aren', 'wasn', 'weren', 'haven', 'hasn', 'hadn', 'won', 'wouldn', 'don', 'doesn', 'didn', 'can', 'couldn', 'shouldn', 'mightn', 'mustn'}\nstop_words = set(stopwords.words('english')) - negations\n"

with open('03_text_preprocessing.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print('Notebook 3 successfully patched!')
