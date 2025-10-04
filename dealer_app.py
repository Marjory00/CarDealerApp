# dealer_app.py


import json
import os
from datetime import datetime
# FIX: Assuming Car is imported from a separate car.py file for clean architecture
from car import Car 
from typing import List, Dict, Any, Optional

# --- Configuration ---
DATA_FILE = 'cars.json'
SALES_FILE = 'sales.json'

# --- Dealer Manager Class (Handles Inventory & Data Persistence) ---
class DealerManager:
    """
    Manages the core inventory and sales operations, including loading, 
    saving, adding, finding, editing, and selling cars.
    """

    def __init__(self, file_path=DATA_FILE, sales_file=SALES_FILE):
        """Initializes the manager and loads existing data."""
        self.file_path = file_path
        self.sales_file = sales_file 
        self.inventory: List[Car] = []
        self.sales_history: List[Dict[str, Any]] = [] 
        self._load_data()
        self._load_sales_history()

    # --- Data Loading/Saving ---

    def _load_data(self):
        """Loads car data from the inventory JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    for car_data in data:
                        try:
                            make = car_data.get('make')
                            model = car_data.get('model')
                            year = car_data.get('year')
                            price = car_data.get('price')
                            vin = car_data.get('vin')
                            image_url = car_data.get('image_url', "")
                            
                            # Instantiate Car object, relying on Car class for validation
                            self.inventory.append(Car(make, model, year, price, vin, image_url))
                        except (TypeError, ValueError) as e:
                            print(f"Skipping corrupt inventory entry. Error: {e}")
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

    def save_data(self):
        """Saves the current inventory to the JSON file."""
        data = [car.to_dict() for car in self.inventory]
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except IOError:
            print("Error: Could not write to inventory data file.")
            return False

    def save_sales_history(self):
        """Saves the current sales history to the sales JSON file."""
        try:
            with open(self.sales_file, 'w') as f:
                json.dump(self.sales_history, f, indent=4)
            return True
        except IOError:
            print("Error: Could not write to sales history file.")
            return False

    # --- Inventory and Search ---

    def get_inventory(self) -> List[Car]:
        """Returns the full inventory list."""
        return self.inventory
    
    def find_car_by_vin(self, vin: str) -> Optional[Car]:
        """Helper method to find a car object by its VIN (case-insensitive)."""
        vin = vin.strip().upper()
        return next((car for car in self.inventory if car.vin == vin), None)

    def search_cars(self, query: str) -> List[Car]:
        """
        FIX: Core logic now returns the list of matching cars immediately.
        It avoids printing messages if the query is empty, making it suitable for 
        the web app's `index()` route where an empty query shows the full list.
        """
        normalized_query = query.lower().strip()
        
        # Return full inventory if the query is empty
        if not normalized_query:
            return self.inventory
            
        results = [
            car for car in self.inventory 
            # Use .lower() for case-insensitive matching
            if normalized_query in car.make.lower() or normalized_query in car.model.lower()
        ]
        return results

    # --- CRUD Operations ---

    def add_car(self, car: Car) -> bool:
        """Adds a new Car object to the inventory after checking for duplicates."""
        if self.find_car_by_vin(car.vin):
            return False
        
        self.inventory.append(car)
        return True

    def edit_car(self, vin: str, new_price: Optional[float] = None, new_year: Optional[int] = None, new_image_url: Optional[str] = None) -> bool:
        """
        Updates the details of an existing car, validating new values. 
        Returns True on success, False otherwise.
        """
        car = self.find_car_by_vin(vin)
        if not car:
            return False

        # Attempt to update attributes with provided non-None values
        try:
            if new_price is not None:
                new_price = float(new_price)
                if new_price <= 0:
                    raise ValueError("Price must be positive.")
                car.price = new_price
            
            if new_year is not None:
                new_year = int(new_year)
                current_year = datetime.now().year
                # Use Car constructor's validation range
                if not (1900 <= new_year <= current_year + 2): 
                    raise ValueError(f"Year out of range (1900 to {current_year + 2}).")
                car.year = new_year
            
            if new_image_url is not None:
                # Set URL or default placeholder
                car.image_url = new_image_url.strip() if new_image_url.strip() else "/static/placeholder.png" 
                
            return True
        except (ValueError, TypeError) as e:
            print(f"Edit validation failed for {vin}: {e}")
            return False

    def remove_car(self, vin: str) -> bool:
        """Removes a car from the inventory and records the sale."""
        car_to_sell = self.find_car_by_vin(vin)
        normalized_vin = vin.strip().upper()

        if car_to_sell:
            # 1. Record the sale
            sale_record = car_to_sell.to_dict()
            sale_record['sale_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.sales_history.append(sale_record)
            
            # 2. Remove the car from the inventory
            self.inventory = [car for car in self.inventory if car.vin != normalized_vin]
            
            return True
        else:
            return False
    
    # --- Reporting ---
    
    def get_sales_report(self) -> Dict[str, Any]:
        """Returns structured data for the sales report."""
        total_revenue = sum(record['price'] for record in self.sales_history)
        
        return {
            'total_sold': len(self.sales_history),
            'total_revenue': total_revenue,
            # Reverse history so newest sales are at the top
            'history': list(reversed(self.sales_history)) 
        }

    # --- CLI Display Methods ---

    def view_sales_history(self):
        """Prints the sales history and summary to the console (CLI function)."""
        report = self.get_sales_report()

        if not report['history']:
            print("\nNo sales transactions have been recorded.")
            return

        print("\n--- Sales History Report ---")
        print(f"Total Cars Sold: {report['total_sold']}")
        print(f"Total Revenue: ${report['total_revenue']:,.2f}")
        print("-" * 30)

        for i, car in enumerate(report['history']):
            print(f"[{i+1}]: {car['sale_date']} | {car['year']} {car['make']} {car['model']} | Price: ${car['price']:,.2f}")
        print("-" * 30)

    def view_inventory(self):
        """Prints the entire current inventory to the console (CLI function)."""
        if not self.inventory:
            print("\nThe inventory is currently empty.")
            return

        print("\n--- Current Inventory ---")
        for i, car in enumerate(self.inventory):
            # Assumes Car object has a __str__ method implemented
            print(f"[{i+1}]: {car}") 
        print("-" * 25)

    def print_search_results(self, query: str):
        """Prints the results of the search to the console (CLI function)."""
        results = self.search_cars(query)
        
        if not results:
            print(f"\nNo cars found matching '{query}'.")
            return

        print(f"\n--- Search Results for '{query}' ({len(results)} found) ---")
        for car in results:
            print(car)
        print("-" * 35)

# --- User Interface and Main Loop (Remains largely the same for CLI) ---
def get_user_input(prompt, data_type=str):
    """Utility function to get input and handle basic type/empty exceptions."""
    while True:
        try:
            user_input = input(prompt).strip()
            # Allow empty string if the expected type is str (for optional image_url)
            if not user_input and data_type is str:
                return ""
            if not user_input and data_type is not str:
                print("Input cannot be empty for this required field.")
                continue
            return data_type(user_input)
        except ValueError:
            print(f"Invalid input. Please enter a valid {data_type.__name__}.")

def main():
    """Main function to run the CLI application loop."""
    manager = DealerManager()

    while True:
        # Display the main menu
        print("\n===== Car Dealer App (CLI) =====")
        print("1. Add New Car")
        print("2. View All Cars")
        print("3. Search Cars (by Make/Model)")
        print("4. Sell/Remove Car (by VIN)")
        print("5. View Sales History & Report")
        print("6. Save & Exit")
        print("7. Exit without Saving")
        
        # Get integer choice, assuming the function handles validation
        choice = get_user_input("Enter your choice (1-7): ", int) 

        if choice == 1:
            print("\n--- Enter Car Details ---")
            
            try: 
                make = get_user_input("Make (e.g., Toyota): ")
                model = get_user_input("Model (e.g., Camry): ")
                year = get_user_input("Year (e.g., 2020): ", int)
                price = get_user_input("Price (e.g., 25000.50): ", float)
                vin = get_user_input("VIN (Unique 17 Chars): ")
                image_url = get_user_input("Image URL (optional): ", str) 
                
                new_car = Car(make, model, year, price, vin, image_url=image_url) 
                if manager.add_car(new_car):
                    print(f"SUCCESS: Added {make} {model}.")
                else:
                    print(f"FAILURE: Car with VIN {vin} already exists.")

            except ValueError as e:
                # Catches errors from Car constructor validation (e.g., invalid year/price)
                print(f"Validation Error: {e}")

        elif choice == 2:
            manager.view_inventory()

        elif choice == 3:
            query = get_user_input("Enter search query (Make or Model): ")
            # FIX: Call the new print_search_results CLI display wrapper
            manager.print_search_results(query)

        elif choice == 4:
            vin_to_remove = get_user_input("Enter VIN of the car to remove (sell): ")
            if manager.remove_car(vin_to_remove):
                print(f"SUCCESS: Car {vin_to_remove} sold and removed.")
                manager.save_data() 
                manager.save_sales_history() 
            else:
                print(f"FAILURE: Car with VIN {vin_to_remove} not found.")

        elif choice == 5: 
            manager.view_sales_history()

        elif choice == 6:
            data_ok = manager.save_data()
            sales_ok = manager.save_sales_history() 
            if data_ok and sales_ok:
                print("Application closed. Goodbye! 👋")
            else:
                print("Application closed. WARNING: Data save failure.")
            break

        elif choice == 7: 
            print("Exiting application without saving changes. Goodbye! 🚪")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

# Standard Python entry point
if __name__ == "__main__":
    main()