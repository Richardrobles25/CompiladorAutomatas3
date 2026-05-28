import sys, glob
sys.stdout.reconfigure(encoding='utf-8')
from pypdf import PdfReader

files = glob.glob(r'Documentacion\*.pdf')
r = PdfReader(files[0])
for i, p in enumerate(r.pages):
    print(f'--- PAGINA {i+1} ---')
    print(p.extract_text())
