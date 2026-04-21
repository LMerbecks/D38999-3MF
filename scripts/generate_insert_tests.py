import FreeCAD
import Mesh
from pathlib import Path
from tqdm import tqdm

ARBOR_NAME = "Body001"
SLEEVE_NAME = "Body"

TEMPLATE_DOC = Path('../tests/insert_tolerance_test.FCStd')
template = FreeCAD.openDocument(str(TEMPLATE_DOC))
arbor_body = template.getObject(ARBOR_NAME)
sleeve_body = template.getObject(SLEEVE_NAME)
spreadsheet = template.Spreadsheet

EXPORT_PATH_SLEEVE = "../tests/tolerance/sleeve_{shell_size}.3mf"
EXPORT_PATH_ARBOR = "../tests/tolerance/arbor_{shell_size}_{tolerance}.3mf"

SHELL_SIZES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J']
SHELL_SIZE_ROWS = dict.fromkeys(SHELL_SIZES)
for i in range(9):
    SHELL_SIZE_ROWS[SHELL_SIZES[i]] = i+2
TOLERANCE_LEVELS = 3
TOLERANCE_COLUMNS = ['C', 'D', 'E']

def generate_sleeve(shell_size:str):
    template.Sketch.setExpression('Constraints[11]', f'Spreadsheet.B{SHELL_SIZE_ROWS[shell_size]} / 2')
    template.recompute()
    export_path = EXPORT_PATH_SLEEVE.format(shell_size=shell_size)
    if hasattr(Mesh, "exportOptions"):
        options = Mesh.exportOptions(export_path)
        Mesh.export([sleeve_body], export_path, options)
    else:
        Mesh.export([sleeve_body], export_path)

def generate_arbor(shell_size:str, tolerance_index):
    template.Sketch001.setExpression('Constraints[8]',
                                     f'Spreadsheet.B{SHELL_SIZE_ROWS[shell_size]} / 2 - Spreadsheet.{TOLERANCE_COLUMNS[tolerance_index]}{SHELL_SIZE_ROWS[shell_size]}')
    tolerance_value = spreadsheet.get(f'{TOLERANCE_COLUMNS[tolerance_index]}{SHELL_SIZE_ROWS[shell_size]}')
    tolerance_string = f'{tolerance_value:.2f}'
    tol_text = template.ShapeString
    tol_text.String = tolerance_string
    tol_text.Size = 3.0
    tol_text.Placement.Base = FreeCAD.Vector(-3.5,-1.5,5)
    template.recompute()
    export_path = EXPORT_PATH_ARBOR.format(shell_size=shell_size, tolerance=tolerance_string)
    if hasattr(Mesh, "exportOptions"):
        options = Mesh.exportOptions(export_path)
        Mesh.export([arbor_body], export_path, options)
    else:
        Mesh.export([arbor_body], export_path)

def main():
    for shell_size in tqdm(SHELL_SIZES):
        generate_sleeve(shell_size)
        for tolerance_index in tqdm(range(0,TOLERANCE_LEVELS), leave=False):
            generate_arbor(shell_size,tolerance_index)

main()

    