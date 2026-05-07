import pdfplumber
import pandas as pd
from pathlib import Path

import csv
import re
from tqdm import tqdm

OVERVIEW_TABLE_CHARACTERISTIC_STRING = 'shell\\nsize'
INSERT_TABLE_CHARACTERISTIC_STRING = ' {insert_arrangement_name})'

START_PAGE = 14 + 5 - 1
END_PAGE = 167 + 5 + 1

CONTACTS_TO_OMIT = ['22M', '22D', '22', '23-22']

DIMENSIONS_DIR = Path("../dimensions")
MIL_STD_PATH = DIMENSIONS_DIR / Path("MIL-STD-1560C_CHG-2.pdf")

APPLICABLE_INSERT_ARRANGEMENTS = DIMENSIONS_DIR / Path("applicable_insert_arrangements.csv")
OVERVIEW_CSV = DIMENSIONS_DIR / Path('overview.csv')

CSV_NAME_TEMPLATE = '{name}_contact_positions.csv'

overview_tables = []
applicable_insert_arrangements = []



def main():
    """The main function that hosts all the operations to
    extract the insert dimensions from the MIL-STD-1560
    standard that work for the D38999 3MF connectors.
    Exports everything to csvs. 
    First runs check if applicable insert are specified in
    `../dimensions/applicable_insert_arrangements.csv`.
    Otherwise creates it. Then uses that table to extract
    the dimensions of the specified insert arrangements.
    """
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
    export_overview_csv(dimension_tables)
    export_csvs(dimension_tables)

def find_overview_tables(page)->tuple[pd.DataFrame,str]:
    """Extract tables in the page of the standard that
    contain overview information of the insert arrangement.
    I.e. contact sizes, number of contacts, insert
    arrangement name. 

    Args:
        page (_type_): a PDF page

    Returns:
        tuple[pd.DataFrame,str]: The overview table and the
        insert name.
    """
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

def is_overview_table(table:pd.DataFrame)->bool:
    """Checks for existence of a characteristic string in a
    table that identifies the table as overview table.

    Args:
        table (pd.DataFrame): The table to test

    Returns:
        bool: True if the table is an overview table, False otherwise.
    """
    return OVERVIEW_TABLE_CHARACTERISTIC_STRING in table.to_string().lower()

def reformat_overview_table(table:pd.DataFrame)->pd.DataFrame:
    """Sets formatted header to table and reindexes the table.

    Args:
        table (pd.DataFrame): Overview table to format

    Returns:
        pd.DataFrame: The reformatted table
    """
    next_overview_table = table
    header = table.loc[0,:].fillna('').apply(lambda x: ''.join(x).replace('\n', ' '))
    next_overview_table.columns = header
    next_overview_table = next_overview_table.loc[1:].reset_index(drop=True)
    return next_overview_table

def extract_insert_arrangement(table:pd.DataFrame)->str:
    """Get the insert arrangement name in the <Shell
    size>-<Arrangement ID> format from an overview table.

    Args:
        table (pd.DataFrame): An insert overview table

    Returns:
        str: The insert arrangement name.
    """
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

def find_dimension_tables(dimension_tables:dict[str,pd.DataFrame], page)->dict[str,pd.DataFrame]:
    """Extract a table containing the dimensions for all
    contact positions from a page of the standard.

    Args:
        dimension_tables (dict[str,pd.DataFrame]): A
        dictionary containing already found and wanted
        dimension tables for insert arrangement names
        page (_type_): A pdf plumber page

    Returns:
        dict[str,pd.DataFrame]: An updated dictionary with
        dimension tables added from the page.
    """
    for table in page.extract_tables():
        df_table = pd.DataFrame(table)
        dimension_tables = extract_applicable_insert_dimensions(df_table,dimension_tables)
    return dimension_tables

def extract_applicable_insert_dimensions(table:pd.DataFrame, dimension_tables:dict[str,pd.DataFrame])->dict[str,pd.DataFrame]:
    """Extracts the dimension information for the insert
    arrangements contacts, if the table provided is a
    dimension table.

    Args:
        table (pd.DataFrame): The dimension table candidate
        dimension_tables (dict[str,pd.DataFrame]): A
        dictionary containing previously found dimension tables

    Returns:
        dict[str,pd.DataFrame]: An updated dictionary
        containing dimension tables.
    """
    for insert_arrangement_name in dimension_tables.keys():
        if is_dimension_table(table, insert_arrangement_name):
            table = remove_header_rows(table)
            triple_column_table = reshape_values(table)
            mm_dimension_table = extract_mm_positions(triple_column_table)
            dimension_tables = combine_with_previous(
                dimension_tables,
                mm_dimension_table,
                insert_arrangement_name)
    return dimension_tables

def is_dimension_table(table:pd.DataFrame, insert_arrangement_name)->bool:
    """Determines if table is a dimension table for an
    insert arrangement using a characteristic string.

    Args:
        table (pd.DataFrame): The candidate table to test
        insert_arrangement_name (_type_): The name of the
        insert this table candidate should contain
        dimensions of.

    Returns:
        bool: True if the table is a dimension table, False
        if it is not
    """
    characteristic_string = INSERT_TABLE_CHARACTERISTIC_STRING.format(insert_arrangement_name=insert_arrangement_name)
    return characteristic_string in table.to_string().lower()

def remove_header_rows(table:pd.DataFrame)->pd.DataFrame:
    """Removes the first three rows of the dimension table
    that do not contain useful information.

    Args:
        table (pd.DataFrame): The table to trim.

    Returns:
        pd.DataFrame: The trimmed table
    """
    return table.loc[3:,:]

def reshape_values(table:pd.DataFrame)->pd.DataFrame:
    """Order the table as rows of triplets and set columns
    to ID, x and y string.

    Args:
        table (pd.DataFrame): The table to rearrange

    Returns:
        pd.DataFrame: The formatted table.
    """
    triplet_values = table.to_numpy().reshape(-1,3)
    formatted_table = pd.DataFrame(triplet_values,columns=['ID','x_string', 'y_string'])
    return formatted_table

def extract_mm_positions(table:pd.DataFrame)->pd.DataFrame:
    """Convert the string dimensions in the table into mm
    float values using regex.

    Args:
        table (pd.DataFrame): The table to extract the
        positions from.

    Returns:
        pd.DataFrame: The table with only the mm position
        information left.
    """
    table['x'] = table['x_string'].apply(extract_mm)
    table['y'] = table['y_string'].apply(extract_mm)
    return table.loc[:,['ID','x','y']].dropna()

def extract_mm(dimension:str)->float:
    """Extract the mm value of a contact position from the
    string representation in imperial and metric. Uses a regex.

    Args:
        dimension (str): The dimension in string form
        containing sign, imperial value and metric value.

    Returns:
        float: The signed metric value.
    """
    regex_pattern = r'([+-]?)\d*\.?\d*\s*\(([\d*\.]+)\)'
    dimension_match = re.match(regex_pattern, dimension)
    if dimension_match:
        sign = -1 if dimension_match.group(1) == '-' else 1
        dimension_mm = float(dimension_match.group(2))
        return sign * dimension_mm

def combine_with_previous(dimension_tables:dict[str,pd.DataFrame], mm_table:pd.DataFrame, insert_name:str)->dict[str,pd.DataFrame]:
    """Combine a dimension table with a previous dimension
    table found for an insert arrangement or add a new entry
    to the dictionary if it is the first table for the
    insert arrangement.

    Args:
        dimension_tables (dict[str,pd.DataFrame]): A
        dictionary containing previous dimension tables
        mm_table (pd.DataFrame): A table with mm positions
        of contacts for an insert arrangement.
        insert_name (str): The name of the insert arrangement.

    Returns:
        dict[str,pd.DataFrame]: An updated dictionary with
        the dimension table added or appended to the
        existing one.
    """
    if dimension_tables[insert_name] is None:
        dimension_tables[insert_name] = sort_contacts(mm_table)
        return dimension_tables
    
    previous_table = dimension_tables[insert_name]
    combined_table = pd.concat([previous_table,mm_table],axis=0,ignore_index=True)
    dimension_tables[insert_name] = sort_contacts(combined_table)
    return dimension_tables

def sort_contacts(table:pd.DataFrame)->pd.DataFrame:
    """Sort the dimension table by the contact ID

    Args:
        table (pd.DataFrame): Unsorted table

    Returns:
        pd.DataFrame: Sorted table
    """
    return table.sort_values(by=['ID'])

def export_overview_csv(dimension_tables:dict[str,pd.DataFrame]):
    """Extract the number of contacts of every insert
    arrangement and export it to a csv

    Args:
        dimension_tables (dict[str,pd.DataFrame]): The
        dictionary with all dimension tables.
    """
    keys = list(dimension_tables.keys())
    overview_dict = dict.fromkeys(['Insert Arrangement Name', 'Number of contacts'])

    overview_dict['Insert Arrangement Name'] = []
    overview_dict['Number of contacts'] = []
    for key in keys:
        overview_dict['Insert Arrangement Name'].append(key)
        overview_dict['Number of contacts'].append(dimension_tables[key].shape[0])

    breakpoint()
    overview_df = pd.DataFrame(overview_dict)
    overview_df.to_csv(OVERVIEW_CSV)

def export_csvs(dimension_tables:dict[str,pd.DataFrame]):
    """Export the dimensions found.

    Args:
        dimension_tables (dict[str,pd.DataFrame]): The
        dictionary containing the dimension tables for the
        insert arrangements. 
    """
    for insert_arrangement in tqdm(dimension_tables,desc="Exporting dimensions..."):
        table = dimension_tables[insert_arrangement]
        export_path = DIMENSIONS_DIR / Path(CSV_NAME_TEMPLATE.format(name=insert_arrangement))
        table.to_csv(export_path)

main()