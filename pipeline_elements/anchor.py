"""Anchor generator for a DOCK workflow"""
import os
import re

from pipeline_elements import PipelineElement, BASE_DIR


class AnchorGenerator(PipelineElement):
    """Anchor generator for a DOCK workflow

    The anchor is the only bond bound to a linker atom. The anchor generator
    finds the anchor atom of a template in a ligand mol2 file based on string
    equality of the coordinates. This is such a bad idea but it works.
    """
    def __init__(self, ligand, template, output_file, docking_in=None):
        """Anchor generator for a DOCK workflow

        :param ligand: ligand to anchor
        :param template: template containing a linker which denotes the anchore
        :param output_file: docking input file with anchor records for DOCK
        :param docking_in: custom input docking file
        """
        self.ligand = ligand
        self.template = template
        self.output_file = output_file
        self.anchored_docking_in = os.path.join(BASE_DIR, 'templates', 'FAD.in.template')
        if docking_in:
            self.anchored_docking_in = docking_in

    def run(self, _recalc=False):
        """Run anchor generation"""
        PipelineElement._files_must_exist([self.ligand, self.template, self.anchored_docking_in])
        ligand_atom_records, _ligand_bond_records = self.__read_atoms_and_bonds(self.ligand)
        template_atom_records, template_bond_records = self.__read_atoms_and_bonds(self.template)
        anchor_atom_record = AnchorGenerator.__get_anchor_atom_record(
            template_atom_records,
            template_bond_records
        )
        ligand_anchor_atom_record = AnchorGenerator.__get_corresponding_atom_record(
            anchor_atom_record,
            ligand_atom_records
        )
        anchor = ligand_anchor_atom_record[1] + ',' + ligand_anchor_atom_record[0]

        with open(self.anchored_docking_in) as anchored_docking_template:
            anchored_docking = anchored_docking_template.read()
        if '{anchor}' not in anchored_docking:
            raise RuntimeError('Docking input file does not support anchored docking')
        # have to use replace because format() demands all keys be present
        anchored_docking = anchored_docking.replace('{anchor}', anchor)
        with open(self.output_file, 'w') as output_file:
            output_file.write(anchored_docking)
        return self

    @staticmethod
    def __parse_record(line):
        """Strip whitespace an split into columns"""
        stripped_line = re.sub(r'\s+', ' ', line)
        return [x for x in stripped_line.split(' ') if x.strip()]

    @staticmethod
    def __read_atoms_and_bonds(mol_file_path):
        """Read atom and bond records from a mol2 file"""
        atom_record = []
        bond_record = []
        with open(mol_file_path) as prepared_file:
            in_atom_block = False
            in_bond_block = False
            for line in prepared_file:
                if in_bond_block:
                    if '@' in line or not line.strip():
                        in_bond_block = False
                    else:
                        bond_record.append(AnchorGenerator.__parse_record(line))

                if in_atom_block:
                    if '@<TRIPOS>BOND' in line:
                        in_atom_block = False
                        in_bond_block = True
                    else:
                        atom_record.append(AnchorGenerator.__parse_record(line))

                if '@<TRIPOS>ATOM' in line:
                    in_atom_block = True
        return atom_record, bond_record

    @staticmethod
    def __get_anchor_atom_record(atom_records, bond_records):
        """Get the anchor atom record"""
        dummy_atomnum = None  # first find the linker atom record
        for atom_record in atom_records:
            if atom_record[5] == 'Du':
                if dummy_atomnum:
                    raise RuntimeError('Found multiple linkers')
                dummy_atomnum = atom_record[0]
        anchor_atomnum = None  # find the anchor atom number from the bond record to the linker
        for bond_record in bond_records:
            if bond_record[1] == dummy_atomnum:
                if anchor_atomnum:
                    raise RuntimeError('Found multiple bonds to linker')
                anchor_atomnum = bond_record[2]
            if bond_record[2] == dummy_atomnum:
                if anchor_atomnum:
                    raise RuntimeError('Found multiple bonds to linker')
                anchor_atomnum = bond_record[1]
        return atom_records[int(anchor_atomnum) - 1]  # atom number is 1 indexed

    @staticmethod
    def __get_corresponding_atom_record(query_atom_record, atom_records):
        """Get corresponding atom record with equal coordinates"""
        found_atom_record = None
        for atom_record in atom_records:
            if query_atom_record[2:5] == atom_record[2:5]:  # coordinate comparison
                if found_atom_record:
                    raise RuntimeError('Found multiple corresponding atom records')
                found_atom_record = atom_record
        return found_atom_record

    def output_exists(self):
        return PipelineElement._files_exist([self.output_file])
