"""Test docking run"""
import configparser
import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipeline_elements import BASE_DIR, DockingRun


class DockingRunTest(TestCase):
    """Test docking run"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(BASE_DIR, 'config.ini'))
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test docking run"""
        ligand = os.path.abspath(
            os.path.join(BASE_DIR, 'tests', 'test_files', '1cps_h_ligand.mol2'))
        selected_spheres = os.path.abspath(
            os.path.join(BASE_DIR, 'tests', 'test_files', 'selected_spheres.sph'))
        grid_prefix = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', 'grid'))
        docking_run = DockingRun(
            ligand,
            selected_spheres,
            grid_prefix,
            self.tmp_dir.name,
            self.config
        ).run()
        self.assertTrue(os.path.exists(docking_run.docked))
        self.assertTrue(docking_run.output_exists())

    def test_run_with_custom_docking_in(self):
        """Test docking run with a custom input file"""
        ligand = os.path.abspath(
            os.path.join(BASE_DIR, 'tests', 'test_files', '1cps_h_ligand.mol2'))
        selected_spheres = os.path.abspath(
            os.path.join(BASE_DIR, 'tests', 'test_files', 'selected_spheres.sph'))
        grid_prefix = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', 'grid'))
        docking_in = os.path.abspath(
            os.path.join(BASE_DIR, 'tests', '../templates', 'FLX.in.template'))
        docking_run = DockingRun(
            ligand,
            selected_spheres,
            grid_prefix,
            self.tmp_dir.name,
            self.config,
            docking_in=docking_in
        ).run()
        self.assertTrue(os.path.exists(docking_run.docked))
        self.assertTrue(docking_run.output_exists())

    def test_run_with_rmsd_reference(self):
        """Test docking run with RMSD reference molecule"""
        ligand = os.path.abspath(
            os.path.join(BASE_DIR, 'tests', 'test_files', '1cps_h_ligand.mol2'))
        selected_spheres = os.path.abspath(
            os.path.join(BASE_DIR, 'tests', 'test_files', 'selected_spheres.sph'))
        grid_prefix = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'test_files', 'grid'))
        docking_run = DockingRun(
            ligand,
            selected_spheres,
            grid_prefix,
            self.tmp_dir.name,
            self.config,
            rmsd_reference=ligand
        ).run()
        self.assertTrue(os.path.exists(docking_run.docked))
        self.assertTrue(docking_run.output_exists())
        with open(docking_run.docked) as docked_ligands:
            docked_ligands_data = docked_ligands.read()
            self.assertIn('HA_RMSDs', docked_ligands_data)  # standard RMSD
            self.assertIn('HA_RMSDh', docked_ligands_data)  # graph matched min RMSD
            self.assertIn('HA_RMSDm', docked_ligands_data)  # greedy min RMSD

    def tearDown(self):
        self.tmp_dir.cleanup()
