"""Test rmsd analysis"""
import os
from unittest import TestCase

from pipeline_elements import BASE_DIR, RmsdAnalysis


class RmsdAnalysisTest(TestCase):
    """Test rmsd analysis"""

    def test_run(self):
        """Test rmsd analysis run"""
        docked_poses = os.path.abspath(
            os.path.join(BASE_DIR, 'tests', 'test_files', 'docked_scored.mol2'))
        rmsd_analysis = RmsdAnalysis(docked_poses).run()
        self.assertIsNotNone(rmsd_analysis.top_rmsd_s)
        self.assertIsNotNone(rmsd_analysis.top_rmsd_h)
        self.assertIsNotNone(rmsd_analysis.top_rmsd_m)
        self.assertIsNotNone(rmsd_analysis.top_rmsd)
        self.assertTrue(rmsd_analysis.output_exists())
