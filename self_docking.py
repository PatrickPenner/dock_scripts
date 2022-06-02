"""Self-docking using the DOCK workflow"""
import argparse
import configparser
import logging
import os

from prepare_receptor import ReceptorPreparation
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
        self.__receptor_preparation = None
        self.__docking_run = None
        self.__build_workflow()

    def __build_workflow(self):
        preparation_dir = os.path.join(self.output, 'receptor')
        self.__receptor_preparation = ReceptorPreparation(
            self.protein,
            self.ligand,
            preparation_dir,
            self.config
        )
        docking_dir = os.path.join(self.output, 'dock')
        self.__docking_run = DockingRun(
            self.__receptor_preparation.converted_ligand,
            self.__receptor_preparation.selected_spheres,
            self.__receptor_preparation.grid_prefix,
            docking_dir,
            self.config
        )

    @property
    def docked(self):
        """get docking run docked"""
        return self.__docking_run.docked

    def run(self, recalc=False):
        """Run self-docking

        :param recalc: recalculate all intermediate results
        """
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        logging.info('receptor preparation')
        self.__receptor_preparation.run(recalc)

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
