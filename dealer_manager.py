
# dealer_manager.py

import json
import os
import re
from car import Car

class DealerManager:
    """
    Manages the car inventory, handling data persistence (JSON) and all
    core inventory operations (add, remove, search, edit).
    """
    
    DATA_FILE = 'cars.json'
    # Simple regex for a standard 17-character VIN (excluding I, O, Q)
    VIN_PATTERN = re.compile(r'^[A-HJ-NPR-Z0-9]{17}$')

    def __init__(self):
        """Initializes the manager and attempts to load existing data."""
        self.inventory = []
        self._load_data()

    def _load_data(self):
        """Loads car data from the JSON file into a list of Car objects."""
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, 'r') as f:
                    data = json.load(f)
                    # Recreate Car objects from the loaded dictionaries
                    for car_data in data:
                        # Use **car_data to unpack the dictionary into Car constructor
                        self.inventory.append(Car(**car_data))
                print(f"Data loaded successfully from {self.DATA_FILE}.")
            except (IOError, json.JSONDecodeError):
                print("Could not read or parse data file. Starting with empty inventory.")
        else:
            print("Data file not found. Starting with empty inventory.")

    def save_data(self):
        """Saves the current inventory (converted to list of dicts) to JSON."""
        # Convert Car objects back to dictionaries for JSON serialization
        data = [car.to_dict() for car in self.inventory]
        try:
            with open(self.DATA_FILE, 'w') as f:
                # Use indent=4 for readable JSON formatting
                json.dump(data, f, indent=4)
            print(f"Inventory successfully saved to {self.DATA_FILE}.")
        except IOError:
            print("Error: Could not write to data file.")

    def find_car_by_vin(self, vin):
        """Returns the Car object matching the VIN, or None if not found."""
        vin = vin.upper()
        for car in self.inventory:
            if car.vin == vin:
                return car
        return None

    def add_car(self, car):
        """Adds a new Car object after validating its VIN."""
        if not self.VIN_PATTERN.match(car.vin):
            print(f"Error: VIN '{car.vin}' is structurally invalid (must be 17 chars, excluding I, O, Q).")
            return False
            
        if self.find_car_by_vin(car.vin):
            print(f"Error: Car with VIN {car.vin} already exists.")
            return False
        
        self.inventory.append(car)
        print(f"Added: {car.make} {car.model}")
        return True

    def view_inventory(self):
        """Prints the entire inventory in a formatted list."""
        if not self.inventory:
            print("\nThe inventory is currently empty.")
            return

        print("\n--- Current Inventory ---")
        for i, car in enumerate(self.inventory, 1):
            print(f"[{i:02}]: {car}") # Ensures two-digit indexing for alignment
        print("-" * 50)
        print(f"Total Vehicles: {len(self.inventory)}")

    def search_cars(self, query):
        """Searches for cars matching the query in make or model (case-insensitive)."""
        query = query.lower().strip()
        results = [
            car for car in self.inventory 
            if query in car.make.lower() or query in car.model.lower()
        ]
        
        if not results:
            print(f"\nNo cars found matching '{query}'.")
            return

        print(f"\n--- Search Results for '{query}' ({len(results)} found) ---")
        for car in results:
            print(car)
        print("-" * 50)

    def remove_car(self, vin):
        """Removes a car by its VIN (simulating a sale)."""
        initial_count = len(self.inventory)
        vin = vin.upper().strip()
        
        # Filter the inventory to exclude the car with the matching VIN
        self.inventory = [car for car in self.inventory if car.vin != vin]

        if len(self.inventory) < initial_count:
            print(f"Car with VIN {vin} sold and removed from inventory.")
            return True
        else:
            print(f"Error: Car with VIN {vin} not found.")
            return False

    def edit_car(self, vin, new_price=None, new_year=None):
        """Allows modification of an existing car's price or year."""
        car = self.find_car_by_vin(vin)
        
        if not car:
            print(f"Error: Car with VIN {vin} not found.")
            return False

        if new_price is not None:
            car.price = new_price
        
        if new_year is not None:
            car.year = new_year

        print(f"Updated Details: {car}")
        return True