import sys
sys.path.insert(0,'.pdfdeps')
import pdfplumber
with pdfplumber.open('tmp/pdfs/sbtet_polycet_2026.pdf') as pdf:
 for i in range(33,38):
  tables=pdf.pages[i].extract_tables()
  print('\nPAGE',i+1)
  for t in tables:
   for row in t:
    if row and any(str(x).strip() for x in row[:4]): print(row[:5],row[5:])
