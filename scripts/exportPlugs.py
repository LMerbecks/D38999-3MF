import Mesh
import os
import time
PLUG_FILE = "../models/D38999-26AXXXX.FCStd"
DOCUMENT_NAME = "D38999_26AXXXX"
OUTPUT_PATH = u"../output/plugs"

SHELL_SIZES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J']
KEYING_OPTIONS = ['N', 'A', 'B', 'C', 'D', 'E']

FreeCAD.openDocument(PLUG_FILE)

PLUG_DOCUMENT = FreeCAD.getDocument(DOCUMENT_NAME)

def build_keying_option(keying:str, shell_size:str) -> str:
    """Builds a keying option code from the keying option
    and the shell size by grouping the shell sizes together.

    Args:
        keying (str): keying option
        shell_size (str): shell size

    Raises:
        ValueError: If the shell size or keying option is
        not supported. 

    Returns:
        str: keying option code string
    """
    shell_groups = {
        'A': 'A',
        'B': 'BCD',
        'C': 'BCD',
        'D': 'BCD',
        'E': 'EF',
        'F': 'EF',
        'G': 'GHJ',
        'H': 'GHJ',
        'J': 'GHJ'
    }
    if shell_size not in shell_groups:
        raise ValueError(f'Unsupported shell size: {shell_size}')
    
    return f"{keying}_{shell_groups[shell_size]}"


def export3mf(output_dir:str, keying:str, shell_size:str) -> None:
    """Exports a 3mf file of a plug with the specified shell
    size and keying.

    Args:
        output_dir (str): The directory path to write the
        3mf file to. Without trailing /
        keying (str): keying option
        shell_size (str): shell size option

    Raises:
        ValueError: If keying option is unknown
        ValueError: If shell size option is unknown
    """
    
    plug_core_part = PLUG_DOCUMENT.getObjectsByLabel('Plug_Core')[0]

    if keying not in KEYING_OPTIONS:
        raise ValueError(f'Unsupported keying option: {keying}')
    if shell_size not in SHELL_SIZES:
        raise ValueError(f'Unsupported shell size: {shell_size}')
    
    plug_core_part.Shell_Size = shell_size
    plug_core_part.Keying_Arrangement = build_keying_option(keying, shell_size)

    PLUG_DOCUMENT.recompute()

    __objs__ = []
    __objs__.append(PLUG_DOCUMENT.getObjectsByLabel("Core")[0])
    __objs__.append(PLUG_DOCUMENT.getObjectsByLabel("Coupling Nut")[0])
    
    export_path = output_dir + f'/D38999-26A{shell_size}XXX{keying}.3mf'
    if hasattr(Mesh, "exportOptions"):
        options = Mesh.exportOptions(export_path)
        Mesh.export(__objs__, export_path, options)
    else:
        Mesh.export(__objs__, export_path)

    del __objs__



for shell_size in SHELL_SIZES:
    print(f'Exporting plugs with shell size {shell_size}...')
    start_time = time.time()
    current_output_directory = OUTPUT_PATH + f'/shell_size_{shell_size}'
    if not os.path.exists(current_output_directory):
        os.makedirs(current_output_directory)

    for keying in KEYING_OPTIONS:
        export3mf(output_dir=current_output_directory, keying=keying, shell_size=shell_size)
    end_time = time.time()
    print(f'\nDone! Exported {len(KEYING_OPTIONS)} plugs for shell size {shell_size}. Took {(end_time-start_time):.3f}s.')