"""Test protoss run"""
import configparser
import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipeline_elements import BASE_DIR, ProtossRun


class ProtossRunTest(TestCase):
    """Test protoss run"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(BASE_DIR, 'config.ini'))
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test protoss run"""
        protein = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', '1cps.pdb'))
        ligand = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', '1cps_ligand.sdf'))
        protoss_run = ProtossRun(protein, self.tmp_dir.name, self.config, ligand=ligand).run()
        self.assertTrue(os.path.exists(protoss_run.protonated_protein))
        self.assertTrue(os.path.exists(protoss_run.protonated_ligand))
        self.assertTrue(protoss_run.output_exists())

    def tearDown(self):
        self.tmp_dir.cleanup()
