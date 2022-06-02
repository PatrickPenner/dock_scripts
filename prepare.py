"""Protein-ligand preparation for a DOCK workflow"""
import argparse
import configparser
import logging
import os
import subprocess


class Preparation:  # intentionally sparse interface pylint: disable=too-few-public-methods
    """Protein-ligand preparation for a DOCK workflow"""

    def __init__(self, protein, ligand, output, config):
        """Protein-ligand preparation for a DOCK workflow

        Protein and ligand will be processed into a protonated active site
        of 15Å around the ligand in MOL2 format and a protonated ligand in
        MOL2 format.

        :param protein: path to the protein as PDB
        :param ligand: path to the ligand as SDF
        :param output: output directory for final and intermediate files
        :param config: config object
        """
        self.protein = protein
        self.pdb, _extension = os.path.splitext(os.path.basename(self.protein))
        self.ligand = ligand
        self.output = output
        self.config = config
        self.active_site = None
        self.converted_ligand = None

    def run(self):
        """Run protein-ligand preparation

        :return: active_site_path, converted_ligand_path
        """
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        protonated_protein, protonated_ligand = self.__run_protoss()
        clean_protein = self.__clean_binding_site(protonated_protein)
        self.active_site = self.__write_active_site(clean_protein)
        self.converted_ligand = self.__convert_ligand(protonated_ligand)
        return self.active_site, self.converted_ligand

    def __run_protoss(self):
        protonated_protein = os.path.join(self.output, self.pdb + '_h.pdb')
        protonated_ligand = os.path.join(self.output, self.pdb + '_ligand_h.sdf')
        args = [
            self.config['Binaries']['protoss'],
            '-i', self.protein,
            '--ligand_input', self.ligand,
            '-o', protonated_protein,
            '--ligand_output', protonated_ligand
        ]
        logging.debug('running: %s', ' '.join(args))
        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        if output:
            logging.debug(output.decode('utf8'))
        return protonated_protein, protonated_ligand

    def __clean_binding_site(self, protonated_protein):
        clean_protein = os.path.join(self.output, self.pdb + '_clean_h.pdb')
        args = [
            self.config['Binaries']['clean_binding_site'],
            '-p', protonated_protein,
            '-l', self.ligand,
            '-c', clean_protein
        ]
        logging.debug('running: %s', ' '.join(args))
        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        if output:
            logging.debug(output.decode('utf8'))
        return clean_protein

    def __write_active_site(self, clean_protein):
        # I wrote a python script in a python script so I could write python while I write python
        active_site = os.path.join(self.output, self.pdb + '_active_site.mol2')
        with open('write_active_site.template.py') as script_template:
            script = script_template.read()
        script = script.replace('{protein}', clean_protein)
        script = script.replace('{ligand}', self.ligand)
        script = script.replace('{active_site}', active_site)
        script_path = os.path.join(self.output, 'write_active_site.py')
        logging.debug(script)
        with open(script_path, 'w') as script_file:
            script_file.write(script)
        args = [
            self.config['Binaries']['chimera'],
            '--nogui',
            script_path
        ]
        logging.debug('running: %s', ' '.join(args))
        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        if output:
            logging.debug(output.decode('utf8'))
        return active_site

    def __convert_ligand(self, protonated_ligand):
        converted_ligand = os.path.join(self.output, self.pdb + '_ligand_h.mol2')
        args = [
            self.config['Binaries']['unicon'],
            '-i', protonated_ligand,
            '-o', converted_ligand
        ]
        logging.debug('running: %s', ' '.join(args))
        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        if output:
            logging.debug(output.decode('utf8'))
        return converted_ligand


def main(args):
    """Module main to demonstrate functionality"""
    logging.basicConfig(level=logging.DEBUG)
    config = configparser.ConfigParser()
    config.read(args.config)
    preparation = Preparation(args.protein, args.ligand, args.output, config)
    preparation.run()
    print(preparation.active_site)
    print(preparation.converted_ligand)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('protein', type=str, help='path to the protein')
    parser.add_argument('ligand', type=str, help='path to the ligand')
    parser.add_argument('output', type=str, help='output directory to write prepared')
    parser.add_argument('--config', type=str, help='path to a config file', default='config.ini')
    main(parser.parse_args())
