# test_dealer.py


# test_dealer.py (FIXED)

import unittest
import os
import json
import time # Import for small delay in sale logging, though not strictly needed for the fix
from car import Car
from dealer_manager import DealerManager
from typing import List, Dict, Any

# Define temporary file names for testing to avoid overwriting real data
TEST_DATA_FILE = 'test_cars.json'
TEST_SALES_FILE = 'test_sales.json'

class TestCar(unittest.TestCase):
    """Tests for the Car class validation and dictionary representation."""

    def test_car_creation_valid(self):
        """Tests creation of a car with valid parameters."""
        car = Car("Honda", "Civic", 2020, 25000.00, "VIN12345678901234567", image_url="test.jpg")
        self.assertEqual(car.make, "Honda")
        self.assertEqual(car.year, 2020)
        self.assertEqual(car.price, 25000.00)

    def test_car_creation_invalid_year(self):
        """Tests that Car creation fails with an invalid year."""
        # Use a more specific assertion pattern if the Car class uses it
        with self.assertRaisesRegex(ValueError, "Year must be between 1900 and"):
            Car("Ford", "Mustang", 1899, 50000.00, "VALIDVIN123456789")

    def test_car_creation_invalid_vin_length(self):
        """Tests that Car creation fails with an invalid VIN length."""
        with self.assertRaisesRegex(ValueError, "VIN must be 17 characters long"):
            Car("Tesla", "Model S", 2023, 80000.00, "SHORTVIN")

    def test_to_dict_conversion(self):
        """Tests that the Car object correctly converts to a dictionary."""
        car = Car("Toyota", "Camry", 2023, 30000.00, "VINTOYOTACAMRY2023X", image_url="none")
        expected_dict = {
            "make": "Toyota",
            "model": "Camry",
            "year": 2023,
            "price": 30000.00,
            "vin": "VINTOYOTACAMRY2023X",
            "image_url": "none"
        }
        self.assertEqual(car.to_dict(), expected_dict)


class TestDealerManager(unittest.TestCase):
    """Tests for the DealerManager inventory management and persistence."""

    def setUp(self):
        """Set up environment before each test: initializes manager and test cars."""
        # Clean up old test files if they exist
        if os.path.exists(TEST_DATA_FILE):
            os.remove(TEST_DATA_FILE)
        if os.path.exists(TEST_SALES_FILE):
            os.remove(TEST_SALES_FILE)

        # Initialize the manager with unique test file names
        self.manager = DealerManager(file_path=TEST_DATA_FILE, sales_file=TEST_SALES_FILE)
        
        # Create car instances for testing
        self.test_car = Car("BMW", "X5", 2021, 55000.00, "VINBMWX5TESTVIN0001", image_url="test_img_1.jpg")
        self.test_car_2 = Car("Audi", "Q7", 2022, 60000.00, "VINAUDIQ7TESTVIN0002", image_url="test_img_2.jpg")
        self.test_car_3 = Car("Ford", "Focus", 2018, 15000.00, "VINFOCUSTESTVIN0003", image_url="test_img_3.jpg")
        
        # Add cars to the in-memory inventory
        self.manager.add_car(self.test_car)
        self.manager.add_car(self.test_car_2)
        self.manager.add_car(self.test_car_3)

    def tearDown(self):
        """Clean up environment after each test by removing temporary files."""
        if os.path.exists(TEST_DATA_FILE):
            os.remove(TEST_DATA_FILE)
        if os.path.exists(TEST_SALES_FILE):
            os.remove(TEST_SALES_FILE)

    # --- Inventory Management Tests ---

    def test_add_car_success(self):
        """Tests successful addition of a car."""
        new_car = Car("Chevy", "Volt", 2017, 18000.00, "VINCHEVYVOLT00000004", image_url="test_img_4.jpg")
        self.manager.add_car(new_car)
        self.assertEqual(len(self.manager.get_inventory()), 4)

    def test_add_car_duplicate(self):
        """Tests that adding a duplicate VIN fails."""
        initial_count = len(self.manager.get_inventory()) # 3 cars
        success = self.manager.add_car(self.test_car) # Duplicate
        self.assertFalse(success)
        self.assertEqual(len(self.manager.get_inventory()), initial_count)

    def test_find_car_by_vin_case_insensitivity(self):
        """Tests retrieval of a car by VIN (case-insensitive)."""
        found_car = self.manager.find_car_by_vin("vinbmwx5testvin0001") # Lowercase input
        self.assertIsNotNone(found_car)
        self.assertEqual(found_car.model, "X5")

    # --- Edit Car Tests ---

    def test_edit_car_price(self):
        """Tests successful editing of a car's price."""
        new_price = 50000.00
        success = self.manager.edit_car("VINBMWX5TESTVIN0001", new_price=new_price)
        car = self.manager.find_car_by_vin("VINBMWX5TESTVIN0001")
        self.assertTrue(success)
        self.assertEqual(car.price, new_price)

    def test_edit_car_year(self):
        """Tests successful editing of a car's year (FIXED: Added this test)."""
        new_year = 2023
        success = self.manager.edit_car("VINBMWX5TESTVIN0001", new_year=new_year)
        car = self.manager.find_car_by_vin("VINBMWX5TESTVIN0001")
        self.assertTrue(success)
        self.assertEqual(car.year, new_year)
        self.assertEqual(car.price, 55000.00) # Ensure price is unchanged

    def test_edit_car_invalid_year_fails(self):
        """Tests that editing a car's year to an invalid value fails."""
        initial_year = self.test_car.year
        success = self.manager.edit_car("VINBMWX5TESTVIN0001", new_year=1800) # Invalid year
        car = self.manager.find_car_by_vin("VINBMWX5TESTVIN0001")
        self.assertFalse(success)
        self.assertEqual(car.year, initial_year) # Year should remain the same

    def test_edit_car_negative_price_fails(self):
        """Tests that editing a car's price to a non-positive value fails."""
        initial_price = self.test_car.price
        success = self.manager.edit_car("VINBMWX5TESTVIN0001", new_price=-100.00) 
        car = self.manager.find_car_by_vin("VINBMWX5TESTVIN0001")
        self.assertFalse(success)
        self.assertEqual(car.price, initial_price) # Price should remain the same

    # --- Removal/Sale Tests ---

    def test_remove_car_success(self):
        """Tests successful removal (sale) of a car and sales history logging."""
        success = self.manager.remove_car("VINBMWX5TESTVIN0001")
        self.assertTrue(success)
        self.assertEqual(len(self.manager.get_inventory()), 2)
        self.assertEqual(len(self.manager.sales_history), 1)
        # Check that the sale record contains necessary fields, including image_url
        self.assertIn('sale_date', self.manager.sales_history[0])
        self.assertIn('image_url', self.manager.sales_history[0])

    def test_remove_car_not_found(self):
        """Tests failure when trying to remove a non-existent car."""
        initial_count = len(self.manager.get_inventory())
        success = self.manager.remove_car("NONEXISTENTVIN12345")
        self.assertFalse(success)
        self.assertEqual(len(self.manager.get_inventory()), initial_count)

    # --- Search Tests ---

    def test_search_cars_by_make(self):
        """Tests searching by car make (case-insensitive partial match)."""
        results = self.manager.search_cars("aud")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].make, "Audi")

    def test_search_cars_by_model(self):
        """Tests searching by car model (case-insensitive partial match)."""
        results = self.manager.search_cars("x5")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].model, "X5")

    def test_search_cars_no_results(self):
        """Tests searching for a non-existent car."""
        results = self.manager.search_cars("tesla")
        self.assertEqual(len(results), 0)

    # --- Sales Report Tests ---

    def test_get_sales_report(self):
        """Tests that the sales report correctly calculates totals and reverses history."""
        # Sale 1
        self.manager.remove_car(self.test_car.vin)
        # Sale 2
        self.manager.remove_car(self.test_car_2.vin) 

        report = self.manager.get_sales_report()
        
        # Verify totals
        self.assertEqual(report['total_sold'], 2)
        expected_revenue = 55000.00 + 60000.00
        self.assertEqual(report['total_revenue'], expected_revenue)
        
        # Verify history order (should be reversed: newest sale first)
        self.assertEqual(len(report['history']), 2)
        # The car added second (Q7) should be the first in the reversed list (index 0)
        self.assertEqual(report['history'][0]['model'], "Q7")
        self.assertEqual(report['history'][1]['model'], "X5")

    # --- Persistence Tests ---

    def test_save_and_load_data(self):
        """Tests that inventory data is saved and loaded correctly, including image_url."""
        self.manager.save_data()
        
        # Load data into a new manager instance
        new_manager = DealerManager(file_path=TEST_DATA_FILE, sales_file=TEST_SALES_FILE)
        
        # Verify inventory loaded correctly (3 cars)
        self.assertEqual(len(new_manager.get_inventory()), 3)
        
        # Verify custom attribute loaded correctly
        loaded_car = new_manager.find_car_by_vin("VINAUDIQ7TESTVIN0002")
        self.assertEqual(loaded_car.image_url, "test_img_2.jpg")

    def test_save_and_load_sales_history(self):
        """Tests that sales history persists correctly."""
        self.manager.remove_car(self.test_car.vin)
        self.manager.save_sales_history()
        
        # Load history into a new manager instance
        new_manager = DealerManager(file_path=TEST_DATA_FILE, sales_file=TEST_SALES_FILE)
        
        # Verify sales history loaded correctly
        self.assertEqual(len(new_manager.sales_history), 1)
        self.assertIn('sale_date', new_manager.sales_history[0])
        # Ensure the sales history attribute is accessible and correct
        self.assertEqual(new_manager.sales_history[0]['model'], "X5")


if __name__ == '__main__':
    unittest.main()