import FreeCAD
import Mesh
import os
import time

from tqdm import tqdm
from dataclasses import dataclass


@dataclass
class ShellConfig:
    file: str
    document_name: str
    output_path_root: str
    output_file_template: str
    body_labels: list[str]
    part_label: str
    shell_sizes: list[str]
    keying_options: list[str]
    
SHELL_SIZES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J']

KEYING_OPTIONS = ['N', 'A', 'B', 'C', 'D', 'E']



plug_config = ShellConfig(file="../models/D38999-26AXXXXX.FCStd",
                         document_name="D38999_26AXXXXX",
                         output_path_root="../output/plugs",
                         output_file_template="D38999-26A{size}XXX{keying}",
                         body_labels=["Core", "Coupling Nut"],
                         part_label="Plug_Core",
                         shell_sizes=SHELL_SIZES,
                         keying_options=KEYING_OPTIONS)

receptacle_config = ShellConfig(file = "../models/D38999-20AXXXXX.FCStd",
                               document_name = "D38999_20AXXXXX",
                               output_path_root = "../output/wall_mount_receptacles",
                               output_file_template="D38999-20A{size}XXX{keying}",
                               body_labels = ["Core"],
                               part_label = "Receptacle_Core",
                               shell_sizes=SHELL_SIZES,
                               keying_options=KEYING_OPTIONS)

def export_shells(config: ShellConfig)->None:
    """Export shell bodys (receptacles and plugs) to 3mf.
    All combinations of keying option and shell size as
    described in the config are exported. 

    Args:
        config (ShellConfig): Export config options object
    """

    shell_document = FreeCAD.openDocument(config.file)
    
    for shell_size in tqdm(config.shell_sizes, desc=f'Exporting shell sizes',position=0):
        current_output_directory = setup_output_directory(config.output_path_root, shell_size)
        for keying in tqdm(config.keying_options, desc=f'Exporting keying options',position=1, leave=False):
            export3mf(shell_document, config, current_output_directory, keying=keying, shell_size=shell_size)


def setup_output_directory(output_path_root:str, shell_size:str)->str:
    """Setup a shell output directory. Generates a folder
    for the shell_size under the root if it does not exist. 

    Args:
        output_path_root (str): Root for the output directories
        shell_size (str): shell size being exported

    Returns:
        str: path to the created or computed output directory
    """
    current_output_directory = output_path_root + f'/{shell_size}'
    if not os.path.exists(current_output_directory):
        os.makedirs(current_output_directory)
    return current_output_directory

def export3mf(shell_document, config:ShellConfig, output_directory:str, keying:str, shell_size:str) -> None:
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
    shell_part = shell_document.getObjectsByLabel(config.part_label)
    if len(shell_part) > 1:
        raise ValueError(f"Multiple parts with label: {config.part_label}")
    if len(shell_part) < 1:
        raise ValueError(f"No object with label: {config.part_label}")
    shell_part = shell_part[0]
    set_shell_options(shell_part, keying, shell_size)
    shell_document.recompute()

    objects = gather_bodies(shell_document, config.body_labels)
    export_path = output_directory + "/" + config.output_file_template.format(size=shell_size, keying=keying) + '.3mf'
    export_bodies(objects, export_path)


def set_shell_options(shell_part, keying, shell_size):
    """Set the option of a FreeCAD shell part according to
    keying and shell size

    Args:
        shell_part (_type_): part to set configuration of
        keying (_type_): keying option
        shell_size (_type_): shell size

    Raises:
        ValueError: If keying option is not supported
        ValueError: If shell size is not supported
    """
    if keying not in KEYING_OPTIONS:
        raise ValueError(f'Unsupported keying option: {keying}')
    if shell_size not in SHELL_SIZES:
        raise ValueError(f'Unsupported shell size: {shell_size}')
    
    shell_part.Shell_Size = shell_size
    shell_part.Keying_Arrangement = build_keying_option_code(keying, shell_size)


def build_keying_option_code(keying:str, shell_size:str) -> str:
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


def gather_bodies(shell_document, body_labels: list[str])->list:
    """Gather all bodies in a FreeCAD document with
    specified labels into a set. 

    Args:
        shell_document (_type_): FreeCAD document containing bodies
        body_labels (list[str]): Body labels

    Raises:
        ValueError: If label is ambiguous

    Returns:
        list: List of the bodies
    """
    objects = []
    for label in body_labels:
        objects_with_label = shell_document.getObjectsByLabel(label)
        if len(objects_with_label) > 1:
            raise ValueError(f'More than one object with label: {label}')
        objects.append(objects_with_label[0])
    return objects


def export_bodies(objects:list[object], export_path:str)->None:
    """Export a set of bodies to a geometry file.

    Args:
        objects (list[object]): List of FreeCAD.body objects
        to export
        export_path (str): Path to export to. File extension
        determines output format.
    """
    if hasattr(Mesh, "exportOptions"):
        options = Mesh.exportOptions(export_path)
        Mesh.export(objects, export_path, options)
    else:
        Mesh.export(objects, export_path)

def main():
    tqdm.write("Exporting plugs. This may take a while...")
    export_shells(plug_config)

    tqdm.write("\nExporting receptacles. This may take a while...")
    export_shells(receptacle_config)


main()