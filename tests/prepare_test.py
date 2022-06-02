"""Test preparation"""
import configparser
import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipeline_elements import BASE_DIR, Preparation


class PreparationTest(TestCase):
    """Test preparation"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(BASE_DIR, 'config.ini'))
        self.tmp_dir = TemporaryDirectory()

    def test_run_with_protein_and_ligand(self):
        """Test preparation run"""
        protein = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', '1cps.pdb'))
        ligand = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', '1cps_ligand.sdf'))
        preparation = Preparation(
            ligand,
            self.tmp_dir.name,
            self.config,
            protein=protein
        ).run()
        self.assertTrue(os.path.exists(preparation.converted_ligand))
        self.assertTrue(os.path.exists(preparation.active_site_mol2))
        self.assertTrue(os.path.exists(preparation.active_site_pdb))
        self.assertTrue(preparation.output_exists())

    def test_run_with_ligand(self):
        """Test ligand preparation"""
        ligand = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', '1cps_ligand.sdf'))
        preparation = Preparation(ligand, self.tmp_dir.name, self.config).run()
        self.assertTrue(os.path.exists(preparation.converted_ligand))
        self.assertTrue(preparation.output_exists())

    def tearDown(self):
        self.tmp_dir.cleanup()
