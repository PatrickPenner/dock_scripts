"""Sphere generation for DOCK workflow"""
import argparse
import configparser
import logging
import os

from pipeline import PipelineElement


# intentionally sparse interface pylint: disable=too-few-public-methods
class SphereGeneration(PipelineElement):
    """Sphere generation for DOCK workflow"""
    def __init__(self, active_site, ligand, output, config):
        """Sphere generation for DOCK workflow

        :param active_site: active site pdb file
        :param ligand: ligand mol2 file
        :param output: output directory to write files to
        :param config: config object
        """
        PipelineElement._files_exist([active_site, ligand])
        self.active_site = active_site
        self.ligand = ligand
        self.output = output
        self.config = config
        self.selected_spheres = None
        self.selected_spheres_pdb = None

    def run(self):
        """Run sphere generation"""
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        surface = self.__generate_surface()
        sphere_clusters = self.__generate_spheres(surface)
        self.selected_spheres = self.__select_spheres(sphere_clusters)
        self.selected_spheres_pdb = self.__show_spheres()

    def __generate_surface(self):
        surface = os.path.join(self.output, 'rec.ms')
        args = [
            self.config['Binaries']['dms'],
            self.active_site,
            '-n',
            '-w', str(1.4),  # probe radius
            '-v',
            '-o', surface
        ]
        PipelineElement._commandline(args)
        PipelineElement._files_exist([surface])
        return surface

    def __generate_spheres(self, surface):
        sphere_clusters = os.path.join(self.output, 'rec.sph')
        with open('templates/INSPH.template') as insph_template:
            insph = insph_template.read()
        # we will be running sphgen in the spheres directory with relative paths
        insph = insph.format(
            surface=os.path.basename(surface),
            spheres=os.path.basename(sphere_clusters)
        )
        with open(os.path.join(self.output, 'INSPH'), 'w') as insph_file:
            insph_file.write(insph)
        outsph = os.path.join(self.output, 'OUTSPH')
        # if outsph exists sphgen won't run, remove it if necessary
        if os.path.exists(outsph):
            os.remove(outsph)
            os.remove(sphere_clusters)
        PipelineElement._commandline([self.config['Binaries']['sphgen']], self.output)
        PipelineElement._files_exist([outsph, sphere_clusters])
        # logging for sphgen is written to OUTSPH, log it to debug
        with open(outsph) as outsph_file:
            logging.debug(outsph_file.read())
        return sphere_clusters

    def __select_spheres(self, sphere_clusters):
        selected_spheres = os.path.join(self.output, 'selected_spheres.sph')
        args = [
            self.config['Binaries']['sphere_selector'],
            sphere_clusters,
            self.ligand,
            self.config['Parameters']['sphere_radius']
        ]
        PipelineElement._commandline(args, cwd=self.output)
        PipelineElement._files_exist([selected_spheres])
        return selected_spheres

    def __show_spheres(self):
        selected_spheres_pdb = os.path.join(self.output, 'selected_spheres.pdb')
        with open('templates/show_spheres.in.template') as show_spheres_template:
            show_spheres = show_spheres_template.read()
        show_spheres = show_spheres.format(
            selected_spheres=self.selected_spheres,
            selected_spheres_pdb=selected_spheres_pdb
        )
        PipelineElement._commandline(
            [self.config['Binaries']['showsphere']],
            input=bytes(show_spheres, 'utf8')
        )
        PipelineElement._files_exist([selected_spheres_pdb])
        return selected_spheres_pdb


def main(args):
    """Module main to demonstrate functionality"""
    logging.basicConfig(level=logging.DEBUG)
    config = configparser.ConfigParser()
    config.read(args.config)
    spheres = SphereGeneration(args.active_site, args.ligand, args.output, config)
    spheres.run()
    print(spheres.selected_spheres)
    print(spheres.selected_spheres_pdb)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('active_site', type=str, help='path to the active site')
    parser.add_argument('ligand', type=str, help='path to the ligand')
    parser.add_argument('output', type=str, help='output directory to write spheres')
    parser.add_argument('--config', type=str, help='path to a config file', default='config.ini')
    main(parser.parse_args())
