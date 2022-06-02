"""Test for DOCK workflow elements"""
import configparser
import logging
import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from prepare import Preparation
from spheres import SphereGeneration
from grid import GridGeneration
from docking_run import DockingRun
from prepare_receptor import ReceptorPreparation
from self_docking import SelfDocking
from cross_docking import CrossDocking
from protoss import ProtossRun
from rmsd_analysis import RmsdAnalysis

logging.basicConfig(level=logging.WARNING)


class ProtossRunTest(TestCase):
    """Test protoss run"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test protoss run"""
        protein = os.path.abspath(os.path.join('test_files', '1cps.pdb'))
        ligand = os.path.abspath(os.path.join('test_files', '1cps_ligand.sdf'))
        protoss_run = ProtossRun(protein, self.tmp_dir.name, self.config, ligand=ligand).run()
        self.assertTrue(os.path.exists(protoss_run.protonated_protein))
        self.assertTrue(os.path.exists(protoss_run.protonated_ligand))
        self.assertTrue(protoss_run.output_exists())

    def tearDown(self):
        self.tmp_dir.cleanup()


class PreparationTest(TestCase):
    """Test preparation"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.tmp_dir = TemporaryDirectory()

    def test_run_with_protein_and_ligand(self):
        """Test preparation run"""
        protein = os.path.abspath(os.path.join('test_files', '1cps.pdb'))
        ligand = os.path.abspath(os.path.join('test_files', '1cps_ligand.sdf'))
        preparation = Preparation(
            ligand,
            self.tmp_dir.name,
            self.config,
            protein=protein
        ).run()
        self.assertTrue(os.path.exists(preparation.converted_ligand))
        self.assertTrue(os.path.exists(preparation.active_site_mol2))
        self.assertTrue(os.path.exists(preparation.active_site_pdb))
        self.assertTrue(preparation.output_exists())

    def test_run_with_ligand(self):
        """Test ligand preparation"""
        ligand = os.path.abspath(os.path.join('test_files', '1cps_ligand.sdf'))
        preparation = Preparation(ligand, self.tmp_dir.name, self.config).run()
        self.assertTrue(os.path.exists(preparation.converted_ligand))
        self.assertTrue(preparation.output_exists())

    def tearDown(self):
        self.tmp_dir.cleanup()


class SphereGenerationTest(TestCase):
    """Test sphere generation"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test sphere generation run"""
        active_site = os.path.abspath(os.path.join('test_files', '1cps_h_active_site.pdb'))
        ligand = os.path.abspath(os.path.join('test_files', '1cps_h_ligand.mol2'))
        sphere_generation = SphereGeneration(
            active_site,
            ligand,
            self.tmp_dir.name,
            self.config
        ).run()
        self.assertTrue(os.path.exists(sphere_generation.selected_spheres))
        self.assertTrue(os.path.exists(sphere_generation.selected_spheres_pdb))
        self.assertTrue(sphere_generation.output_exists())

    def tearDown(self):
        self.tmp_dir.cleanup()


class GridGenerationTest(TestCase):
    """Test grid generation"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test grid generation run"""
        active_site = os.path.abspath(os.path.join('test_files', '1cps_h_active_site.mol2'))
        selected_spheres = os.path.abspath(os.path.join('test_files', 'selected_spheres.sph'))
        grid_generation = GridGeneration(
            active_site,
            selected_spheres,
            self.tmp_dir.name,
            self.config
        ).run()
        self.assertTrue(os.path.exists(grid_generation.energy_grid))
        self.assertTrue(os.path.exists(grid_generation.bump_grid))
        self.assertTrue(grid_generation.output_exists())

    def tearDown(self):
        self.tmp_dir.cleanup()


class DockingRunTest(TestCase):
    """Test docking run"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test docking run"""
        ligand = os.path.abspath(os.path.join('test_files', '1cps_h_ligand.mol2'))
        selected_spheres = os.path.abspath(os.path.join('test_files', 'selected_spheres.sph'))
        grid_prefix = os.path.abspath(os.path.join('test_files', 'grid'))
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
        ligand = os.path.abspath(os.path.join('test_files', '1cps_h_ligand.mol2'))
        selected_spheres = os.path.abspath(os.path.join('test_files', 'selected_spheres.sph'))
        grid_prefix = os.path.abspath(os.path.join('test_files', 'grid'))
        docking_in = os.path.abspath(os.path.join('templates', 'FAD.in.template'))
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
        ligand = os.path.abspath(os.path.join('test_files', '1cps_h_ligand.mol2'))
        selected_spheres = os.path.abspath(os.path.join('test_files', 'selected_spheres.sph'))
        grid_prefix = os.path.abspath(os.path.join('test_files', 'grid'))
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


class ReceptorPreparationTest(TestCase):
    """Test receptor preparation"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test receptor preparation run"""
        protein = os.path.abspath(os.path.join('test_files', '1cps.pdb'))
        ligand = os.path.abspath(os.path.join('test_files', '1cps_ligand.sdf'))
        receptor_preparation = ReceptorPreparation(
            protein,
            ligand,
            self.tmp_dir.name,
            self.config
        ).run()
        self.assertTrue(os.path.exists(receptor_preparation.converted_ligand))
        self.assertTrue(os.path.exists(receptor_preparation.selected_spheres))
        self.assertTrue(receptor_preparation.output_exists())

    def tearDown(self):
        self.tmp_dir.cleanup()


class SelfDockingTest(TestCase):
    """Test self docking"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test self docking run"""
        protein = os.path.abspath(os.path.join('test_files', '1cps.pdb'))
        ligand = os.path.abspath(os.path.join('test_files', '1cps_ligand.sdf'))
        self_docking = SelfDocking(protein, ligand, self.tmp_dir.name, self.config).run()
        self.assertTrue(os.path.exists(self_docking.docked))

    def tearDown(self):
        self.tmp_dir.cleanup()


class CrossDockingTest(TestCase):
    """Test cross docking"""

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.tmp_dir = TemporaryDirectory()

    def test_run(self):
        """Test cross docking run"""
        protein = os.path.abspath(os.path.join('test_files', '1cps.pdb'))
        native_ligand = os.path.abspath(os.path.join('test_files', '1cps_ligand.sdf'))
        docking_ligand = os.path.abspath(os.path.join('test_files', '1cbx_ligand.sdf'))
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


class RmsdAnalysisTest(TestCase):
    """Test rmsd analysis"""
    def test_run(self):
        """Test rmsd analysis run"""
        docked_poses = os.path.abspath(os.path.join('test_files', 'docked_scored.mol2'))
        rmsd_analysis = RmsdAnalysis(docked_poses).run()
        self.assertIsNotNone(rmsd_analysis.top_rmsd_s)
        self.assertIsNotNone(rmsd_analysis.top_rmsd_h)
        self.assertIsNotNone(rmsd_analysis.top_rmsd_m)
        self.assertIsNotNone(rmsd_analysis.top_rmsd)
        self.assertTrue(rmsd_analysis.output_exists())
