"""DOCK de novo fragment generation"""
import argparse
import configparser
import logging
import os

from pipeline_elements import BASE_DIR, PipelineElement


class FragmentGeneration(PipelineElement):
    """DOCK de novo fragment generation"""

    def __init__(self, molecules, output, config):
        """DOCK de novo fragment generation

        :param molecules: molecules to fragment
        :param output: output directory to write fragment library
        :param config: config object
        """
        self.molecules = os.path.abspath(molecules)
        self.output = os.path.abspath(output)
        self.fragment_prefix = os.path.join(self.output, 'fraglib')
        self.fragment_torenv = self.fragment_prefix + '_torenv.dat'
        # fragments with one linker atom
        self.fragment_sidechains = self.fragment_prefix + '_sidechain.mol2'
        # fragments with two linker atoms
        self.fragment_linkers = self.fragment_prefix + '_linker.mol2'
        # fragments with three linker atoms
        self.fragment_scaffolds = self.fragment_prefix + '_scaffold.mol2'
        # fragments with no rotatable bonds and no linkers
        self.fragment_rigid = self.fragment_prefix + '_rigid.mol2'
        self.config = config

    def run(self, _recalc=False):
        """Run DOCK de novo fragment generation"""
        PipelineElement._files_must_exist([self.molecules])
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        self.__generate_fragments()
        return self

    def output_exists(self):
        return PipelineElement._files_exist(
            [self.fragment_sidechains, self.fragment_linkers, self.fragment_scaffolds,
             self.fragment_rigid, self.fragment_torenv])

    def __generate_fragments(self):
        fragmentation_template_path = os.path.join(
            BASE_DIR, 'templates', 'fragment_generation.in.template')
        with open(fragmentation_template_path) as fragmentation_template:
            fragmentation_in = fragmentation_template.read()

        fragmentation_in = fragmentation_in.format(
            molecules=os.path.relpath(self.molecules, self.output),
            fraglib_prefix=self.fragment_prefix,
            vdw=self.config['Parameters']['vdw'],
            flex=self.config['Parameters']['flex'],
            flex_drive=self.config['Parameters']['flex_drive']
        )
        logging.debug(fragmentation_in)
        fragmentation_in_path = os.path.join(self.output, 'fragment_generation.in')
        with open(fragmentation_in_path, 'w') as fragmentation_in_file:
            fragmentation_in_file.write(fragmentation_in)
        args = [
            self.config['Binaries']['dock'],
            '-i', os.path.relpath(fragmentation_in_path, self.output)
        ]
        PipelineElement._commandline(args, cwd=self.output)
        PipelineElement._files_must_exist(
            [self.fragment_sidechains, self.fragment_linkers, self.fragment_scaffolds,
             self.fragment_rigid, self.fragment_torenv])


def main(args):
    """Module main to demonstrate functionality"""
    logging.basicConfig(level=logging.DEBUG)
    config = configparser.ConfigParser()
    config.read(args.config)
    fragment_generation = FragmentGeneration(args.molecules, args.output, config)
    fragment_generation.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('molecules', type=str, help='path to the molecules to fragment')
    parser.add_argument('output', type=str, help='output directory to write fragment library')
    base_config = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.ini'))
    parser.add_argument(
        '--config',
        type=str,
        help='path to a config file',
        default=os.path.join(BASE_DIR, 'config.ini')
    )
    main(parser.parse_args())
