"""Test anchored growing"""
import configparser
import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipeline_elements import BASE_DIR
from anchored_growing import AnchoredGrowing


class AnchoredGrowingTester(TestCase):
    """Test anchored growing"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(BASE_DIR, 'config.ini'))
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test anchored growing run"""
        protein = os.path.join(BASE_DIR, 'tests', 'test_files', '1bty_clean.pdb')
        native_ligand = os.path.join(BASE_DIR, 'tests', 'test_files', '1bty_ligand.mol2')
        anchor = os.path.join(BASE_DIR, 'tests', 'test_files', '1bty_core.mol2')
        fragment_prefix = os.path.join(BASE_DIR, 'tests', 'test_files', 'fraglib', 'fraglib')
        anchored_growing = AnchoredGrowing(
            protein,
            native_ligand,
            anchor,
            fragment_prefix,
            self.tmp_dir.name,
            self.config
        ).run()
        self.assertTrue(os.path.exists(anchored_growing.built_molecules))

    def tearDown(self):
        self.tmp_dir.cleanup()
