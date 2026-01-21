"""
Tests for Pandemic Simulator Engine
BlackMamba University Educational Module
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pandemic_simulator_engine import PandemicSimulatorEngine, Virus


class TestPandemicSimulator(unittest.TestCase):
    """Test suite for Pandemic Simulator Engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = PandemicSimulatorEngine()
    
    def test_load_historical_pandemics(self):
        """Test that historical pandemics are loaded correctly"""
        self.assertIn("covid19", self.engine.historical_pandemics)
        self.assertIn("spanish_flu", self.engine.historical_pandemics)
        self.assertIn("black_death", self.engine.historical_pandemics)
        
        # Verify COVID-19 data
        covid = self.engine.historical_pandemics["covid19"]
        self.assertEqual(covid["virus"].r0, 2.5)
        self.assertEqual(covid["virus"].name, "SARS-CoV-2")
        self.assertEqual(covid["year"], 2019)
    
    def test_virus_creation(self):
        """Test custom virus creation"""
        custom_virus = self.engine.create_custom_virus(
            name="Test Virus",
            r0=2.0,
            mortality=0.05,
            transmission="airborne"
        )
        
        self.assertEqual(custom_virus.name, "Test Virus")
        self.assertEqual(custom_virus.r0, 2.0)
        self.assertEqual(custom_virus.mortality_rate, 0.05)
        self.assertEqual(custom_virus.transmission_type, "airborne")
    
    def test_simulate_spread_basic(self):
        """Test basic simulation without interventions"""
        virus = self.engine.historical_pandemics["covid19"]["virus"]
        result = self.engine.simulate_spread(
            virus=virus,
            origin_country="China",
            days=100,
            interventions=[]
        )
        
        # Verify result structure
        self.assertIn("timeline", result)
        self.assertIn("total_infected", result)
        self.assertIn("total_deaths", result)
        self.assertIn("peak_day", result)
        
        # Verify progression
        self.assertGreater(result["total_infected"], 100)
        self.assertGreater(result["total_deaths"], 0)
        self.assertGreater(len(result["timeline"]), 0)
        self.assertEqual(len(result["timeline"]), 100)
    
    def test_interventions_reduce_r0(self):
        """Test that interventions reduce effective R0"""
        base_r0 = 2.5
        
        # Test lockdown
        lockdown = [{"type": "lockdown", "start_day": 0}]
        effective_r0 = self.engine.apply_interventions(base_r0, 1, lockdown)
        self.assertLess(effective_r0, base_r0)
        self.assertAlmostEqual(effective_r0, 1.0, places=1)
        
        # Test masks
        masks = [{"type": "masks", "start_day": 0}]
        effective_r0 = self.engine.apply_interventions(base_r0, 1, masks)
        self.assertLess(effective_r0, base_r0)
        self.assertAlmostEqual(effective_r0, 1.25, places=1)
    
    def test_multiple_interventions(self):
        """Test that multiple interventions stack"""
        base_r0 = 2.5
        interventions = [
            {"type": "lockdown", "start_day": 0},
            {"type": "masks", "start_day": 0}
        ]
        
        effective_r0 = self.engine.apply_interventions(base_r0, 1, interventions)
        self.assertLess(effective_r0, 1.0)  # Combined effect should be strong
    
    def test_intervention_timing(self):
        """Test that interventions only apply after start_day"""
        base_r0 = 2.5
        intervention = [{"type": "lockdown", "start_day": 30}]
        
        # Before intervention
        r0_before = self.engine.apply_interventions(base_r0, 20, intervention)
        self.assertEqual(r0_before, base_r0)
        
        # After intervention
        r0_after = self.engine.apply_interventions(base_r0, 35, intervention)
        self.assertLess(r0_after, base_r0)
    
    def test_vaccine_with_coverage(self):
        """Test vaccine intervention with different coverage levels"""
        base_r0 = 2.5
        
        # 70% coverage
        vaccine_70 = [{"type": "vaccine", "start_day": 0, "coverage": 0.7}]
        r0_70 = self.engine.apply_interventions(base_r0, 1, vaccine_70)
        
        # 90% coverage
        vaccine_90 = [{"type": "vaccine", "start_day": 0, "coverage": 0.9}]
        r0_90 = self.engine.apply_interventions(base_r0, 1, vaccine_90)
        
        # Higher coverage should result in lower R0
        self.assertLess(r0_90, r0_70)
    
    def test_compare_pandemics(self):
        """Test pandemic comparison functionality"""
        comparison = self.engine.compare_pandemics(
            ["black_death", "spanish_flu", "covid19"]
        )
        
        self.assertEqual(len(comparison), 3)
        self.assertIn("black_death", comparison)
        self.assertIn("spanish_flu", comparison)
        self.assertIn("covid19", comparison)
        
        # Verify data structure
        for pandemic_id, data in comparison.items():
            self.assertIn("name", data)
            self.assertIn("r0", data)
            self.assertIn("mortality", data)
            self.assertIn("deaths", data)
    
    def test_find_peak_day(self):
        """Test peak day calculation"""
        timeline = [
            {"day": 0, "infected": 100},
            {"day": 1, "infected": 500},
            {"day": 2, "infected": 1000},
            {"day": 3, "infected": 800},
            {"day": 4, "infected": 400}
        ]
        
        peak = self.engine.find_peak_day(timeline)
        self.assertEqual(peak, 2)
    
    def test_get_intervention_recommendations(self):
        """Test AI recommendation system"""
        # High R0 scenario
        high_r0_state = {"r_effective": 2.0, "infected": 500000, "deaths": 5000}
        recommendations = self.engine.get_intervention_recommendations(high_r0_state)
        
        self.assertIn("lockdown", recommendations)
        self.assertIn("masks", recommendations)
        
        # Very severe scenario
        severe_state = {"r_effective": 3.0, "infected": 2000000, "deaths": 50000}
        recommendations = self.engine.get_intervention_recommendations(severe_state)
        
        self.assertIn("lockdown", recommendations)
        self.assertIn("emergency_healthcare", recommendations)
        self.assertIn("vaccine", recommendations)
    
    def test_simulation_with_interventions_reduces_deaths(self):
        """Test that simulations with interventions result in fewer deaths"""
        virus = self.engine.historical_pandemics["covid19"]["virus"]
        
        # Simulation without interventions
        result_no_intervention = self.engine.simulate_spread(
            virus=virus,
            origin_country="China",
            days=100,
            interventions=[]
        )
        
        # Simulation with early lockdown
        result_with_lockdown = self.engine.simulate_spread(
            virus=virus,
            origin_country="China",
            days=100,
            interventions=[{"type": "lockdown", "start_day": 10}]
        )
        
        # Lockdown should reduce deaths
        self.assertLess(
            result_with_lockdown["total_deaths"],
            result_no_intervention["total_deaths"]
        )
    
    def test_get_pandemic_data(self):
        """Test retrieving specific pandemic data"""
        covid_data = self.engine.get_pandemic_data("covid19")
        
        self.assertIsNotNone(covid_data)
        self.assertEqual(covid_data["name"], "COVID-19")
        self.assertEqual(covid_data["year"], 2019)
        
        # Test invalid pandemic ID
        invalid_data = self.engine.get_pandemic_data("invalid_id")
        self.assertIsNone(invalid_data)


class TestVirusDataClass(unittest.TestCase):
    """Test Virus dataclass"""
    
    def test_virus_creation(self):
        """Test creating a Virus instance"""
        virus = Virus(
            name="Test Virus",
            r0=2.5,
            mortality_rate=0.02,
            incubation_days=5,
            infectious_days=10,
            transmission_type="airborne"
        )
        
        self.assertEqual(virus.name, "Test Virus")
        self.assertEqual(virus.r0, 2.5)
        self.assertEqual(virus.mortality_rate, 0.02)
        self.assertEqual(virus.incubation_days, 5)
        self.assertEqual(virus.infectious_days, 10)
        self.assertEqual(virus.transmission_type, "airborne")


if __name__ == "__main__":
    unittest.main()
