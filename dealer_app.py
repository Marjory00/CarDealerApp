# dealer_app.py

import json
import os
import sys
from datetime import datetime # NEW: Import for sales date logging

# --- Configuration ---
DATA_FILE = 'cars.json'
SALES_FILE = 'sales.json' # NEW: File for sales history

# --- 1. Car Class (Object-Oriented Approach with Validation) ---
class Car:
    """
    Represents a single vehicle in the dealer's inventory.
    This class enforces data integrity using internal validation.
    """
    
    def __init__(self, make, model, year, price, vin):
        """Initializes a new Car object with basic input validation."""
        
        # Strip whitespace and normalize case
        self.make = make.strip()
        self.model = model.strip()
        self.vin = vin.strip().upper() 

        # --- Internal Validation ---
        
        # 1. VIN Format Check
        if len(self.vin) != 17 or not self.vin.isalnum():
             raise ValueError("VIN must be a 17-character alphanumeric code.")

        # 2. Year Range Check
        current_year = datetime.now().year
        try:
            year_val = int(year)
            if year_val < 1900 or year_val > (current_year + 1):
                raise ValueError(f"Year {year_val} is outside a reasonable range (1900 to {current_year + 1}).")
            self.year = year_val
        except ValueError:
             raise ValueError("Year must be a valid integer.")

        # 3. Price Positive Check
        try:
            price_val = float(price)
            if price_val <= 0:
                raise ValueError("Price must be a positive number.")
            self.price = price_val
        except ValueError:
             raise ValueError("Price must be a valid numeric value.")
        
        # --- End Validation ---

    def to_dict(self):
        """Returns a dictionary representation of the car for saving to JSON."""
        return {
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'price': self.price,
            'vin': self.vin
        }

    def __str__(self):
        """Provides a user-friendly string representation of the car for display."""
        return (f"VIN: {self.vin} | {self.year} {self.make} {self.model} "
                f"| Price: ${self.price:,.2f}")


# --- 2. Dealer Manager Class (Handles Inventory & Data Persistence) ---
class DealerManager:
    """
    Manages the core inventory and sales operations. (UPDATED)
    """

    def __init__(self, file_path=DATA_FILE, sales_file=SALES_FILE):
        """Initializes the manager and loads existing data."""
        self.file_path = file_path
        self.sales_file = sales_file 
        self.inventory = []
        self.sales_history = [] 
        self._load_data()
        self._load_sales_history() # NEW

    def _load_data(self):
        """Loads car data from the inventory JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    for car_data in data:
                        try:
                            # Recreate Car objects, catching validation errors
                            self.inventory.append(Car(**car_data))
                        except (TypeError, ValueError) as e:
                            print(f"Skipping corrupt inventory entry. Error: {e}")
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

    def add_car(self, car):
        """Adds a new Car object to the inventory after checking for duplicates."""
        if any(c.vin == car.vin for c in self.inventory):
            print(f"Error: Car with VIN {car.vin} already exists.")
            return False
        
        self.inventory.append(car)
        print(f"Added: {car.make} {car.model}")
        return True

    def find_car_by_vin(self, vin):
        """Helper method to find a car object by its VIN."""
        vin = vin.strip().upper()
        return next((car for car in self.inventory if car.vin == vin), None)

    def remove_car(self, vin):
        """Removes a car from the inventory and records the sale. (UPDATED)"""
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
    
    def view_sales_history(self):
        """NEW: Prints the sales history and summary to the console."""
        if not self.sales_history:
            print("\nNo sales transactions have been recorded.")
            return

        total_revenue = sum(record['price'] for record in self.sales_history)
        
        print("\n--- Sales History Report ---")
        print(f"Total Cars Sold: {len(self.sales_history)}")
        print(f"Total Revenue: ${total_revenue:,.2f}")
        print("-" * 30)

        for i, car in enumerate(reversed(self.sales_history)):
            print(f"[{len(self.sales_history) - i}]: {car['sale_date']} | {car['year']} {car['make']} {car['model']} | Price: ${car['price']:,.2f}")
        print("-" * 30)

    def view_inventory(self):
        """Prints the entire current inventory to the console."""
        if not self.inventory:
            print("\nThe inventory is currently empty.")
            return

        print("\n--- Current Inventory ---")
        for i, car in enumerate(self.inventory):
            print(f"[{i+1}]: {car}") 
        print("-" * 25)

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

        print(f"\n--- Search Results for '{query}' ---")
        for car in results:
            print(car)
        print("-" * 35)


# --- 3. User Interface and Main Loop ---
def get_user_input(prompt, data_type=str):
    """Utility function to get input and handle basic type/empty exceptions."""
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input:
                print("Input cannot be empty.")
                continue
            return data_type(user_input)
        except ValueError:
            print(f"Invalid input. Please enter a valid {data_type.__name__}.")

def main():
    """Main function to run the CLI application loop. (UPDATED)"""
    manager = DealerManager()

    while True:
        # Display the main menu (UPDATED for sales)
        print("\n===== Car Dealer App =====")
        print("1. Add New Car")
        print("2. View All Cars")
        print("3. Search Cars (by Make/Model)")
        print("4. Sell/Remove Car (by VIN)")
        print("5. View Sales History & Report") # NEW menu option
        print("6. Save & Exit")
        print("7. Exit without Saving")
        
        # Choice input is now 1-7
        choice = get_user_input("Enter your choice (1-7): ", int) 

        if choice == 1:
            print("\n--- Enter Car Details ---")
            
            try: # Use try block to catch ValueError from Car.__init__
                make = get_user_input("Make (e.g., Toyota): ")
                model = get_user_input("Model (e.g., Camry): ")
                year = get_user_input("Year (e.g., 2020): ", int)
                price = get_user_input("Price (e.g., 25000.50): ", float)
                vin = get_user_input("VIN (Unique 17 Chars): ")
                
                # Car creation attempts validation, raises ValueError on failure
                new_car = Car(make, model, year, price, vin) 
                manager.add_car(new_car)

            except ValueError as e:
                # Catch validation errors from the Car class
                print(f"Validation Error: {e}")

        elif choice == 2:
            manager.view_inventory()

        elif choice == 3:
            query = get_user_input("Enter search query (Make or Model): ")
            manager.search_cars(query)

        elif choice == 4:
            vin_to_remove = get_user_input("Enter VIN of the car to remove (sell): ")
            if manager.remove_car(vin_to_remove):
                manager.save_data()
                manager.save_sales_history() # NEW: Save sales history after sale

        elif choice == 5: # NEW: Handle View Sales History
            manager.view_sales_history()

        elif choice == 6:
            # Save the current state and terminate the program
            manager.save_data()
            manager.save_sales_history() # NEW: Save sales history before exit
            print("Application closed. Goodbye!")
            break

        elif choice == 7: # Exit without saving is now option 7
            print("Exiting application without saving changes. Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

# Standard Python entry point: run main() only if the script is executed directly
if __name__ == "__main__":
    main()