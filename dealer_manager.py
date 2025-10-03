# dealer_manager.py

import json
import os
from car import Car 

# Define the data file path
DATA_FILE = 'cars.json'

class DealerManager:
    """Manages the core inventory operations, including loading, saving, and validation."""

    def __init__(self, file_path=DATA_FILE):
        """Initializes the manager, setting up file path and loading data."""
        self.file_path = file_path
        self.inventory = []
        self._load_data()

    def _load_data(self):
        """Loads car data from the JSON file and recreates Car objects."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    for car_data in data:
                        try:
                            # Recreate Car objects from dictionary data
                            self.inventory.append(Car(**car_data))
                        except (TypeError, ValueError) as e:
                            print(f"Skipping corrupt car entry in JSON: {car_data}. Error: {e}")
                print(f"Data loaded successfully from {self.file_path}.")
            except (IOError, json.JSONDecodeError):
                print("Could not read or parse data file. Starting with empty inventory.")
        else:
            print("Data file not found. Starting with empty inventory.")

    def save_data(self):
        """Saves the current inventory to the JSON file."""
        data = [car.to_dict() for car in self.inventory]
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Inventory successfully saved to {self.file_path}.")
        except IOError:
            print("Error: Could not write to data file.")

    def find_car_by_vin(self, vin):
        """Helper method to find a car object by its VIN."""
        vin = vin.strip().upper()
        # Returns the Car object or None if not found
        return next((car for car in self.inventory if car.vin == vin), None)

    def add_car(self, car):
        """Adds a new Car object to the inventory after validation checks."""
        # VIN validation: Check for 17-character alphanumeric format
        if len(car.vin) != 17 or not car.vin.isalnum():
             print(f"Error: VIN {car.vin} is not a valid 17-character alphanumeric code.")
             return False

        # Check for duplicate VIN
        if self.find_car_by_vin(car.vin):
            print(f"Error: Car with VIN {car.vin} already exists.")
            return False
        
        self.inventory.append(car)
        print(f"Added: {car.make} {car.model}")
        return True
    
    def edit_car(self, vin, new_price=None, new_year=None):
        """Updates the price and/or year of an existing car by VIN."""
        car = self.find_car_by_vin(vin)
        
        if not car:
            return False # Car not found

        # Update and Validate Price
        if new_price is not None:
            if new_price <= 0:
                print("Error: Price must be a positive number.")
                return False
            car.price = new_price

        # Update and Validate Year
        if new_year is not None:
            current_year = 2025 # Define a reasonable limit for validation
            if new_year < 1900 or new_year > (current_year + 1):
                print(f"Error: Year {new_year} is out of a reasonable range.")
                return False
            car.year = new_year
            
        return True

    def search_cars(self, query):
        """Searches for cars matching the query in make or model (case-insensitive)."""
        query = query.lower().strip()
        results = [
            car for car in self.inventory 
            if query in car.make.lower() or query in car.model.lower()
        ]
        return results

    def remove_car(self, vin):
        """Removes a car from the inventory by its VIN (Simulates a sale)."""
        initial_count = len(self.inventory)
        vin = vin.strip().upper()

        # Rebuild the inventory list, excluding the car with the matching VIN
        self.inventory = [car for car in self.inventory if car.vin != vin]

        if len(self.inventory) < initial_count:
            print(f"Car with VIN {vin} sold and removed from inventory.")
            return True
        else:
            print(f"Error: Car with VIN {vin} not found.")
            return False