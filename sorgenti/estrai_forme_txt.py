"""docx del Libro delle Forme Non Morte -> testo per parse_forme.py (un paragrafo per riga).
Uso: python3 estrai_forme_txt.py Libro_dei_Morti_Forme_Non_Morte_vX.docx forme_non_morte.txt"""
import sys, re, docx
d = docx.Document(sys.argv[1])
righe = []
for p in d.paragraphs:
    t = p.text.replace(' ', ' ').replace(' ', ' ')
    t = re.sub(r' {2,}', ' ', t).strip()
    righe.extend(x.strip() for x in t.split('\n'))
open(sys.argv[2], 'w', encoding='utf8').write('\n'.join(righe) + '\n')
