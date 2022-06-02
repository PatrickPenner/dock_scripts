"""Grid generation for DOCK workflow"""
import argparse
import configparser
import logging
import os

from pipeline import PipelineElement


# intentionally sparse interface pylint: disable=too-few-public-methods
class GridGeneration(PipelineElement):
    """Grid generation for DOCK workflow"""

    def __init__(self, active_site, spheres, output, config):
        """Grid generation for DOCK workflow

        :param active_site: active site mol2 file
        :param spheres: selected spheres file
        :param output: output directory to write to
        :param config: config object
        """
        PipelineElement._files_exist([active_site, spheres])
        self.active_site = active_site
        self.spheres = spheres
        self.output = output
        self.config = config
        self.grid_prefix = None

    def run(self):
        """Run grid generation"""
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        box = self.__create_box()
        self.grid_prefix = self.__create_grid(box)
        return self

    def __create_box(self):
        box = os.path.join(self.output, 'box.pdb')
        with open('templates/box.in.template') as box_template:
            box_in = box_template.read()
        box_in = box_in.format(
            spheres=self.spheres,
            box=box
        )
        logging.debug(box_in)
        PipelineElement._commandline(
            [self.config['Binaries']['showbox']],
            input=bytes(box_in, 'utf8')
        )
        PipelineElement._files_exist([box])
        return box

    def __create_grid(self, box):
        grid = os.path.join(self.output, 'grid')
        with open('templates/grid.in.template') as grid_template:
            grid_in = grid_template.read()
        grid_in = grid_in.format(
            active_site=self.active_site,
            box=box,
            vdw=self.config['Parameters']['vdw'],
            grid=grid
        )
        grid_in_path = os.path.join(self.output, 'grid.in')
        with open(grid_in_path, 'w') as grid_in_file:
            grid_in_file.write(grid_in)
        args = [
            self.config['Binaries']['grid'],
            '-i', grid_in_path
        ]
        PipelineElement._commandline(args)
        PipelineElement._files_exist([grid + '.bmp', grid + '.nrg'])
        return grid


def main(args):
    """Module main to demonstrate functionality"""
    logging.basicConfig(level=logging.DEBUG)
    config = configparser.ConfigParser()
    config.read(args.config)
    grid = GridGeneration(args.active_site, args.spheres, args.output, config)
    grid.run()
    print(grid.grid_prefix)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('active_site', type=str, help='path to the active site')
    parser.add_argument('spheres', type=str, help='path to the spheres')
    parser.add_argument('output', type=str, help='output directory to write spheres')
    parser.add_argument('--config', type=str, help='path to a config file', default='config.ini')
    main(parser.parse_args())
