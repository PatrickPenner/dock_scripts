"""Test anchor generator"""
import os
from tempfile import NamedTemporaryFile
from unittest import TestCase

from pipeline_elements import BASE_DIR, AnchorGenerator


class AnchorGeneratorTest(TestCase):
    """Test anchor generator"""

    def test_run(self):
        """Test anchor generator run"""
        prepared_ligand = os.path.join(BASE_DIR, 'tests', 'test_files', '1cbx_ligand.mol2')
        template = os.path.join(BASE_DIR, 'tests', 'test_files', '1cbx_core.mol2')
        output_file = NamedTemporaryFile(suffix='anchored_dock.in')
        anchor_generator = AnchorGenerator(prepared_ligand, template, output_file.name).run()
        self.assertIn('C2,2', output_file.read().decode('utf8'))
        self.assertTrue(anchor_generator.output_exists())
        output_file.close()
