"""Sphere generation for DOCK workflow

Should be compatible with both the fortran as well as cpp sphgen
implementations.
"""
import argparse
import configparser
import logging
import os

from pipeline_elements import PipelineElement, BASE_DIR


class SphereGeneration(PipelineElement):
    """Sphere generation for DOCK workflow

    Should be compatible with both the fortran as well as cpp sphgen
    implementations.
    """

    def __init__(self, active_site, ligand, output, config):
        """Sphere generation for DOCK workflow

        Should be compatible with both the fortran as well as cpp sphgen
        implementations.

        :param active_site: active site pdb file
        :param ligand: ligand mol2 file
        :param output: output directory to write files to
        :param config: config object
        """
        self.active_site = os.path.abspath(active_site)
        self.ligand = os.path.abspath(ligand)
        self.output = os.path.abspath(output)
        self.config = config
        self.selected_spheres = os.path.join(self.output, 'selected_spheres.sph')
        self.selected_spheres_pdb = os.path.join(self.output, 'selected_spheres.pdb')

    def run(self, _recalc=False):
        """Run sphere generation"""
        PipelineElement._files_must_exist([self.active_site, self.ligand])
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        surface = self.__generate_surface()
        sphere_clusters = self.__generate_spheres(surface)
        self.__select_spheres(sphere_clusters)
        self.__show_spheres()
        return self

    def output_exists(self):
        return PipelineElement._files_exist([self.selected_spheres, self.selected_spheres_pdb])

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
        PipelineElement._files_must_exist([surface])
        return surface

    def __generate_spheres(self, surface):
        sphere_clusters = os.path.join(self.output, 'rec.sph')
        insph_template_path = os.path.join(BASE_DIR, 'templates', 'INSPH.template')
        with open(insph_template_path) as insph_template:
            insph = insph_template.read()
        # we will be running sphgen in the spheres directory with relative paths
        insph = insph.format(
            surface=os.path.relpath(surface, self.output),
            spheres=os.path.relpath(sphere_clusters, self.output)
        )
        with open(os.path.join(self.output, 'INSPH'), 'w') as insph_file:
            insph_file.write(insph)
        outsph = os.path.join(self.output, 'OUTSPH')
        # if output exists sphgen won't run, remove it if necessary
        if os.path.exists(outsph):
            os.remove(outsph)
        if os.path.exists(sphere_clusters):
            os.remove(sphere_clusters)
        PipelineElement._commandline([self.config['Binaries']['sphgen']], self.output)
        PipelineElement._files_must_exist([sphere_clusters])
        # logging for fortran sphgen is written to OUTSPH, log it to debug if it exists
        if os.path.exists(outsph):
            with open(outsph) as outsph_file:
                logging.debug(outsph_file.read())
        return sphere_clusters

    def __select_spheres(self, sphere_clusters):
        args = [
            self.config['Binaries']['sphere_selector'],
            os.path.relpath(sphere_clusters, self.output),
            self.ligand,
            self.config['Parameters']['sphere_radius']
        ]
        PipelineElement._commandline(args, cwd=self.output)
        PipelineElement._files_must_exist([self.selected_spheres])

    def __show_spheres(self):
        show_spheres_template_path = os.path.join(BASE_DIR, 'templates', 'show_spheres.in.template')
        with open(show_spheres_template_path) as show_spheres_template:
            show_spheres = show_spheres_template.read()
        show_spheres = show_spheres.format(
            selected_spheres=os.path.relpath(self.selected_spheres, self.output),
            selected_spheres_pdb=os.path.relpath(self.selected_spheres_pdb, self.output)
        )
        logging.debug(show_spheres)
        PipelineElement._commandline(
            [self.config['Binaries']['showsphere']],
            input=bytes(show_spheres, 'utf8'),
            cwd=self.output
        )
        PipelineElement._files_must_exist([self.selected_spheres_pdb])
