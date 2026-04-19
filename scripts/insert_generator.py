import FreeCAD
import Mesh

from pathlib import Path
import pandas as pd
import numpy as np

import pdb
from dataclasses import dataclass

SHELL_SIZES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J']
CIVIL_TO_MIL_SHELL_SIZES = {'9': 'A', '11': 'B', '13': 'C', '15': 'D',
                             '17': 'E', '19': 'F', '21': 'G', '23': 'H', '25': 'J'}

DOMAIN_3MF = '.3mf'
DEFAULT_OUTPUT_DIR = '../output/inserts'
DEFAULT_DIMENSIONS_DIR = '../dimensions'

BOOLEAN_CUT_CODE = 1
TOOL_BODY_ID = 'Body'
PIN_INSERT_DOCUMENT_NAME = Path('../models/PinInserts.FCStd')
if Path.exists(PIN_INSERT_DOCUMENT_NAME):
    PIN_INSERT_DOCUMENT = FreeCAD.openDocument(str(PIN_INSERT_DOCUMENT_NAME))

SOCKET_INSERT_DOCUMENT_NAME = Path('../models/SocketInserts.FCStd')
if Path.exists(SOCKET_INSERT_DOCUMENT_NAME):
    SOCKET_INSERT_DOCUMENT = FreeCAD.openDocument(str(SOCKET_INSERT_DOCUMENT_NAME))

USE_ALL_CONFIGS = False

ARRANGEMENT_CONFIGURATIONS = ["9-3_contact_positions.csv", 
                              "11-2_contact_positions.csv",
                              "11-4_contact_positions.csv",
                              "11-5_contact_positions.csv"]
if USE_ALL_CONFIGS:
    ARRANGEMENT_CONFIGURATIONS = []

DUMMY_LABEL_TEMPLATE = "Size{shell_size}InsertDummy"

@dataclass
class InsertFactory():

    gender: str
    output_dir: Path=Path(DEFAULT_OUTPUT_DIR)
    dimensions_dir: Path=Path(DEFAULT_DIMENSIONS_DIR)

    def __post_init__(self):
        if self.gender != 'P' and self.gender != 'S':
            raise ValueError(f"Gender must be any of ['P','S'] not {self.gender}")
        if self.gender == 'P':
            self.root_document = PIN_INSERT_DOCUMENT
        if self.gender == 'S':
            self.root_document = SOCKET_INSERT_DOCUMENT

    def generate_insert(self, arrangement_config: Path):
        arrangement_csv = self.dimensions_dir / arrangement_config
        shell_size, contact_positions = self.parse_arrangement_csv(arrangement_csv)
        tool_body = self.get_contact_tool_body()
        insert_dummy = self.get_insert_dummy(shell_size)
        insert_identifier = self.extract_insert_name(arrangement_config)
        insert_body = self.clone_body(insert_dummy, insert_identifier)
        contact_tools = []

        for index, contact in enumerate(contact_positions):
            current_identifier = f'contact_tool_{index}'
            current_contact_tool = self.clone_body(tool_body, current_identifier)
            contact_x = contact[0]
            contact_y = contact[1]
            self.translate_contact_tool(current_contact_tool, contact_x, contact_y)
            contact_tools.append(current_contact_tool)
        
        self.create_contact_cutouts(insert_body, contact_tools)
        self.export_insert(insert_body, insert_identifier)

    def parse_arrangement_csv(self,csv_filename:Path)->tuple[str, np.array]:
        file_name = csv_filename.stem
        shell_size = file_name.split('-')[0]
        positions = self.get_contact_positions(csv_filename)
        if self.gender == 'S':
            positions = self.invert_positions(positions)
            return CIVIL_TO_MIL_SHELL_SIZES[shell_size], positions
        return CIVIL_TO_MIL_SHELL_SIZES[shell_size], positions
    
    def get_contact_positions(self, csv_filename:Path)->np.array:
        """Parse a csv containing the x and y positions of
        the contacts as noted when looking at the front face
        of the pin insert (!). Includes transform into the
        x-z coordinate frame of the FreeCAD Document. 

        Args:
            csv_filename (Path): Path to csv containing x
            and y columns

        Returns:
            np.array: Array containing the x and z positions
            of all contacts in FreeCAD Document global 
            coordinates. Each row is one contact.
        """
        positions = pd.read_csv(csv_filename)
        if not ('x' in positions.columns and 'y' in positions.columns):
            raise ValueError("CSV needs to have x and y columns!")

        positions = positions.loc[:,['x','y']].values
        return positions

    def invert_positions(self,pin_contact_positions:np.array)->np.array:
        """Mirror the contact positions along the z axis.

        Args:
            pin_contact_positions (np.array): original
            positions of the pin contacts

        Returns:
            np.array: socket contact positions in x and z
        """
        pin_contact_positions[:,0] = -1 * pin_contact_positions[:,0] 
        return pin_contact_positions

    def get_contact_tool_body(self)->None:
        """Gets the contact tool body in the current
        document. The body identified by the string in
        TOOL_BODY_ID.

        Returns:
            None: Body object of the contact tool
        """
        return self.root_document.getObject(TOOL_BODY_ID)

    def get_insert_dummy(self,shell_size: str)->None:
        """Gets the correct insert dummy (or template) body
        for a given shell size.

        Args:
            shell_size (str): The size of the shell the
            insert is for. One of A to H and J

        Raises:
            ValueError: If more or less than one dummy is found

        Returns:
            None: The dummy insert body
        """
        if shell_size not in SHELL_SIZES:
            raise ValueError(f'{shell_size} is not a valid shell size: {SHELL_SIZES}')
        dummy_label = DUMMY_LABEL_TEMPLATE.format(shell_size=shell_size)
        dummy_body_candidates = self.root_document.getObjectsByLabel(dummy_label)
        if len(dummy_body_candidates) != 1:
            raise ValueError(f"{len(dummy_body_candidates)} Bodies found for {shell_size}!")
        return dummy_body_candidates[0]

    def clone_body(self, original_body, identifier:str)->None:
        """Wraps the FreeCAD operations for cloning a body.
        

        Args:
            original_body (Body): The body that should be cloned
            identifier (str): A unique (!) identifier for
            the new body

        Returns:
            None: The cloned body
        """
        cloned_body = self.root_document.addObject('PartDesign::Body', identifier)
        clone_feature = self.root_document.addObject('PartDesign::FeatureBase', identifier + 'Clone')
        cloned_body.Group = [clone_feature]
        cloned_body.Tip = clone_feature
        cloned_body.AllowCompound = False
        clone_feature.BaseFeature = original_body
        clone_feature.Placement = original_body.Placement
        clone_feature.setEditorMode('Placement', 0)
        return cloned_body

    def translate_contact_tool(self,tool_body, x:float, z:float)->None:
        """Translate a contact fixture tool body in the x-z
        plane. 

        Args:
            tool_body : FreeCAD object of the tool body to
            be moved
            x (float): x position of the tool after
            translation 
            z (float): z position of the tool after translation
        """
        position_vector = FreeCAD.Vector(0, x, z)
        euler_angles = FreeCAD.Rotation(0, 0, 0)
        rotation_axis = FreeCAD.Vector(0,0,0)
        new_placement = FreeCAD.Placement(position_vector, euler_angles, rotation_axis)
        tool_body.Placement = new_placement

    def create_contact_cutouts(self,insert_base_body:None, contact_tools:list[None]):
        """Create the final insert body by cutting away all
        the contact bodies.

        Args:
            insert_base_body (None): The base body
            of the insert. This should be a clone of the template
            contact_tools (list): A list of the contact
            fixture tool bodies at the appropriate positions
        """
        boolean_identifier = insert_base_body.Name + 'Boolean' # I assume the Name is unique
        boolean_feature = insert_base_body.newObject('PartDesign::Boolean',boolean_identifier)
        boolean_feature.setObjects(contact_tools)
        boolean_feature.Type = BOOLEAN_CUT_CODE
    
    def extract_insert_name(self, arrangement_name:str)->str:
        """Takes the arrangement contact position file name
        and uses it to define the insert name. The insert
        name should constitute the characters up to the
        first underscore.

        Args:
            arrangement_name (str): filename of the csv

        Returns:
            str: insert name
        """
        insert_name = str(arrangement_name).split('_')[0]
        return insert_name
    
    def export_insert(self, insert_body, insert_identifier:str):
        """Recomputes the document and then exports the
        specified body to 3mf under the insert identifier
        name. The file is written to a subfolder specified
        by the gender of the insert. 

        Args:
            insert_body (): The body
            containing the geometry to be exported
            insert_identifier (str): The identifier of the
            exported body
        """
        self.root_document.recompute()
        #TODO: make this export to shell size directories
        #instead and insert the gender into the filename.
        shell_size = insert_identifier.split('-')[0]
        mil_shell_size = CIVIL_TO_MIL_SHELL_SIZES[shell_size]
        export_directory = self.output_dir / mil_shell_size
        if not export_directory.exists():
            export_directory.mkdir()
        export_path = export_directory / (insert_identifier + self.gender + DOMAIN_3MF)
        export_path = str(export_path)

        if hasattr(Mesh, "exportOptions"):
            options = Mesh.exportOptions(export_path)
            Mesh.export([insert_body], export_path, options)
        else:
            Mesh.export([insert_body], export_path)
        

def main():
    pin_insert_factory = InsertFactory('P')
    socket_insert_factory = InsertFactory('S')
    for arrangement in ARRANGEMENT_CONFIGURATIONS:
        pin_insert_factory.generate_insert(Path(arrangement))
        socket_insert_factory.generate_insert(Path(arrangement))



if __name__ == 'insert_generator':
    main()