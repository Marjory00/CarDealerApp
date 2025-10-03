# dealer_manager.py

import json
import os
from datetime import datetime
from car import Car 
from typing import List, Dict, Any, Optional

# Define the data file paths
DATA_FILE = 'cars.json'
SALES_FILE = 'sales.json' 

class DealerManager:
    """
    Manages the core inventory and sales operations, including loading, saving,
    adding, removing, and searching for cars, and handling image_url data.
    """

    def __init__(self, file_path: str = DATA_FILE, sales_file: str = SALES_FILE):
        """Initializes the manager, setting up file paths and loading data."""
        self.file_path = file_path
        self.sales_file = sales_file
        self.inventory: List[Car] = []
        self.sales_history: List[Dict[str, Any]] = [] 
        self._load_data()
        self._load_sales_history()

    # ------------------ Data Persistence Methods ------------------

    def _load_data(self):
        """Loads car data from the inventory JSON file and recreates Car objects."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    for car_data in data:
                        try:
                            # Recreate Car objects using its attributes (safely handles image_url)
                            self.inventory.append(Car(**car_data))
                        except (TypeError, ValueError) as e:
                            print(f"Skipping corrupt car entry in JSON: {car_data}. Error: {e}")
            except (IOError, json.JSONDecodeError):
                print("Could not read or parse inventory file. Starting with empty inventory.")

    def _load_sales_history(self):
        """Loads sales data from the sales JSON file."""
        if os.path.exists(self.sales_file):
            try:
                with open(self.sales_file, 'r') as f:
                    self.sales_history = json.load(f)
            except (IOError, json.JSONDecodeError):
                print("Could not read or parse sales file. Starting with empty sales history.")

    def save_data(self) -> bool:
        """Saves the current inventory to the JSON file. Returns True/False for success."""
        data = [car.to_dict() for car in self.inventory] 
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Inventory successfully saved to {self.file_path}.")
            return True
        except IOError:
            print("CRITICAL ERROR: Could not write to inventory data file. Data is not saved.")
            return False
    
    def save_sales_history(self) -> bool:
        """Saves the current sales history to the sales JSON file. Returns True/False for success."""
        try:
            with open(self.sales_file, 'w') as f:
                json.dump(self.sales_history, f, indent=4)
            print(f"Sales history successfully saved to {self.sales_file}.")
            return True
        except IOError:
            print("CRITICAL ERROR: Could not write to sales history file. Data is not saved.")
            return False

    # ------------------ Inventory Management Methods ------------------

    def find_car_by_vin(self, vin: str) -> Optional[Car]:
        """Helper method to find a car object by its VIN (case-insensitive)."""
        vin = vin.strip().upper()
        # Returns the Car object or None if not found
        return next((car for car in self.inventory if car.vin == vin), None)

    # Alias for clarity when retrieving a car object in the UI
    get_car_by_vin = find_car_by_vin

    def add_car(self, car: Car) -> bool:
        """Adds a new Car object to the inventory after checking for duplicates."""
        if self.find_car_by_vin(car.vin):
            print(f"Error: Car with VIN {car.vin} already exists.")
            return False
        
        self.inventory.append(car)
        print(f"Added: {car.make} {car.model}")
        return True
    
    def edit_car(self, vin: str, new_price: Optional[float] = None, new_year: Optional[int] = None) -> bool:
        """Updates the price and/or year of an existing car by VIN."""
        car = self.find_car_by_vin(vin)
        
        if not car:
            raise ValueError(f"Car with VIN {vin} not found.")

        if new_price is None and new_year is None:
            raise ValueError("No changes specified (both price and year skipped).") 

        # Use new/old values for validation via Car.__init__ before applying changes
        temp_price = new_price if new_price is not None else car.price
        temp_year = new_year if new_year is not None else car.year
        temp_image_url = car.image_url 

        try:
            # Re-validate the car with proposed changes
            Car(car.make, car.model, temp_year, temp_price, car.vin, image_url=temp_image_url) 
        except ValueError as e:
            raise ValueError(f"Validation error during edit: {e}") from e

        # If validation passed, apply the changes
        if new_price is not None:
            car.price = float(new_price)
        if new_year is not None:
            car.year = int(new_year)
            
        return True

    def remove_car(self, vin: str) -> bool:
        """Removes a car from the inventory by its VIN and records the sale."""
        car_to_sell = self.find_car_by_vin(vin)
        vin = vin.strip().upper()

        if car_to_sell:
            # 1. Record the sale (uses Car.to_dict(), which includes image_url)
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
            
    def get_sales_history(self) -> List[Dict[str, Any]]:
        """Returns the list of sales records."""
        return self.sales_history

    def view_sales_history(self):
        """Prints the sales history and summary to the console."""
        if not self.sales_history:
            print("\nNo sales transactions have been recorded.")
            return

        total_revenue = sum(record['price'] for record in self.sales_history)
        
        print("\n--- Sales History Report ---")
        print(f"Total Cars Sold: {len(self.sales_history)}")
        print(f"Total Revenue: ${total_revenue:,.2f}")
        print("-" * 30)

        # Display sales in reverse chronological order
        for i, car in enumerate(reversed(self.sales_history)):
            print(f"[{len(self.sales_history) - i}]: {car['sale_date']} | {car['year']} {car['make']} {car['model']} | Price: ${car['price']:,.2f}")
        print("-" * 30)

    def search_cars(self, query: str) -> List[Car]:
        """Searches for cars matching the query in make or model (case-insensitive)."""
        query = query.lower().strip()
        results = [
            car for car in self.inventory 
            if query in car.make.lower() or query in car.model.lower()
        ]
        return results

    def get_inventory(self) -> List[Car]:
        """Returns the entire inventory list."""
        return self.inventory