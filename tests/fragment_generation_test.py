"""Test fragment generation"""
import configparser
import os
from unittest import TestCase
from tempfile import TemporaryDirectory

from pipeline_elements import BASE_DIR
from fragment_generation import FragmentGeneration


class FragmentGenerationTest(TestCase):
    """Test fragment generation"""
    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(BASE_DIR, 'config.ini'))
        self.tmp_dir = TemporaryDirectory()

    def test_run_fragment_generation(self):
        """Test fragment generation run"""
        molecules = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', 'fragments.mol2'))
        fragment_generation = FragmentGeneration(molecules, self.tmp_dir.name, self.config).run()
        self.assertTrue(os.path.exists(fragment_generation.fragment_sidechains))
        self.assertTrue(fragment_generation.output_exists())

    def tearDown(self):
        self.tmp_dir.cleanup()
