"""Test grid generation"""
import configparser
import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipeline_elements import BASE_DIR, GridGeneration


class GridGenerationTest(TestCase):
    """Test grid generation"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(BASE_DIR, 'config.ini'))
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test grid generation run"""
        active_site = os.path.abspath(
            os.path.join(BASE_DIR, 'tests', 'test_files', '1cps_h_active_site.mol2'))
        selected_spheres = os.path.abspath(
            os.path.join(BASE_DIR, 'tests', 'test_files', 'selected_spheres.sph'))
        grid_generation = GridGeneration(
            active_site,
            selected_spheres,
            self.tmp_dir.name,
            self.config
        ).run()
        self.assertTrue(os.path.exists(grid_generation.energy_grid))
        self.assertTrue(os.path.exists(grid_generation.bump_grid))
        self.assertTrue(grid_generation.output_exists())

    def tearDown(self):
        self.tmp_dir.cleanup()
