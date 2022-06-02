"""Grid generation for DOCK workflow"""
import argparse
import configparser
import logging
import os

from pipeline import PipelineElement, BASE_DIR


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
        grid_in = grid_in.format(
            active_site=os.path.relpath(self.active_site, self.output),
            box=os.path.relpath(box, self.output),
            vdw=self.config['Parameters']['vdw'],
            grid=os.path.relpath(self.grid_prefix, self.output)
        )
        grid_in_path = os.path.join(self.output, 'grid.in')
        with open(grid_in_path, 'w') as grid_in_file:
            grid_in_file.write(grid_in)
        args = [
            self.config['Binaries']['grid'],
            '-i', grid_in_path
        ]
        PipelineElement._commandline(args, cwd=self.output)
        PipelineElement._files_must_exist([self.energy_grid, self.bump_grid])


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
    base_config = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.ini'))
    parser.add_argument(
        '--config',
        type=str,
        help='path to a config file',
        default=os.path.join(BASE_DIR, 'config.ini')
    )
    main(parser.parse_args())
