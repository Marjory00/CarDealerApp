# dealer_app.py

# dealer_app.py


import json
import os
import sys
from datetime import datetime
# FIX: Assuming Car is imported from a separate car.py file for clean architecture
from car import Car 

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
        self.inventory = []
        self.sales_history = [] 
        self._load_data()
        self._load_sales_history()

    def _load_data(self):
        """Loads car data from the inventory JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    for car_data in data:
                        try:
                            # Use .get() for optional fields like 'image_url' for compatibility
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
                # print(f"Inventory loaded successfully from {self.file_path}.")
            except (IOError, json.JSONDecodeError):
                print("Could not read or parse inventory file. Starting with empty inventory.")
        # else:
            # print("Inventory file not found. Starting with empty inventory.")
    
    def _load_sales_history(self):
        """Loads sales data from the sales JSON file."""
        if os.path.exists(self.sales_file):
            try:
                with open(self.sales_file, 'r') as f:
                    self.sales_history = json.load(f)
                # print(f"Sales history loaded successfully from {self.sales_file}.")
            except (IOError, json.JSONDecodeError):
                print("Could not read or parse sales file. Starting with empty sales history.")
        # else:
            # print("Sales file not found. Starting with empty sales history.")

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

    def get_inventory(self):
        """Returns the full inventory list."""
        return self.inventory
    
    def add_car(self, car):
        """Adds a new Car object to the inventory after checking for duplicates."""
        if any(c.vin == car.vin for c in self.inventory):
            # print(f"Error: Car with VIN {car.vin} already exists.")
            return False
        
        self.inventory.append(car)
        return True

    def find_car_by_vin(self, vin):
        """Helper method to find a car object by its VIN."""
        vin = vin.strip().upper()
        return next((car for car in self.inventory if car.vin == vin), None)

    def edit_car(self, vin: str, new_price: float = None, new_year: int = None, new_image_url: str = None) -> bool:
        """
        FIX: Added edit_car method. 
        Updates the details of an existing car. Returns True on success, False otherwise.
        """
        car = self.find_car_by_vin(vin)
        if not car:
            return False

        # Attempt to update attributes with provided non-None values
        try:
            if new_price is not None:
                car.price = float(new_price)
                if car.price <= 0:
                    raise ValueError("Price must be positive.")
            
            if new_year is not None:
                car.year = int(new_year)
                current_year = datetime.now().year
                if not (1900 <= car.year <= current_year + 2):
                    raise ValueError(f"Year out of range (1900 to {current_year + 2}).")
            
            if new_image_url is not None:
                 # The Car constructor handles defaulting to placeholder if empty
                car.image_url = new_image_url.strip() if new_image_url.strip() else "/static/placeholder.png" 
                
            return True
        except (ValueError, TypeError) as e:
            print(f"Edit validation failed for {vin}: {e}")
            return False

    def remove_car(self, vin):
        """Removes a car from the inventory and records the sale."""
        car_to_sell = self.find_car_by_vin(vin)
        vin = vin.strip().upper()

        if car_to_sell:
            # 1. Record the sale
            sale_record = car_to_sell.to_dict()
            sale_record['sale_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.sales_history.append(sale_record)
            
            # 2. Remove the car from the inventory
            self.inventory = [car for car in self.inventory if car.vin != vin]
            
            # print(f"Car with VIN {vin} sold and removed from inventory.")
            return True
        else:
            # print(f"Error: Car with VIN {vin} not found.")
            return False
    
    def get_sales_report(self):
        """
        FIX: Added get_sales_report to return structured data for the Flask web page.
        """
        total_revenue = sum(record['price'] for record in self.sales_history)
        
        return {
            'total_sold': len(self.sales_history),
            'total_revenue': total_revenue,
            # Reverse history so newest sales are at the top (better for table display)
            'history': list(reversed(self.sales_history)) 
        }

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

        # Iterate through history, showing newest first
        for i, car in enumerate(report['history']):
             # The index i will be 0 for the newest sale
            print(f"[{i+1}]: {car['sale_date']} | {car['year']} {car['make']} {car['model']} | Price: ${car['price']:,.2f}")
        print("-" * 30)

    def view_inventory(self):
        """Prints the entire current inventory to the console (CLI function)."""
        if not self.inventory:
            print("\nThe inventory is currently empty.")
            return

        print("\n--- Current Inventory ---")
        for i, car in enumerate(self.inventory):
            print(f"[{i+1}]: {car}") 
        print("-" * 25)

    def search_cars(self, query):
        """Returns and prints results for cars matching the query in make or model."""
        query = query.lower().strip()
        results = [
            car for car in self.inventory 
            if query in car.make.lower() or query in car.model.lower()
        ]
        
        if not results:
            print(f"\nNo cars found matching '{query}'.")
            return [] # Return empty list for consistency with Flask app

        # CLI Display (optional, since Flask app uses its own display)
        print(f"\n--- Search Results for '{query}' ({len(results)} found) ---")
        for car in results:
            print(car)
        print("-" * 35)
        
        return results # Return results for Flask app usage


# --- User Interface and Main Loop (Remains largely the same for CLI) ---
def get_user_input(prompt, data_type=str):
    """Utility function to get input and handle basic type/empty exceptions."""
    while True:
        try:
            user_input = input(prompt).strip()
            # Allow empty string if the expected type is string (for optional image_url)
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
                print(f"Validation Error: {e}")

        elif choice == 2:
            manager.view_inventory()

        elif choice == 3:
            query = get_user_input("Enter search query (Make or Model): ")
            manager.search_cars(query)

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