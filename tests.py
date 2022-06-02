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

logging.basicConfig(level=logging.ERROR)


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
            self.tmp_dir.name,
            self.config,
            protein=protein,
            ligand=ligand
        ).run()
        self.assertTrue(os.path.exists(preparation.converted_ligand))
        self.assertTrue(os.path.exists(preparation.active_site_mol2))
        self.assertTrue(os.path.exists(preparation.active_site_pdb))
        self.assertTrue(preparation.output_exists())

    def test_run_with_ligand(self):
        """Test ligand preparation"""
        ligand = os.path.abspath(os.path.join('test_files', '1cps_ligand.sdf'))
        preparation = Preparation(self.tmp_dir.name, self.config, ligand=ligand).run()
        self.assertTrue(os.path.exists(preparation.converted_ligand))
        self.assertTrue(preparation.output_exists())

    def test_run_with_protein(self):
        """Test ligand protein preparation (only performs protonation)"""
        protein = os.path.abspath(os.path.join('test_files', '1cps.pdb'))
        preparation = Preparation(self.tmp_dir.name, self.config, protein=protein).run()
        self.assertTrue(protein != preparation.protein)
        self.assertIn('_h', preparation.protein)

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
        active_site = os.path.abspath(os.path.join('test_files', '1cps_active_site.pdb'))
        ligand = os.path.abspath(os.path.join('test_files', '1cps_ligand_h.mol2'))
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
        active_site = os.path.abspath(os.path.join('test_files', '1cps_active_site.mol2'))
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
        ligand = os.path.abspath(os.path.join('test_files', '1cps_ligand_h.mol2'))
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
