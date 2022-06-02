"""Cross-docking using the DOCK workflow"""
import argparse
import configparser
import logging
import os

from pipeline import BASE_DIR
from prepare import Preparation
from prepare_receptor import ReceptorPreparation
from docking_run import DockingRun


class CrossDocking:
    """Cross-docking using the DOCK workflow"""

    def __init__(
            self,
            protein,
            native_ligand,
            docking_ligand,
            output,
            config,
            docking_in=None,
            rmsd_reference=None
    ):
        """Cross-docking using the DOCK workflow

        :param protein: protein pdb to dock into
        :param native_ligand: native ligand for active site definition
        :param docking_ligand: ligand to dock
        :param output: output directory for final and intermediate files
        :param config: config object
        :param docking_in: DOCK input template file
        :param rmsd_reference: reference molecule for RMSD calculation
        """
        self.protein = os.path.abspath(protein)
        self.native_ligand = os.path.abspath(native_ligand)
        self.docking_ligand = os.path.abspath(docking_ligand)
        self.output = os.path.abspath(output)
        self.config = config
        self.docking_in = docking_in
        self.rmsd_reference = os.path.abspath(rmsd_reference)
        self.__receptor_preparation = None
        self.__ligand_preparation = None
        self.__docking_run = None
        self.__build_workflow()

    def __build_workflow(self):
        receptor_preparation_dir = os.path.join(self.output, 'receptor')
        self.__receptor_preparation = ReceptorPreparation(
            self.protein,
            self.native_ligand,
            receptor_preparation_dir,
            self.config
        )
        preparation_dir = os.path.join(self.output, 'prepare')
        self.__ligand_preparation = Preparation(
            self.docking_ligand,
            preparation_dir,
            self.config,
        )
        docking_dir = os.path.join(self.output, 'dock')
        self.__docking_run = DockingRun(
            self.__ligand_preparation.converted_ligand,
            self.__receptor_preparation.selected_spheres,
            self.__receptor_preparation.grid_prefix,
            docking_dir,
            self.config,
            docking_in=self.docking_in,
            rmsd_reference=self.rmsd_reference
        )

    @property
    def docked(self):
        """get docking run docked"""
        return self.__docking_run.docked

    def run(self, recalc=False):
        """Run cross-docking

        :param recalc: recalculate all intermediate results
        """
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        logging.info('receptor preparation')
        self.__receptor_preparation.run(recalc)

        logging.info('ligand preparation')
        if recalc or not self.__ligand_preparation.output_exists():
            self.__ligand_preparation.run()

        # docking run is always rerun
        logging.info('docking')
        self.__docking_run.run()
        return self


def main(args):
    """Module main to demonstrate functionality"""
    logging.basicConfig(level=logging.DEBUG)
    config = configparser.ConfigParser()
    config.read(args.config)
    cross_docking = CrossDocking(
        args.protein,
        args.native_ligand,
        args.docking_ligand,
        args.output,
        config,
        docking_in=args.docking_in,
        rmsd_reference=args.rmsd_reference
    )
    cross_docking.run(args.recalc)
    print(cross_docking.docked)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('protein', type=str, help='path to the protein')
    parser.add_argument('native_ligand', type=str, help='path to the native ligand')
    parser.add_argument('docking_ligand', type=str, help='path to the docking ligand')
    parser.add_argument('output', type=str, help='output directory to write prepared')
    parser.add_argument(
        '--recalc',
        action='store_true',
        help='recalculate all intermediate results'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='path to a config file',
        default=os.path.join(BASE_DIR, 'config.ini')
    )
    parser.add_argument('--docking_in', type=str, help='custom docking input file for DOCK')
    parser.add_argument(
        '--rmsd_reference',
        type=str,
        help='reference molecule for RMSD calculation'
    )
    main(parser.parse_args())
