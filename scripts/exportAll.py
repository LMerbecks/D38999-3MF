import Mesh
import os
import time
from dataclasses import dataclass

import arguably

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
INSERT_TEMPLATES = {
    'A': "9-1{gender}", 
    'B': "11-4{gender}",
    'C': "13-8{gender}", 
    'D': "15-12{gender}",
    'E': "17-18{gender}",
    'F': "19-26{gender}",
    'G': None,
    'H': None,
    'J': None
}
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

INSERT_DOCUMENTS = {
    'P': receptacle_config.document_name,
    'S': plug_config.document_name
}

INSERT_FILES = {
    'P': receptacle_config.file,
    'S': plug_config.file
}


def export_shells(config: ShellConfig)->None:

    shell_document = FreeCAD.openDocument(config.file)
    
    for keying in config.keying_options:
        print(f'Exporting {config.document_name} shells with keying {keying}...')
        start_time = time.time()
        current_output_directory = setup_output_directory(config.output_path_root, keying)
        for shell_size in config.shell_sizes:
            print(f"Shell size: {shell_size}")
            export3mf(shell_document, config, current_output_directory, keying=keying, shell_size=shell_size)
        end_time = time.time()
        print(f'\nExported {len(SHELL_SIZES)} shells. Took {(end_time-start_time):.3f}s.')


def setup_output_directory(output_path_root:str, keying:str)->str:
    """Setup a shell output directory. Generates a folder
    for the keying under the root if it does not exist. 

    Args:
        output_path_root (str): Root for the output directories
        keying (str): keying option being exported

    Returns:
        str: path to the created or computed output directory
    """
    current_output_directory = output_path_root + f'/keying_{keying}'
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
    objects = []
    for label in body_labels:
        objects_with_label = shell_document.getObjectsByLabel(label)
        if len(objects_with_label) > 1:
            raise ValueError(f'More than one object with label: {label}')
        objects.append(objects_with_label[0])
    return objects


def export_bodies(objects, export_path:str)->None:
    if hasattr(Mesh, "exportOptions"):
        options = Mesh.exportOptions(export_path)
        Mesh.export(objects, export_path, options)
    else:
        Mesh.export(objects, export_path)

def export_inserts(file_paths:str, output_root:str):

    genders = ['P', 'S']
    
    for gender in genders:
        file = file_paths[gender]
        insert_doc = FreeCAD.openDocument(file)
        output_dir = output_root + '/' + gender 
        if not os.path.exists(output_dir): 
            os.makedirs(output_dir)
        for shell in SHELL_SIZES:
            current_template = INSERT_TEMPLATES[shell]
            if current_template is None:
                continue
            export_insert(gender, insert_doc, output_dir, current_template)

def export_insert(gender, insert_doc, output_dir, current_template):
    insert_label = current_template.format(gender=gender) + "_insert"
    insert_candidates = insert_doc.getObjectsByLabel(insert_label)
    if len(insert_candidates) > 1: 
        raise ValueError(f'Multiple objects with label: {insert_label}')
    if len(insert_candidates) < 1:
        raise ValueError(f'No object with label: {insert_label}')
    insert_body = insert_candidates[0]
    bodies = [insert_body]
    export_path = output_dir + '/' + current_template.format(gender=gender) + '.3mf'
    export_bodies(bodies, export_path)

        

print('Exporting inserts...')
start = time.time()
export_inserts(INSERT_FILES, '../output/inserts')
end = time.time()
print(f'\nDone. Took {end-start:.3f}s')

print("Exporting plugs. This may take a while...")
start = time.time()
export_shells(plug_config)
end = time.time()
print(f'\nDone. Took {end-start:.3f}s')

print("\nExporting receptacles. This may take a while...")
start = time.time()
export_shells(receptacle_config)
end = time.time()
print(f'\nDone. Took {end-start:.3f}s')

