"""Test receptor preparation"""
import configparser
import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipeline_elements import BASE_DIR, ReceptorPreparation


class ReceptorPreparationTest(TestCase):
    """Test receptor preparation"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(BASE_DIR, 'config.ini'))
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test receptor preparation run"""
        protein = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', '1cps.pdb'))
        ligand = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', '1cps_ligand.sdf'))
        receptor_preparation = ReceptorPreparation(
            protein,
            ligand,
            self.tmp_dir.name,
            self.config
        ).run()
        self.assertTrue(os.path.exists(receptor_preparation.converted_ligand))
        self.assertTrue(os.path.exists(receptor_preparation.selected_spheres))
        self.assertTrue(receptor_preparation.output_exists())

    def tearDown(self):
        self.tmp_dir.cleanup()
