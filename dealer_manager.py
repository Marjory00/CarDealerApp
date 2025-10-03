# dealer_manager.py

import json
import os
from datetime import datetime # Import for sales date logging
from car import Car 

# Define the data file paths
DATA_FILE = 'cars.json'
SALES_FILE = 'sales.json' # NEW: File for sales history

class DealerManager:
    """
    Manages the core inventory and sales operations, including loading, saving,
    adding, removing, and searching for cars.
    """

    def __init__(self, file_path=DATA_FILE, sales_file=SALES_FILE):
        """Initializes the manager, setting up file paths and loading data."""
        self.file_path = file_path
        self.sales_file = sales_file
        self.inventory = []
        self.sales_history = [] # NEW: Stores records of cars sold
        self._load_data()
        self._load_sales_history() # NEW: Load sales data

    # --- Data Persistence Methods ---

    def _load_data(self):
        """Loads car data from the inventory JSON file and recreates Car objects."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    for car_data in data:
                        try:
                            # Recreate Car objects using its __init__ (which should include validation)
                            self.inventory.append(Car(**car_data))
                        except (TypeError, ValueError) as e:
                            # Catch validation/structure errors when loading old data
                            print(f"Skipping corrupt car entry in JSON: {car_data}. Error: {e}")
                print(f"Inventory loaded successfully from {self.file_path}.")
            except (IOError, json.JSONDecodeError):
                print("Could not read or parse inventory file. Starting with empty inventory.")
        else:
            print("Inventory file not found. Starting with empty inventory.")

    def _load_sales_history(self):
        """NEW: Loads sales data from the sales JSON file."""
        if os.path.exists(self.sales_file):
            try:
                with open(self.sales_file, 'r') as f:
                    self.sales_history = json.load(f)
                print(f"Sales history loaded successfully from {self.sales_file}.")
            except (IOError, json.JSONDecodeError):
                print("Could not read or parse sales file. Starting with empty sales history.")
        else:
            print("Sales file not found. Starting with empty sales history.")

    def save_data(self):
        """Saves the current inventory to the JSON file."""
        data = [car.to_dict() for car in self.inventory]
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Inventory successfully saved to {self.file_path}.")
        except IOError:
            print("Error: Could not write to inventory data file.")
    
    def save_sales_history(self):
        """NEW: Saves the current sales history to the sales JSON file."""
        try:
            with open(self.sales_file, 'w') as f:
                json.dump(self.sales_history, f, indent=4)
            print(f"Sales history successfully saved to {self.sales_file}.")
        except IOError:
            print("Error: Could not write to sales history file.")

    # --- Inventory Management Methods ---

    def find_car_by_vin(self, vin):
        """Helper method to find a car object by its VIN (case-insensitive)."""
        vin = vin.strip().upper()
        return next((car for car in self.inventory if car.vin == vin), None)

    def add_car(self, car):
        """Adds a new Car object to the inventory after checking for duplicates.
        NOTE: Relies on Car object already being validated by Car.__init__."""
        
        # REMOVED redundant VIN validation (assumed done by Car.__init__)

        # Check for duplicate VIN
        if self.find_car_by_vin(car.vin):
            # Error message for application/CLI level display
            print(f"Error: Car with VIN {car.vin} already exists.")
            return False
        
        self.inventory.append(car)
        print(f"Added: {car.make} {car.model}")
        return True
    
    def edit_car(self, vin, new_price=None, new_year=None):
        """Updates the price and/or year of an existing car by VIN.
        Uses Car.__init__ for validation by creating a temporary Car object."""
        car = self.find_car_by_vin(vin)
        
        if not car:
            # Raise an exception for API/CLI to catch
            raise ValueError(f"Car with VIN {vin} not found.")

        # Temporarily create a new Car instance to leverage its validation logic
        temp_price = new_price if new_price is not None else car.price
        temp_year = new_year if new_year is not None else car.year
        
        try:
            # Validate new values by attempting to create a new Car (won't save it)
            Car(car.make, car.model, temp_year, temp_price, car.vin)
        except ValueError as e:
            # Re-raise the ValueError with context
            raise ValueError(f"Validation error during edit: {e}") from e

        # If validation passed, apply the changes to the original car object
        if new_price is not None:
            car.price = float(new_price)
        if new_year is not None:
            car.year = int(new_year)
            
        return True

    def remove_car(self, vin):
        """Removes a car from the inventory by its VIN and records the sale. (UPDATED)"""
        car_to_sell = self.find_car_by_vin(vin)
        vin = vin.strip().upper()

        if car_to_sell:
            # 1. Record the sale
            sale_record = car_to_sell.to_dict()
            sale_record['sale_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.sales_history.append(sale_record)
            
            # 2. Remove the car from the inventory
            self.inventory = [car for car in self.inventory if car.vin != vin]
            
            print(f"Car with VIN {vin} sold and removed from inventory.")
            return True
        else:
            print(f"Error: Car with VIN {vin} not found.")
            return False
            
    def get_sales_history(self):
        """Returns the list of sales records."""
        return self.sales_history

    def search_cars(self, query):
        """Searches for cars matching the query in make or model (case-insensitive)."""
        query = query.lower().strip()
        results = [
            car for car in self.inventory 
            if query in car.make.lower() or query in car.model.lower()
        ]
        return results

    def get_inventory(self):
        """Returns the entire inventory list."""
        return self.inventory