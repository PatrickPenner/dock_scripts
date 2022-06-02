"""Test anchored de novo"""
import configparser
import os
from unittest import TestCase
from tempfile import TemporaryDirectory

from pipeline_elements import BASE_DIR, AnchoredDeNovo


class AnchoredDeNovoTest(TestCase):
    """Test anchored de novo"""
    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(BASE_DIR, 'config.ini'))
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test anchored de novo run"""
        anchor = os.path.join(BASE_DIR, 'tests', 'test_files', '3ryx_core.mol2')
        fragment_prefix = os.path.join(BASE_DIR, 'tests', 'test_files', 'fraglib', 'fraglib')
        grid_prefix = os.path.join(BASE_DIR, 'tests', 'test_files', '3ryx_grid', 'grid')
        anchored_de_novo = AnchoredDeNovo(
            anchor,
            fragment_prefix,
            grid_prefix,
            self.tmp_dir.name,
            self.config
        ).run()
        self.assertTrue(os.path.exists(anchored_de_novo.built_molecules))
        self.assertTrue(anchored_de_novo.output_exists())

    def tearDown(self):
        self.tmp_dir.cleanup()
