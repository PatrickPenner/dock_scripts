"""Protein-ligand preparation for a DOCK workflow"""
import argparse
import configparser
import logging
import os

from pipeline import PipelineElement


# intentionally sparse interface with a number of parameters
# pylint: disable=too-few-public-methods too-many-instance-attributes too-many-arguments
class Preparation(PipelineElement):
    """Protein-ligand preparation for a DOCK workflow"""

    def __init__(self, output, config, protein=None, ligand=None, name=None):
        """Protein-ligand preparation for a DOCK workflow

        Protein and ligand will be processed into a protonated active site
        of 15Å around the ligand in MOL2 format and a protonated ligand in
        MOL2 format.

        :param protein: path to the protein as PDB
        :param ligand: path to the ligand as SDF
        :param output: output directory for final and intermediate files
        :param config: config object
        """
        files = []
        if not protein and not ligand:
            raise RuntimeError('Either protein or ligand or both are required')
        if protein:
            files.append(protein)
        if ligand:
            files.append(ligand)
        PipelineElement._files_exist(files)
        self.protein = protein
        self.name = 'prepared'
        if name:
            self.name = name
        elif self.protein:
            self.name, _extension = os.path.splitext(os.path.basename(self.protein))
        self.ligand = ligand
        self.output = output
        self.config = config
        self.active_site_pdb = None
        self.active_site_mol2 = None
        self.converted_ligand = None

    def run(self):
        """Run protein-ligand preparation"""
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        if self.protein and self.ligand:
            self.protein, self.ligand = self.__run_protoss()
            self.protein = self.__clean_binding_site()
            self.active_site_pdb, self.active_site_mol2 = self.__write_active_site()
        if self.protein and not self.ligand:
            self.protein, self.ligand = self.__run_protoss()
        if self.ligand:
            self.converted_ligand = self.__convert_ligand()
        return self

    def __run_protoss(self):
        protonated_protein = os.path.join(self.output, self.name + '_h.pdb')
        protonated_ligand = None
        if self.ligand:
            protonated_ligand = os.path.join(self.output, self.name + '_ligand_h.sdf')
        args = [
            self.config['Binaries']['protoss'],
            '-i', self.protein,
            '-o', protonated_protein
        ]
        if self.ligand:
            args.extend([
                '--ligand_input', self.ligand,
                '--ligand_output', protonated_ligand
            ])
        PipelineElement._commandline(args)
        files = [protonated_protein]
        if protonated_ligand:
            files.append(protonated_ligand)
        PipelineElement._files_exist(files)
        return protonated_protein, protonated_ligand

    def __clean_binding_site(self):
        clean_protein = os.path.join(self.output, self.name + '_clean_h.pdb')
        args = [
            self.config['Binaries']['clean_binding_site'],
            '-p', self.protein,
            '-l', self.ligand,
            '-c', clean_protein
        ]
        PipelineElement._commandline(args)
        PipelineElement._files_exist([clean_protein])
        return clean_protein

    def __write_active_site(self):
        # I wrote a python script in a python script so I could write python while I write python
        active_site_pdb = os.path.join(self.output, self.name + '_active_site.pdb')
        active_site_mol2 = os.path.join(self.output, self.name + '_active_site.mol2')
        with open('templates/write_active_site.py.template') as script_template:
            script = script_template.read()
        script = script.format(
            protein=self.protein,
            ligand=self.ligand if self.ligand else '',
            radius=self.config['Parameters']['active_site_radius'],
            active_site_pdb=active_site_pdb,
            active_site_mol2=active_site_mol2
        )
        script_path = os.path.join(self.output, 'write_active_site.py')
        logging.debug(script)
        with open(script_path, 'w') as script_file:
            script_file.write(script)
        args = [
            self.config['Binaries']['chimera'],
            '--nogui',
            script_path
        ]
        PipelineElement._commandline(args)
        PipelineElement._files_exist([active_site_pdb, active_site_mol2])
        return active_site_pdb, active_site_mol2

    def __convert_ligand(self):
        converted_ligand = os.path.join(self.output, self.name + '_ligand_h.mol2')
        args = [
            self.config['Binaries']['unicon'],
            '-i', self.ligand,
            '-o', converted_ligand
        ]
        PipelineElement._commandline(args)
        PipelineElement._files_exist([converted_ligand])
        return converted_ligand


def main(args):
    """Module main to demonstrate functionality"""
    logging.basicConfig(level=logging.DEBUG)
    config = configparser.ConfigParser()
    config.read(args.config)
    preparation = Preparation(args.protein, args.ligand, args.output, config)
    preparation.run()
    print(preparation.converted_ligand)
    print(preparation.active_site_mol2)
    print(preparation.active_site_pdb)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('protein', type=str, help='path to the protein')
    parser.add_argument('ligand', type=str, help='path to the ligand')
    parser.add_argument('output', type=str, help='output directory to write prepared')
    parser.add_argument('--config', type=str, help='path to a config file', default='config.ini')
    main(parser.parse_args())
