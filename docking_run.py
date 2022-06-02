"""Docking run using DOCK"""
import argparse
import configparser
import logging
import os

from pipeline import PipelineElement, BASE_DIR


class DockingRun(PipelineElement):
    """Docking run using DOCK"""

    def __init__(self, ligand, spheres, grid, output, config, docking_in=None):
        """Docking run using DOCK

        The docking input file used is either user specified with docking_in or
        an adapted FLX protocol docking input file from doi: 10.1002/jcc.23905.

        :param ligand: ligand mol2 file
        :param spheres: spheres file
        :param grid: grid prefix
        :param output: output directory to write to
        :param config: config object
        :param docking_in: DOCK input template file
        """
        self.ligand = os.path.abspath(ligand)
        self.spheres = os.path.abspath(spheres)
        self.grid = grid
        self.output = os.path.abspath(output)
        self.config = config
        self.docking_in = os.path.join(BASE_DIR, 'templates', 'FLX.in.template')
        if docking_in:
            PipelineElement._files_must_exist([docking_in])
            self.docking_in = docking_in
        self.docked_prefix = docked_prefix = os.path.join(self.output, 'docked')
        self.docked = docked_prefix + '_scored.mol2'

    def run(self, _recalc=False):
        """Run docking"""
        # grid is a prefix not a file
        PipelineElement._files_must_exist([self.ligand, self.spheres])
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        with open(self.docking_in) as dock_template:
            dock_in = dock_template.read()
        dock_in = dock_in.format(
            ligand=os.path.relpath(self.ligand, self.output),
            spheres=os.path.relpath(self.spheres, self.output),
            grid=os.path.relpath(self.grid, self.output),
            vdw=self.config['Parameters']['vdw'],
            flex=self.config['Parameters']['flex'],
            flex_drive=self.config['Parameters']['flex_drive'],
            docked_prefix=os.path.relpath(self.docked_prefix, self.output)
        )
        dock_in_path = os.path.join(self.output, 'dock.in')
        with open(dock_in_path, 'w') as dock_in_file:
            dock_in_file.write(dock_in)
        args = [
            self.config['Binaries']['dock'],
            '-i', dock_in_path
        ]
        PipelineElement._commandline(args, cwd=self.output)
        PipelineElement._files_must_exist([self.docked])
        return self

    def output_exists(self):
        return PipelineElement._files_exist([self.docked])


def main(args):
    """Module main to demonstrate functionality"""
    logging.basicConfig(level=logging.DEBUG)
    config = configparser.ConfigParser()
    config.read(args.config)
    dock = DockingRun(
        args.ligand,
        args.spheres,
        args.grid,
        args.output,
        config,
        docking_in=args.docking_in
    )
    dock.run()
    print(dock.docked)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ligand', type=str, help='path to the ligand')
    parser.add_argument('spheres', type=str, help='path to the spheres')
    parser.add_argument('grid', type=str, help='grid prefix')
    parser.add_argument('output', type=str, help='output directory to write docking')
    base_config = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.ini'))
    parser.add_argument(
        '--config',
        type=str,
        help='path to a config file',
        default=os.path.join(BASE_DIR, 'config.ini')
    )
    parser.add_argument('--docking_in', type=str, help='custom docking input file for DOCK')
    main(parser.parse_args())
