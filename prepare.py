"""Protein-ligand preparation for a DOCK workflow"""
import argparse
import configparser
import logging
import os

from pipeline import PipelineElement, BASE_DIR


class Preparation(PipelineElement):
    """Protein-ligand preparation for a DOCK workflow"""

    def __init__(self, ligand, output, config, protein=None, name=None):
        """Protein-ligand preparation for a DOCK workflow

        Protein and ligand will be processed into an active site of 15Å around
        the ligand in MOL2 format and a ligand in MOL2 format. If only a ligand
        is given the ligand will be converted.

        :param protein: path to the protein as PDB
        :param ligand: path to the ligand as SDF
        :param output: output directory for final and intermediate files
        :param config: config object
        """
        if not ligand:
            raise RuntimeError('Either a ligand or a protein and a ligand required')
        self.protein = os.path.abspath(protein) if protein else None
        self.name = 'prepared'
        if name:
            self.name = name
        elif self.protein:
            self.name, _extension = os.path.splitext(os.path.basename(self.protein))
        self.ligand = os.path.abspath(ligand)
        self.output = os.path.abspath(output)
        self.config = config
        self.active_site_pdb = os.path.join(self.output, self.name + '_active_site.pdb')
        self.active_site_mol2 = os.path.join(self.output, self.name + '_active_site.mol2')
        self.converted_ligand = os.path.join(self.output, self.name + '_ligand.mol2')

    def run(self, _recalc=False):
        """Run protein-ligand preparation"""
        files = [self.ligand]
        if self.protein:
            files.append(self.protein)
        PipelineElement._files_must_exist(files)
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        if self.protein and self.ligand:
            self.__write_active_site()
        self.__convert_ligand()
        return self

    def output_exists(self):
        files = [self.converted_ligand]
        if self.protein:
            files.extend([self.active_site_pdb, self.active_site_mol2])
        return PipelineElement._files_exist(files)

    def __write_active_site(self):
        # I wrote a python script in a python script so I could write python while I write python
        script_template_path = os.path.join(BASE_DIR, 'templates', 'write_active_site.py.template')
        with open(script_template_path) as script_template:
            script = script_template.read()
        script = script.format(
            protein=self.protein,
            ligand=self.ligand,
            radius=self.config['Parameters']['active_site_radius'],
            active_site_pdb=self.active_site_pdb,
            active_site_mol2=self.active_site_mol2
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
        PipelineElement._files_must_exist([self.active_site_pdb, self.active_site_mol2])

    def __convert_ligand(self):
        script_template_path = os.path.join(
            BASE_DIR,
            'templates',
            'write_converted_ligand.py.template'
        )
        with open(script_template_path) as script_template:
            script = script_template.read()
        script = script.format(
            ligand=self.ligand,
            converted_ligand=self.converted_ligand
        )
        script_path = os.path.join(self.output, 'write_converted_ligand.py')
        logging.debug(script)
        with open(script_path, 'w') as script_file:
            script_file.write(script)
        args = [
            self.config['Binaries']['chimera'],
            '--nogui',
            script_path
        ]
        PipelineElement._commandline(args)
        PipelineElement._files_must_exist([self.converted_ligand])


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
    base_config = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.ini'))
    parser.add_argument(
        '--config',
        type=str,
        help='path to a config file',
        default=os.path.join(BASE_DIR, 'config.ini')
    )
    main(parser.parse_args())
