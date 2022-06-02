"""Test cross docking"""
import configparser
import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipeline_elements import BASE_DIR
from cross_docking import CrossDocking


class CrossDockingTest(TestCase):
    """Test cross docking"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(BASE_DIR, 'config.ini'))
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test cross docking run"""
        protein = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', '1cps.pdb'))
        native_ligand = os.path.abspath(
            os.path.join(BASE_DIR, 'tests', 'test_files', '1cps_ligand.sdf'))
        docking_ligand = os.path.abspath(
            os.path.join(BASE_DIR, 'tests', 'test_files', '1cbx_ligand.sdf'))
        cross_docking = CrossDocking(
            protein,
            native_ligand,
            docking_ligand,
            self.tmp_dir.name,
            self.config
        ).run()
        self.assertTrue(os.path.exists(cross_docking.docked))

    def tearDown(self):
        self.tmp_dir.cleanup()
