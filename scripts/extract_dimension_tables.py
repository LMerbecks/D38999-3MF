import camelot
import pdfplumber
import tabula 
import pandas as pd
from pathlib import Path

import csv

START_PAGE = 14 + 5 - 1
END_PAGE = 167 + 5 + 1

CONTACTS_TO_OMIT = ['22M', '22D', '22', '23-22']

MIL_STD_PATH = Path("./dimensions/MIL-STD-1560C_CHG-2.pdf")

APPLICABLE_INSERT_ARRANGEMENTS = Path("./applicable_insert_arrangements.csv")

overview_tables = []
applicable_insert_arrangements = []

def reformat_overview_table(table:pd.DataFrame):
    next_overview_table = df_table
    header = df_table.loc[0,:].fillna('').apply(lambda x: ''.join(x).replace('\n', ' '))
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


if not APPLICABLE_INSERT_ARRANGEMENTS.exists():
    with pdfplumber.open(MIL_STD_PATH) as pdf:
        for page_number, page in enumerate(pdf.pages[START_PAGE:END_PAGE]):
            print('Page ' + str(page_number + START_PAGE))
            for table in page.extract_tables():
                df_table = pd.DataFrame(table)
                if 'shell\\nsize' in df_table.to_string().lower():
                    next_overview_table = reformat_overview_table(df_table)
                    
                    if 'Size contacts' not in next_overview_table.columns.values:
                        print('"Size contacts" not in this table!')
                        print(next_overview_table.head())
                        continue
                    mask = next_overview_table.loc[:,'Size contacts'].isin(CONTACTS_TO_OMIT)
                    if not mask.any():
                        print(next_overview_table.loc[:,'Size contacts'])
                        overview_tables.append(next_overview_table)
                        insert_arrangement_name = extract_insert_arrangement(next_overview_table)
                        applicable_insert_arrangements.append(insert_arrangement_name)
    with open(APPLICABLE_INSERT_ARRANGEMENTS,'w') as csv_file:
        wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        wr.writerow(applicable_insert_arrangements)

with open(APPLICABLE_INSERT_ARRANGEMENTS, newline='') as file:
    reader = csv.reader(file)
    applicable_insert_arrangements = next(reader)

print(applicable_insert_arrangements)

dimension_tables = dict.fromkeys(applicable_insert_arrangements)

with pdfplumber.open(MIL_STD_PATH) as pdf:
        for page_number, page in enumerate(pdf.pages[START_PAGE:END_PAGE]):
            print('Page ' + str(page_number + START_PAGE))
            for table in page.extract_tables():
                df_table = pd.DataFrame(table)
                for insert_arrangement_name in applicable_insert_arrangements:
                    if insert_arrangement_name in df_table.to_string().lower():
                        breakpoint()
                        # the first 3 rows are not
                        # necessary
                        remove_header_rows()
                        # reshape the values as rows of 3
                        # columns
                        reshape_values()
                        # redefine the header as index, x,y
                        redefine_header()
                        # perform regex operation on values
                        # to extract mm position
                        extract_mm_positions()
                        # concatenate with existing data in
                        # the dictionary if there is any
                        combine_with_previous()
                        # sort the dataframe in the
                        # dictionary according to the index
                        # field
                        sort_with_index()
                    

# dfs = tabula.read_pdf(MIL_STD_PATH, pages=[19,25])
# print(dfs[0])