import argparse
import configparser
import logging
import os

from pipeline import PipelineElement, BASE_DIR


class ProtossRun(PipelineElement):

    def __init__(self, protein, output, config, ligand=None):
        if not protein:
            raise RuntimeError('Protein is required')
        self.protein = protein
        self.ligand = ligand
        self.output = output
        self.config = config
        self.name, _extension = os.path.splitext(os.path.basename(self.protein))
        self.protonated_protein = os.path.join(self.output, self.name + '_h.pdb')
        self.protonated_ligand = os.path.join(self.output, self.name + '_h_ligand.sdf')

    def run(self, _recalc=False):
        files = [self.protein]
        if self.ligand:
            files.append(self.ligand)
        PipelineElement._files_must_exist(files)
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        self.__run_protoss()
        self.__clean_binding_site()
        return self

    def __run_protoss(self):
        args = [
            self.config['Binaries']['protoss'],
            '-i', self.protein,
            '-o', self.protonated_protein
        ]
        if self.ligand:
            args.extend([
                '--ligand_input', self.ligand,
                '--ligand_output', self.protonated_ligand
            ])
        PipelineElement._commandline(args)
        files = [self.protonated_protein]
        if self.ligand:
            files.append(self.protonated_ligand)
        PipelineElement._files_must_exist(files)

    def __clean_binding_site(self):
        args = [
            self.config['Binaries']['clean_binding_site'],
            '-p', self.protonated_protein,
            '-l', self.protonated_ligand,
            '-c', self.protonated_protein
        ]
        PipelineElement._commandline(args)
        PipelineElement._files_must_exist([self.protonated_protein])

    def output_exists(self):
        return PipelineElement._files_exist([self.protonated_protein, self.protonated_ligand])


def main(args):
    """Module main to demonstrate functionality"""
    logging.basicConfig(level=logging.DEBUG)
    config = configparser.ConfigParser()
    config.read(args.config)
    protoss_run = ProtossRun(args.protein, args.output, config, ligand=args.ligand)
    protoss_run.run()
    print(protoss_run.protonated_protein)
    print(protoss_run.protonated_ligand)


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
