"""Receptor Preparation for a DOCK workflow"""
import argparse
import configparser
import logging
import os

from pipeline_elements import PipelineElement, BASE_DIR, ProtossRun, Preparation, \
    SphereGeneration, GridGeneration


class ReceptorPreparation(PipelineElement):
    """Receptor Preparation for a DOCK workflow"""

    def __init__(self, protein, native_ligand, output, config):
        """Receptor Preparation for a DOCK workflow

        :param protein: protein pdb file
        :param native_ligand: native ligand sdf for active site definition
        :param output: output directory to write to
        :param config: config object
        """
        self.protein = os.path.abspath(protein)
        self.native_ligand = os.path.abspath(native_ligand)
        self.output = os.path.abspath(output)
        self.config = config
        self.__protoss_run = None
        self.__preparation = None
        self.__sphere_generation = None
        self.__grid_generation = None
        self.__build_workflow()

    def __build_workflow(self):
        protoss_dir = os.path.join(self.output, 'protoss')
        self.__protoss_run = ProtossRun(
            self.protein,
            protoss_dir,
            self.config,
            ligand=self.native_ligand
        )
        preparation_dir = os.path.join(self.output, 'prepare')
        self.__preparation = Preparation(
            self.__protoss_run.protonated_ligand,
            preparation_dir,
            self.config,
            protein=self.__protoss_run.protonated_protein
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

    @property
    def converted_ligand(self):
        """get preparation converted ligand"""
        return self.__preparation.converted_ligand

    @property
    def selected_spheres(self):
        """get sphere generation selected spheres"""
        return self.__sphere_generation.selected_spheres

    @property
    def grid_prefix(self):
        """get grid generation grid prefix"""
        return self.__grid_generation.grid_prefix

    def run(self, recalc=False):
        """Run receptor preparation

        :param recalc: recalculate all intermediate results
        """
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        logging.debug('protoss')
        if recalc or not self.__protoss_run.output_exists():
            self.__protoss_run.run()

        logging.debug('preparation')
        if recalc or not self.__preparation.output_exists():
            self.__preparation.run()

        logging.debug('sphere generation')
        if recalc or not self.__sphere_generation.output_exists():
            self.__sphere_generation.run()

        logging.debug('grid generation')
        if recalc or not self.__grid_generation.output_exists():
            self.__grid_generation.run()
        return self

    def output_exists(self):
        return self.__preparation.output_exists() \
               and self.__sphere_generation.output_exists() \
               and self.__grid_generation.output_exists()
