"""Anchored DOCK de novo run"""
import argparse
import configparser
import logging
import os

from pipeline_elements import BASE_DIR, PipelineElement


class AnchoredDeNovo(PipelineElement):
    """Anchored DOCK de novo run"""

    def __init__(self, anchor, fragment_prefix, grid_prefix, output, config, docking_in=None):
        """Anchored DOCK de novo run

        :param anchor: anchor to grow from
        :param fragment_prefix: prefix of the fragment library to use
        :param grid_prefix: grid prefix
        :param output: output directory to write anchored de novo
        :param config: config object
        :param docking_in: DOCK input template file
        """
        self.anchor = os.path.abspath(anchor)
        self.fragment_prefix = os.path.abspath(fragment_prefix)
        self.fragment_torenv = self.fragment_prefix + '_torenv.dat'
        # fragments with one linker atom
        self.fragment_sidechains = self.fragment_prefix + '_sidechain.mol2'
        # fragments with two linker atoms
        self.fragment_linkers = self.fragment_prefix + '_linker.mol2'
        # fragments with three linker atoms
        self.fragment_scaffolds = self.fragment_prefix + '_scaffold.mol2'
        # fragments with no rotatable bonds and no linkers
        self.fragment_rigid = self.fragment_prefix + '_rigid.mol2'
        self.grid_prefix = os.path.abspath(grid_prefix)
        self.output = os.path.abspath(output)
        self.config = config
        self.docking_in = os.path.join(BASE_DIR, 'templates', 'anchored_de_novo.in.template')
        if docking_in:
            self.docking_in = os.path.abspath(docking_in)
        self.built_molecules = os.path.join(self.output, 'final.denovo_build.mol2')

    def run(self, _recalc=False):
        """Run anchored de novo"""
        PipelineElement._files_must_exist([
            self.anchor,
            self.fragment_torenv,
            self.fragment_sidechains,
            self.fragment_scaffolds,
            self.fragment_rigid
        ])
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        with open(self.docking_in) as docking_in_template:
            docking_in = docking_in_template.read()
        docking_in = docking_in.format(
            anchor=self.anchor,
            linkers=self.fragment_linkers,
            scaffolds=self.fragment_scaffolds,
            sidechains=self.fragment_sidechains,
            torenv=self.fragment_torenv,
            grid=self.grid_prefix,
            vdw=self.config['Parameters']['vdw'],
            flex=self.config['Parameters']['flex'],
            flex_drive=self.config['Parameters']['flex_drive']
        )
        logging.debug(docking_in)
        docking_in_path = os.path.join(self.output, 'anchored_de_novo.in')
        with open(docking_in_path, 'w') as docking_in_file:
            docking_in_file.write(docking_in)
        args = [
            self.config['Binaries']['dock'],
            '-i', os.path.relpath(docking_in_path, self.output)
        ]
        PipelineElement._commandline(args, cwd=self.output)
        PipelineElement._files_must_exist([self.built_molecules])
        return self

    def output_exists(self):
        return PipelineElement._files_exist([self.built_molecules])
