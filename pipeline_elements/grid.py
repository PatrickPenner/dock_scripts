"""Grid generation for DOCK workflow"""
import argparse
import configparser
import logging
import os

from pipeline_elements import PipelineElement, BASE_DIR


class GridGeneration(PipelineElement):
    """Grid generation for DOCK workflow"""

    def __init__(self, active_site, spheres, output, config):
        """Grid generation for DOCK workflow

        :param active_site: active site mol2 file
        :param spheres: selected spheres file
        :param output: output directory to write to
        :param config: config object
        """
        self.active_site = os.path.abspath(active_site)
        self.spheres = os.path.abspath(spheres)
        self.output = os.path.abspath(output)
        self.config = config
        self.grid_prefix = os.path.join(self.output, 'grid')
        self.energy_grid = self.grid_prefix + '.nrg'
        self.bump_grid = self.grid_prefix + '.bmp'

    def run(self, _recalc=False):
        """Run grid generation"""
        PipelineElement._files_must_exist([self.active_site, self.spheres])
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        box = self.__create_box()
        self.__create_grid(box)
        return self

    def output_exists(self):
        return PipelineElement._files_exist([self.energy_grid, self.bump_grid])

    def __create_box(self):
        box = os.path.join(self.output, 'box.pdb')
        box_template_path = os.path.join(BASE_DIR, 'templates', 'box.in.template')
        with open(box_template_path) as box_template:
            box_in = box_template.read()
        box_in = box_in.format(
            spheres=os.path.relpath(self.spheres, self.output),
            box=os.path.relpath(box, self.output)
        )
        logging.debug(box_in)
        PipelineElement._commandline(
            [self.config['Binaries']['showbox']],
            input=bytes(box_in, 'utf8'),
            cwd=self.output
        )
        PipelineElement._files_must_exist([box])
        return box

    def __create_grid(self, box):
        grid_template_path = os.path.join(BASE_DIR, 'templates', 'grid.in.template')
        with open(grid_template_path) as grid_template:
            grid_in = grid_template.read()

        # TODO go back over all paths and check they are not longer than 80 chars
        active_site_path = os.path.relpath(self.active_site, self.output)
        if len(active_site_path) > 80:
            active_site_path = self.active_site

        grid_in = grid_in.format(
            active_site=active_site_path,
            box=os.path.relpath(box, self.output),
            vdw=self.config['Parameters']['vdw'],
            grid=os.path.relpath(self.grid_prefix, self.output)
        )
        logging.debug(grid_in)
        grid_in_path = os.path.join(self.output, 'grid.in')
        with open(grid_in_path, 'w') as grid_in_file:
            grid_in_file.write(grid_in)
        args = [
            self.config['Binaries']['grid'],
            '-i', os.path.relpath(grid_in_path, self.output)
        ]
        PipelineElement._commandline(args, cwd=self.output)
        PipelineElement._files_must_exist([self.energy_grid, self.bump_grid])
