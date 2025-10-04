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
        # sales_history stores dictionaries (JSON-ready)
        self.sales_history: List[Dict[str, Any]] = [] 
        self._load_data()
        self._load_sales_history()


    # --- Internal Data Loading/Saving ---

    def _load_data(self):
        """Loads car data from the inventory JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    for car_data in data:
                        try:
                            # Robust loading: ensures all required keys exist
                            required_keys = ['make', 'model', 'year', 'price', 'vin']
                            if any(k not in car_data for k in required_keys):
                                raise ValueError("Missing required key in car data.")
                                
                            self.inventory.append(Car(
                                make=car_data['make'],
                                model=car_data['model'],
                                year=car_data['year'],
                                price=car_data['price'],
                                vin=car_data['vin'],
                                image_url=car_data.get('image_url', "")
                            ))
                        except (TypeError, ValueError, KeyError) as e:
                            # Skip corrupt entries
                            print(f"Skipping corrupt car entry in JSON: {car_data}. Error: {e}") 
            except (IOError, json.JSONDecodeError) as e:
                # Catching specific loading errors and resetting inventory
                print(f"Error loading inventory data: {e}. Inventory reset.")
                self.inventory = [] 

        # --- DEBUG LINE ---
        print(f"DEBUG: Loaded {len(self.inventory)} cars from {self.file_path}.")
        # ------------------
        
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

    def get_car_by_vin(self, vin: str) -> Optional[Car]:
        """Helper method to find a car object by its VIN (case and whitespace-insensitive)."""
        # FIX: The single source of truth for VIN cleaning is here.
        vin_to_find = vin.strip().upper() 
        return next((car for car in self.inventory if car.vin == vin_to_find), None)

    def add_car(self, car: Car) -> bool:
        """Adds a new Car object to the inventory after checking for duplicates."""
        if self.get_car_by_vin(car.vin):
            return False
        self.inventory.append(car)
        return True
    
    def edit_car(self, vin: str, 
                     new_price: Optional[float] = None, 
                     new_image_url: Optional[str] = None, 
                     new_year: Optional[int] = None) -> bool:
        """Updates specific details of an existing car."""
        car = self.get_car_by_vin(vin)
        if not car:
            return False
            
        # 1. Update Price
        if new_price is not None:
            try:
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
            # We trust the Car constructor's validation logic was already performed in app.py
            # or rely on the Car object's setter if one were defined.
            car.year = new_year
                
        return True

    def remove_car(self, vin: str) -> bool:
        """Removes a car from inventory and logs it to sales history."""
        car = self.get_car_by_vin(vin)
        if not car:
            return False

        # 1. Log sale
        sale_record = car.to_dict()
        sale_record['sale_date'] = datetime.now().isoformat()
        self.sales_history.append(sale_record)
        
        # 2. Remove from inventory
        # FIX: Since get_car_by_vin cleaned the VIN, we can use the cleaned VIN for removal.
        vin_to_remove = car.vin 
        self.inventory = [c for c in self.inventory if c.vin != vin_to_remove]
        
        return True
    
    def get_all_cars(self) -> List[Car]:
        """Returns the entire inventory list."""
        return self.inventory


    def search_cars(self, query: str) -> List[Car]:
        """
        Searches cars by VIN, make, or model. Returns full inventory if query is empty.
        """
        normalized_query = query.strip().lower()

        if not normalized_query:
            return self.inventory
        
        results = [
            car for car in self.inventory 
            if normalized_query in str(getattr(car, 'make', '')).lower() 
            or normalized_query in str(getattr(car, 'model', '')).lower()
            or normalized_query in str(getattr(car, 'vin', '')).lower()
        ]
        return results
    

    def get_sold_cars(self) -> List[Dict[str, Any]]:
        """
        Returns a list of all cars that have been sold, with newest sales first.
        """
        return list(reversed(self.sales_history))


    def get_sales_report(self) -> Dict[str, Any]:
        """Generates a summary of sales history."""
        total_revenue = sum(sale.get('price', 0) for sale in self.sales_history)
        total_sold = len(self.sales_history)
        
        return {
            'total_sold': total_sold,
            'total_revenue': total_revenue,
            'history': self.get_sold_cars()
        }