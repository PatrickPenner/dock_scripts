"""Test self docking"""
import configparser
import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipeline_elements import BASE_DIR
from self_docking import SelfDocking


class SelfDockingTest(TestCase):
    """Test self docking"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(BASE_DIR, 'config.ini'))
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test self docking run"""
        protein = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', '1cps.pdb'))
        ligand = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', '1cps_ligand.sdf'))
        self_docking = SelfDocking(protein, ligand, self.tmp_dir.name, self.config).run()
        self.assertTrue(os.path.exists(self_docking.docked))

    def test_run_with_rmsd_reference(self):
        """Test self docking run with rmsd reference"""
        protein = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', '1cps.pdb'))
        ligand = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', '1cps_ligand.sdf'))
        self_docking = SelfDocking(
            protein,
            ligand,
            self.tmp_dir.name,
            self.config,
            rmsd_reference=ligand
        ).run()
        self.assertTrue(os.path.exists(self_docking.docked))

    def tearDown(self):
        self.tmp_dir.cleanup()
