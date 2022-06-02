"""Perform protonation using protoss"""
import argparse
import configparser
import logging
import os

from pipeline_elements import PipelineElement, BASE_DIR


class ProtossRun(PipelineElement):
    """Perform protonation using protoss"""

    def __init__(self, protein, output, config, ligand=None):
        """Perform protonation using protoss

        :param protein: path to the protein as PDB
        :param output: output directory for final and intermediate files
        :param config: config object
        :param ligand: path to the ligand as SDF
        """
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
        """Run protoss protonation"""
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
