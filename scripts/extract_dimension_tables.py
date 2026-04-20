import pdfplumber
import pandas as pd
from pathlib import Path

import csv
import re
from tqdm import tqdm

START_PAGE = 14 + 5 - 1
END_PAGE = 167 + 5 + 1

CONTACTS_TO_OMIT = ['22M', '22D', '22', '23-22']

DIMENSIONS_DIR = Path("./dimensions")
MIL_STD_PATH = DIMENSIONS_DIR / Path("MIL-STD-1560C_CHG-2.pdf")

APPLICABLE_INSERT_ARRANGEMENTS = DIMENSIONS_DIR / Path("applicable_insert_arrangements.csv")

CSV_NAME_TEMPLATE = '{name}_contact_positions.csv'

overview_tables = []
applicable_insert_arrangements = []

def reformat_overview_table(table:pd.DataFrame):
    next_overview_table = table
    header = table.loc[0,:].fillna('').apply(lambda x: ''.join(x).replace('\n', ' '))
    next_overview_table.columns = header
    next_overview_table = next_overview_table.loc[1:].reset_index(drop=True)
    return next_overview_table

def extract_insert_arrangement(table:pd.DataFrame):
    if 'Arrangement no.' in table.columns:
        name_columns = table.loc[:,['Shell size', 'Arrangement no.']].dropna()
    elif 'Arrangement No.' in table.columns:
        name_columns = table.loc[:,['Shell size','Arrangement No.']].dropna()
    elif 'Arrange- ment no.' in table.columns:
        name_columns = table.loc[:,['Shell size','Arrange- ment no.']].dropna()
    elif 'Arrange- ment No.' in table.columns:
        name_columns = table.loc[:,['Shell size','Arrange- ment No.']].dropna()
    elif 'Arrange ment no.' in table.columns:
        name_columns = table.loc[:,['Shell size','Arrange ment no.']].dropna()
    else:
        breakpoint()

    
    return f"{name_columns.iloc[0, 0]}-{str(name_columns.iloc[0, 1]).lstrip('-')}"

def is_overview_table(table:pd.DataFrame)->bool:
    return 'shell\\nsize' in table.to_string().lower()

def find_overview_tables(page)->tuple[pd.DataFrame,str]:
    for table in page.extract_tables():
        df_table = pd.DataFrame(table)
        if is_overview_table(df_table):
            next_overview_table = reformat_overview_table(df_table)
            
            if 'Size contacts' not in next_overview_table.columns.values:
                print('"Size contacts" not in this table!')
                print(next_overview_table.head())
                continue
            mask = next_overview_table.loc[:,'Size contacts'].isin(CONTACTS_TO_OMIT)
            if not mask.any():
                insert_arrangement_name = extract_insert_arrangement(next_overview_table)
                return (next_overview_table, insert_arrangement_name)
            
    return (None,'')

def find_dimension_tables(dimension_tables:dict, page):
    for table in page.extract_tables():
        df_table = pd.DataFrame(table)
        dimension_tables = extract_applicable_insert_dimensions(df_table,dimension_tables)
    return dimension_tables

def extract_applicable_insert_dimensions(table:pd.DataFrame, dimension_tables:dict):
    for insert_arrangement_name in dimension_tables.keys():
        if is_dimension_table(table, insert_arrangement_name):
            # the first 3 rows are not
            # necessary
            table = remove_header_rows(table)
            # reshape the values as rows of 3
            # columns
            triple_column_table = reshape_values(table)
            
            # perform regex operation on values
            # to extract mm position
            mm_dimension_table = extract_mm_positions(triple_column_table)
            # concatenate with existing data in
            # the dictionary if there is any
            dimension_tables = combine_with_previous(
                dimension_tables,
                mm_dimension_table,
                insert_arrangement_name)
    return dimension_tables

def is_dimension_table(table:pd.DataFrame, insert_arrangement_name):
    characteristic_string = ' ' + insert_arrangement_name + ')'
    return characteristic_string in table.to_string().lower()

def remove_header_rows(table:pd.DataFrame):
    return table.loc[3:,:]

def reshape_values(table:pd.DataFrame)->pd.DataFrame:
    triplet_values = table.to_numpy().reshape(-1,3)
    formatted_table = pd.DataFrame(triplet_values,columns=['ID','x_string', 'y_string'])
    return formatted_table

def extract_mm_positions(table:pd.DataFrame)->pd.DataFrame:
    table['x'] = table['x_string'].apply(extract_mm)
    table['y'] = table['y_string'].apply(extract_mm)
    return table.loc[:,['ID','x','y']].dropna()

def extract_mm(dimension:str)->float:
    regex_pattern = r'([+-]?)\d*\.?\d*\s*\(([\d*\.]+)\)'
    dimension_match = re.match(regex_pattern, dimension)
    if dimension_match:
        sign = -1 if dimension_match.group(1) == '-' else 1
        dimension_mm = float(dimension_match.group(2))
        return sign * dimension_mm

def combine_with_previous(dimension_tables:dict, mm_table:pd.DataFrame, insert_name:str)->dict:
    if dimension_tables[insert_name] is None:
        dimension_tables[insert_name] = sort_contacts(mm_table)
        return dimension_tables
    
    previous_table = dimension_tables[insert_name]
    combined_table = pd.concat([previous_table,mm_table],axis=0,ignore_index=True)
    dimension_tables[insert_name] = sort_contacts(combined_table)
    return dimension_tables

def sort_contacts(table:pd.DataFrame)->pd.DataFrame:
    return table.sort_values(by=['ID'])

def export_csvs(dimension_tables:dict[str,pd.DataFrame]):
    for insert_arrangement in tqdm(dimension_tables,desc="Exporting dimensions..."):
        table = dimension_tables[insert_arrangement]
        export_path = DIMENSIONS_DIR / Path(CSV_NAME_TEMPLATE.format(name=insert_arrangement))
        table.to_csv(export_path)

if not APPLICABLE_INSERT_ARRANGEMENTS.exists():
    with pdfplumber.open(MIL_STD_PATH) as pdf:
        for page_number, page in enumerate(tqdm(pdf.pages[START_PAGE:END_PAGE],desc='Finding overview tables...')):
            next_overview_table, insert_name = find_overview_tables(page)
            if insert_name != '':
                overview_tables.append(next_overview_table)
                applicable_insert_arrangements.append(insert_name)

            
    with open(APPLICABLE_INSERT_ARRANGEMENTS,'w') as csv_file:
        wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        wr.writerow(applicable_insert_arrangements)

with open(APPLICABLE_INSERT_ARRANGEMENTS, newline='') as file:
    reader = csv.reader(file)
    applicable_insert_arrangements = next(reader)


dimension_tables = dict.fromkeys(applicable_insert_arrangements)

with pdfplumber.open(MIL_STD_PATH) as pdf:
    for page_number, page in enumerate(tqdm(pdf.pages[START_PAGE:END_PAGE],desc='Finding dimension tables...')):
        dimension_tables = find_dimension_tables(dimension_tables, page)

export_csvs(dimension_tables)
          

# dfs = tabula.read_pdf(MIL_STD_PATH, pages=[19,25])
# print(dfs[0])