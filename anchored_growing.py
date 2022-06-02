"""Anchored growing using the DOCK de novo workflow"""
import argparse
import configparser
import logging
import os

from pipeline_elements import BASE_DIR, ReceptorPreparation, AnchoredDeNovo


class AnchoredGrowing:
    """Anchored growing using the DOCK de novo workflow"""

    def __init__(
            self,
            protein,
            native_ligand,
            anchor,
            fragment_prefix,
            output,
            config,
            docking_in=None,
            receptor=None
    ):
        """Anchored growing using the DOCK de novo workflow

        :param protein: protein pdb to dock into
        :param native_ligand: native ligand for active site definition
        :param anchor: anchor to grow from
        :param fragment_prefix: prefix of the fragment library to use
        :param output: output directory for final and intermediate files
        :param config: config object
        :param docking_in: DOCK input template file
        :param receptor: path to the receptor
        """
        self.protein = os.path.abspath(protein)
        self.native_ligand = os.path.abspath(native_ligand)
        self.anchor = os.path.abspath(anchor)
        self.fragment_prefix = fragment_prefix
        self.output = os.path.abspath(output)
        self.config = config
        self.docking_in = docking_in
        self.receptor = os.path.abspath(receptor) if receptor else None
        self.__receptor_preparation = None
        self.__ligand_preparation = None
        self.__anchored_de_novo = None
        self.__build_workflow()

    def __build_workflow(self):
        receptor_preparation_dir = os.path.join(self.output, 'receptor')
        if self.receptor:
            receptor_preparation_dir = self.receptor
        self.__receptor_preparation = ReceptorPreparation(
            self.protein,
            self.native_ligand,
            receptor_preparation_dir,
            self.config
        )
        de_novo_dir = os.path.join(self.output, 'denovo')
        self.__anchored_de_novo = AnchoredDeNovo(
            self.anchor,
            self.fragment_prefix,
            self.__receptor_preparation.grid_prefix,
            de_novo_dir,
            self.config,
            docking_in=self.docking_in
        )

    def run(self, recalc=False):
        """Run anchored growing

        :param recalc: recalculate all intermediate results
        """
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        logging.info('receptor preparation')
        self.__receptor_preparation.run(recalc)

        logging.info('de novo growing')
        self.__anchored_de_novo.run()

        return self

    @property
    def built_molecules(self):
        """get de novo built molecules"""
        return self.__anchored_de_novo.built_molecules


def main(args):
    """Module main to demonstrate functionality"""
    logging.basicConfig(level=logging.DEBUG)
    config = configparser.ConfigParser()
    config.read(args.config)
    anchored_de_novo = AnchoredGrowing(
        args.protein,
        args.native_ligand,
        args.anchor,
        args.fragment_prefix,
        args.output,
        config,
        docking_in=args.docking_in,
        receptor=args.receptor
    )
    anchored_de_novo.run(args.recalc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('protein', type=str, help='path to the protein')
    parser.add_argument('native_ligand', type=str, help='path to the native ligand')
    parser.add_argument('anchor', type=str, help='path to the anchor')
    parser.add_argument('fragment_prefix', type=str, help='prefix of the fragment library')
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
        '--receptor',
        type=str,
        help='path to the receptor, if it doesn\'t exist, it will be generated at this path'
    )
    main(parser.parse_args())
