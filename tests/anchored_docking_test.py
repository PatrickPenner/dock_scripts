"""Test anchored docking"""
import configparser
import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipeline_elements import BASE_DIR
from anchored_docking import AnchoredDocking


class AnchoredDockingTest(TestCase):
    """Test anchored docking"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(BASE_DIR, 'config.ini'))
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test anchored docking run"""
        protein = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', '1cps.pdb'))
        native_ligand = os.path.abspath(
            os.path.join(BASE_DIR, 'tests', 'test_files', '1cps_ligand.sdf'))
        docking_ligand = os.path.abspath(
            os.path.join(BASE_DIR, 'tests', 'test_files', '1cbx_ligand.sdf'))
        template = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', '1cbx_core.mol2'))
        cross_docking = AnchoredDocking(
            protein,
            native_ligand,
            docking_ligand,
            template,
            self.tmp_dir.name,
            self.config
        ).run()
        self.assertTrue(os.path.exists(cross_docking.docked))

    def tearDown(self):
        self.tmp_dir.cleanup()
