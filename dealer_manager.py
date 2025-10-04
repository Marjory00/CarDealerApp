# dealer_manager.py


# dealer_manager.py

import json
import os
from datetime import datetime
from car import Car 
from typing import List, Dict, Any, Optional

DATA_FILE = 'cars.json'
SALES_FILE = 'sales.json' 

class DealerManager:
    """
    Manages the core inventory and sales operations.
    """

    def __init__(self, file_path: str = DATA_FILE, sales_file: str = SALES_FILE):
        self.file_path = file_path
        self.sales_file = sales_file
        self.inventory: List[Car] = []
        self.sales_history: List[Dict[str, Any]] = [] 
        self._load_data()
        self._load_sales_history()


    # --- FIXED Update: To Fetch cars that are sold ---

    def get_sold_cars(self) -> List[Dict[str, Any]]:
        """
        Returns a list of all cars that have been sold. 
        Since sold cars are removed from inventory and stored in self.sales_history 
        as dictionaries, we return the sales history.
        """
        # FIX: Return the sales history, reversed to show newest sales first.
        return list(reversed(self.sales_history))


    # --- Internal Data Loading/Saving ---

    def _load_data(self):
        """Loads car data from the inventory JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    for car_data in data:
                        try:
                            # FIX: Reverting to explicit key passing for robustness 
                            # against potential JSON key/order variations vs. Car constructor.
                            self.inventory.append(Car(
                                make=car_data.get('make'),
                                model=car_data.get('model'),
                                year=car_data.get('year'),
                                price=car_data.get('price'),
                                vin=car_data.get('vin'),
                                image_url=car_data.get('image_url', "")
                            ))
                        except (TypeError, ValueError) as e:
                            # Added detailed context to the error message for debugging
                            print(f"Skipping corrupt car entry in JSON: {car_data}. Error: {e}") 
            except (IOError, json.JSONDecodeError):
                self.inventory = [] 

    def _load_sales_history(self):
        """Loads sales data from the sales JSON file."""
        if os.path.exists(self.sales_file):
            try:
                with open(self.sales_file, 'r') as f:
                    self.sales_history = json.load(f)
            except (IOError, json.JSONDecodeError):
                self.sales_history = []

    def save_data(self) -> bool:
        """Saves the current inventory to the JSON file."""
        data = [car.to_dict() for car in self.inventory] 
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except IOError:
            return False
    
    def save_sales_history(self) -> bool:
        """Saves the current sales history to the sales JSON file."""
        try:
            with open(self.sales_file, 'w') as f:
                json.dump(self.sales_history, f, indent=4)
            return True
        except IOError:
            return False

    # --- CRUD Operations ---

    def find_car_by_vin(self, vin: str) -> Optional[Car]:
        """Helper method to find a car object by its VIN (case-insensitive)."""
        vin = vin.strip().upper()
        return next((car for car in self.inventory if car.vin == vin), None)

    def add_car(self, car: Car) -> bool:
        """Adds a new Car object to the inventory after checking for duplicates."""
        if self.find_car_by_vin(car.vin):
            return False
        self.inventory.append(car)
        return True
    
    def edit_car(self, vin: str, 
                  new_price: Optional[float] = None, 
                  new_image_url: Optional[str] = None, 
                  new_year: Optional[int] = None) -> bool:
        """Updates specific details of an existing car."""
        car = self.find_car_by_vin(vin)
        if not car:
            return False
            
        # 1. Update Price
        if new_price is not None:
            try:
                # Basic validation: must be positive
                if new_price <= 0:
                    raise ValueError("Price must be positive.")
                car.price = new_price
            except ValueError:
                return False 
                
        # 2. Update Image URL
        if new_image_url is not None:
            car.image_url = new_image_url.strip() if new_image_url.strip() else "/static/placeholder.png"
            
        # 3. Update Year
        if new_year is not None:
            try:
                # The most reliable way to validate changes (like year) is to check 
                # against the Car validation logic. We temporarily create a Car instance
                # using the existing attributes and the new year to check.
                # Note: This is computationally heavier but ensures full validation.
                Car(car.make, car.model, new_year, car.price, car.vin, car.image_url) 
                car.year = new_year
            except ValueError:
                return False 
                
        return True

    def remove_car(self, vin: str) -> bool:
        """Removes a car from inventory and logs it to sales history."""
        car = self.find_car_by_vin(vin)
        if not car:
            return False

        # 1. Log sale
        sale_record = car.to_dict()
        sale_record['sale_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sales_history.append(sale_record)
        
        # 2. Remove from inventory
        # The filter must use the normalized VIN to match the find_car_by_vin logic
        normalized_vin = vin.strip().upper()
        self.inventory = [c for c in self.inventory if c.vin != normalized_vin]
        
        return True
    
    def get_inventory(self) -> List[Car]:
        """Returns the entire inventory list."""
        return self.inventory

    def search_cars(self, query: str) -> List[Car]:
        """Searches cars by make or model."""
        query = query.strip().lower()
        if not query:
            return []
        
        results = [
            car for car in self.inventory 
            if query in car.make.lower() or query in car.model.lower()
        ]
        return results

    def get_sales_report(self) -> Dict[str, Any]:
        """Generates a summary of sales history."""
        total_revenue = sum(sale['price'] for sale in self.sales_history)
        total_sold = len(self.sales_history)
        
        return {
            'total_sold': total_sold,
            'total_revenue': total_revenue,
            # FIX: Return history in reverse-chronological order (newest first)
            'history': list(reversed(self.sales_history)) 
        }