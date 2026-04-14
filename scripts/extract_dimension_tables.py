import camelot
import pdfplumber
import tabula 
from pathlib import Path

MIL_STD_PATH = Path("./dimensions/MIL-STD-1560C_CHG-2.pdf")

with pdfplumber.open(MIL_STD_PATH) as pdf:
    for page in pdf.pages[18:19]:
        for table in page.extract_tables():
            print(table)

# dfs = tabula.read_pdf(MIL_STD_PATH, pages=[19,25])
# print(dfs[0])