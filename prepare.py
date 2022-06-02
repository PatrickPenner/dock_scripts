"""Protein-ligand preparation for a DOCK workflow"""
import argparse
import configparser
import logging
import os

from pipeline import PipelineElement, BASE_DIR


class Preparation(PipelineElement):
    """Protein-ligand preparation for a DOCK workflow"""

    def __init__(self, output, config, protein=None, ligand=None, name=None):
        """Protein-ligand preparation for a DOCK workflow

        Protein and ligand will be processed into a protonated active site
        of 15Å around the ligand in MOL2 format and a protonated ligand in
        MOL2 format. If only a protein is given the protein will be protonated.
        If only a ligand is given the ligand will be protonated and converted.

        :param protein: path to the protein as PDB
        :param ligand: path to the ligand as SDF
        :param output: output directory for final and intermediate files
        :param config: config object
        """
        if not protein and not ligand:
            raise RuntimeError('Either protein or ligand or both are required')
        self.protein = os.path.abspath(protein) if protein else None
        self.name = 'prepared'
        if name:
            self.name = name
        elif self.protein:
            self.name, _extension = os.path.splitext(os.path.basename(self.protein))
        self.ligand = os.path.abspath(ligand) if ligand else None
        self.output = os.path.abspath(output)
        self.config = config
        self.active_site_pdb = os.path.join(self.output, self.name + '_active_site.pdb')
        self.active_site_mol2 = os.path.join(self.output, self.name + '_active_site.mol2')
        self.converted_ligand = os.path.join(self.output, self.name + '_ligand_h.mol2')

    def run(self, _recalc=False):
        """Run protein-ligand preparation"""
        files = []
        if self.protein:
            files.append(self.protein)
        if self.ligand:
            files.append(self.ligand)
        PipelineElement._files_must_exist(files)
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        if self.protein and self.ligand:
            self.protein, self.ligand = self.__run_protoss()
            self.protein = self.__clean_binding_site()
            self.__write_active_site()
        if self.protein and not self.ligand:
            self.protein, self.ligand = self.__run_protoss()
        if self.ligand:
            self.__convert_ligand()
        return self

    def output_exists(self):
        """Get the output of the protein-ligand preparation"""
        if self.protein and self.ligand:
            return PipelineElement._files_exist(
                [self.active_site_pdb, self.active_site_mol2, self.converted_ligand]
            )
        if self.protein:
            return PipelineElement._files_exist([self.protein])
        if self.ligand:
            return PipelineElement._files_exist([self.converted_ligand])
        return False

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
        PipelineElement._files_must_exist(files)
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
        PipelineElement._files_must_exist([clean_protein])
        return clean_protein

    def __write_active_site(self):
        # I wrote a python script in a python script so I could write python while I write python
        script_template_path = os.path.join(BASE_DIR, 'templates', 'write_active_site.py.template')
        with open(script_template_path) as script_template:
            script = script_template.read()
        script = script.format(
            protein=self.protein,
            ligand=self.ligand if self.ligand else '',
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
        args = [
            self.config['Binaries']['unicon'],
            '-i', self.ligand,
            '-o', self.converted_ligand
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
