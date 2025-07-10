import pandas as pd
from docx import Document

def load_urls(file_path):
    ext = file_path.lower().split('.')[-1]
    urls = []
    if ext == 'csv':
        df = pd.read_csv(file_path)
        urls = df.iloc[:, 0].dropna().astype(str).tolist()
    elif ext in ['xlsx', 'xls']:
        df = pd.read_excel(file_path)
        urls = df.iloc[:, 0].dropna().astype(str).tolist()
    elif ext == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    elif ext == 'docx':
        doc = Document(file_path)
        urls = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    else:
        raise ValueError("Unsupported file type")
    return urls 