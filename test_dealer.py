# test_dealer.py

import unittest
import os
import json
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
        
        # Add the first car to the in-memory inventory
        self.manager.add_car(self.test_car)

    def tearDown(self):
        """Clean up environment after each test by removing temporary files."""
        if os.path.exists(TEST_DATA_FILE):
            os.remove(TEST_DATA_FILE)
        if os.path.exists(TEST_SALES_FILE):
            os.remove(TEST_SALES_FILE)

    # --- Inventory Management Tests ---

    def test_add_car_success(self):
        """Tests successful addition of a car."""
        self.assertEqual(len(self.manager.get_inventory()), 1)
        self.manager.add_car(self.test_car_2)
        self.assertEqual(len(self.manager.get_inventory()), 2)

    def test_add_car_duplicate(self):
        """Tests that adding a duplicate VIN fails."""
        initial_count = len(self.manager.get_inventory())
        success = self.manager.add_car(self.test_car) 
        self.assertFalse(success)
        self.assertEqual(len(self.manager.get_inventory()), initial_count)

    def test_find_car_by_vin(self):
        """Tests retrieval of a car by VIN (case-insensitive)."""
        found_car = self.manager.find_car_by_vin("vinbmwx5testvin0001") # Lowercase input
        self.assertIsNotNone(found_car)
        self.assertEqual(found_car.model, "X5")

    def test_edit_car_price(self):
        """Tests successful editing of a car's price."""
        new_price = 50000.00
        self.manager.edit_car("VINBMWX5TESTVIN0001", new_price=new_price)
        car = self.manager.find_car_by_vin("VINBMWX5TESTVIN0001")
        self.assertEqual(car.price, new_price)
        self.assertEqual(car.year, 2021) # Ensure other fields are unchanged

    def test_remove_car_success(self):
        """Tests successful removal (sale) of a car and sales history logging."""
        success = self.manager.remove_car("VINBMWX5TESTVIN0001")
        self.assertTrue(success)
        self.assertEqual(len(self.manager.get_inventory()), 0)
        self.assertEqual(len(self.manager.get_sales_history()), 1)
        # Check that the sale record contains necessary fields, including image_url
        self.assertIn('sale_date', self.manager.get_sales_history()[0])
        self.assertIn('image_url', self.manager.get_sales_history()[0])

    # --- Persistence Tests ---

    def test_save_and_load_data(self):
        """Tests that inventory data is saved and loaded correctly, including image_url."""
        self.manager.add_car(self.test_car_2)
        self.manager.save_data()
        
        # Load data into a new manager instance
        new_manager = DealerManager(file_path=TEST_DATA_FILE, sales_file=TEST_SALES_FILE)
        
        # Verify inventory loaded correctly
        self.assertEqual(len(new_manager.get_inventory()), 2)
        
        # Verify custom attribute loaded correctly
        loaded_car = new_manager.find_car_by_vin("VINAUDIQ7TESTVIN0002")
        self.assertEqual(loaded_car.image_url, "test_img_2.jpg")

    def test_save_and_load_sales_history(self):
        """Tests that sales history persists correctly."""
        self.manager.remove_car("VINBMWX5TESTVIN0001")
        self.manager.save_sales_history()
        
        # Load history into a new manager instance
        new_manager = DealerManager(file_path=TEST_DATA_FILE, sales_file=TEST_SALES_FILE)
        
        # Verify sales history loaded correctly
        self.assertEqual(len(new_manager.get_sales_history()), 1)
        self.assertIn('sale_date', new_manager.get_sales_history()[0])


if __name__ == '__main__':
    unittest.main()