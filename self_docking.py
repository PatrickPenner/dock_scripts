"""Self-docking using the DOCK workflow"""
import argparse
import configparser
import logging
import os

from prepare import Preparation
from spheres import SphereGeneration
from grid import GridGeneration
from docking_run import DockingRun


class SelfDocking:
    """Self-docking using the DOCK workflow"""

    def __init__(self, protein, ligand, output, config):
        """Self-docking using the DOCK workflow

        :param protein: protein pdb to dock into
        :param ligand: both ligand for active site definition and ligand to dock
        :param output: output directory for final and intermediate files
        :param config: config object
        """
        self.protein = protein
        self.ligand = ligand
        self.output = output
        self.config = config
        self.docked = None
        self.__preparation = None
        self.__sphere_generation = None
        self.__grid_generation = None
        self.__docking_run = None
        self.__build_workflow()

    def __build_workflow(self):
        preparation_dir = os.path.join(self.output, 'prepare')
        self.__preparation = Preparation(
            preparation_dir,
            self.config,
            protein=self.protein,
            ligand=self.ligand
        )
        sphere_generation_dir = os.path.join(self.output, 'spheres')
        self.__sphere_generation = SphereGeneration(
            self.__preparation.active_site_pdb,
            self.__preparation.converted_ligand,
            sphere_generation_dir,
            self.config
        )
        grid_generation_dir = os.path.join(self.output, 'grid')
        self.__grid_generation = GridGeneration(
            self.__preparation.active_site_mol2,
            self.__sphere_generation.selected_spheres,
            grid_generation_dir,
            self.config
        )
        docking_dir = os.path.join(self.output, 'dock')
        self.__docking_run = DockingRun(
            self.__preparation.converted_ligand,
            self.__sphere_generation.selected_spheres,
            self.__grid_generation.grid_prefix,
            docking_dir,
            self.config
        )
        self.docked = self.__docking_run.docked

    def run(self, recalc=False):
        """Run self-docking

        :param recalc: recalculate all intermediate results
        """
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        logging.info('preparation')
        if recalc or not self.__preparation.output_exists():
            self.__preparation.run()

        logging.info('sphere generation')
        if recalc or not self.__sphere_generation.output_exists():
            self.__sphere_generation.run()

        logging.info('grid generation')
        if recalc or not self.__grid_generation.output_exists():
            self.__grid_generation.run()

        # docking run is always rerun
        logging.info('docking')
        self.__docking_run.run()
        return self


def main(args):
    """Module main to demonstrate functionality"""
    logging.basicConfig(level=logging.DEBUG)
    config = configparser.ConfigParser()
    config.read(args.config)
    self_docking = SelfDocking(args.protein, args.ligand, args.output, config).run(args.recalc)
    print(self_docking.docked)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('protein', type=str, help='path to the protein')
    parser.add_argument('ligand', type=str, help='path to the ligand')
    parser.add_argument('output', type=str, help='output directory to write prepared')
    parser.add_argument(
        '--recalc',
        action='store_true',
        help='recalculate all intermediate results'
    )
    parser.add_argument('--config', type=str, help='path to a config file', default='config.ini')
    main(parser.parse_args())
