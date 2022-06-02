"""Docking use DOCK"""
import argparse
import configparser
import logging
import os

from pipeline import PipelineElement


# intentionally sparse interface pylint: disable=too-few-public-methods
class Dock(PipelineElement):
    """Docking use DOCK"""

    # prefer to explicitly list these arguments instead of putting them in config pylint: disable=too-many-arguments
    def __init__(self, ligand, spheres, grid, output, config):
        self.ligand = ligand
        self.spheres = spheres
        self.grid = grid
        self.output = output
        self.config = config
        self.docked = None

    def run(self):
        """Run docking"""
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        docked_prefix = os.path.join(self.output, 'docked')
        with open('anchor_and_grow.in.template') as dock_template:
            dock_in = dock_template.read()
        dock_in = dock_in.replace('{ligand}', self.ligand)
        dock_in = dock_in.replace('{spheres}', self.spheres)
        dock_in = dock_in.replace('{grid}', self.grid)
        dock_in = dock_in.replace('{vdw}', self.config['Parameters']['vdw'])
        dock_in = dock_in.replace('{flex}', self.config['Parameters']['flex'])
        dock_in = dock_in.replace('{flex_drive}', self.config['Parameters']['flex_drive'])
        dock_in = dock_in.replace('{docked_prefix}', docked_prefix)
        dock_in_path = os.path.join(self.output, 'dock.in')
        with open(dock_in_path, 'w') as dock_in_file:
            dock_in_file.write(dock_in)
        args = [
            self.config['Binaries']['dock'],
            '-i', dock_in_path
        ]
        PipelineElement._commandline(args)
        self.docked = docked_prefix + '_scored.mol2'


def main(args):
    """Module main to demonstrate functionality"""
    logging.basicConfig(level=logging.DEBUG)
    config = configparser.ConfigParser()
    config.read(args.config)
    dock = Dock(args.ligand, args.spheres, args.grid, args.output, config)
    dock.run()
    print(dock.docked)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ligand', type=str, help='path to the ligand')
    parser.add_argument('spheres', type=str, help='path to the spheres')
    parser.add_argument('grid', type=str, help='grid prefix')
    parser.add_argument('output', type=str, help='output directory to write docking')
    parser.add_argument('--config', type=str, help='path to a config file', default='config.ini')
    main(parser.parse_args())
