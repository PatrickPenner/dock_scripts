"""Test sphere generation"""
import configparser
import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipeline_elements import BASE_DIR, SphereGeneration


class SphereGenerationTest(TestCase):
    """Test sphere generation"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(BASE_DIR, 'config.ini'))
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test sphere generation run"""
        active_site = os.path.abspath(
            os.path.join(BASE_DIR, 'tests', 'test_files', '1cps_h_active_site.pdb'))
        ligand = os.path.abspath(
            os.path.join(BASE_DIR, 'tests', 'test_files', '1cps_h_ligand.mol2'))
        sphere_generation = SphereGeneration(
            active_site,
            ligand,
            self.tmp_dir.name,
            self.config
        ).run()
        self.assertTrue(os.path.exists(sphere_generation.selected_spheres))
        self.assertTrue(os.path.exists(sphere_generation.selected_spheres_pdb))
        self.assertTrue(sphere_generation.output_exists())

    def tearDown(self):
        self.tmp_dir.cleanup()
