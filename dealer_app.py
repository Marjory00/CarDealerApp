

import json
import os

# --- Configuration ---
DATA_FILE = 'cars.json'

# --- 1. Car Class (Object-Oriented Approach) ---
class Car:
    """Represents a car in the dealer's inventory."""
    
    def __init__(self, make, model, year, price, vin):
        """Initializes a new Car object."""
        self.make = make
        self.model = model
        self.year = int(year)  # Store year as integer
        self.price = float(price) # Store price as float
        self.vin = vin # Unique identifier

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
        """Provides a user-friendly string representation of the car."""
        return (f"VIN: {self.vin} | {self.year} {self.make} {self.model} "
                f"| Price: ${self.price:,.2f}")


# --- 2. Dealer Manager Class (Handles Inventory & Data Persistence) ---
class DealerManager:
    """Manages the inventory, including loading, saving, and operations."""

    def __init__(self, file_path):
        """Initializes the manager and loads existing data."""
        self.file_path = file_path
        self.inventory = []
        self._load_data()

    def _load_data(self):
        """Loads car data from the JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    # Recreate Car objects from the loaded dictionaries
                    for car_data in data:
                        self.inventory.append(Car(**car_data))
                print(f"Data loaded successfully from {self.file_path}.")
            except (IOError, json.JSONDecodeError):
                print("Could not read or parse data file. Starting with empty inventory.")
        else:
            print("Data file not found. Starting with empty inventory.")

    def save_data(self):
        """Saves the current inventory to the JSON file."""
        # Convert all Car objects back to dictionaries for JSON saving
        data = [car.to_dict() for car in self.inventory]
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Inventory successfully saved to {self.file_path}.")
        except IOError:
            print("Error: Could not write to data file.")

    def add_car(self, car):
        """Adds a new Car object to the inventory."""
        # Check for duplicate VIN
        if any(c.vin == car.vin for c in self.inventory):
            print(f"Error: Car with VIN {car.vin} already exists.")
            return False
        
        self.inventory.append(car)
        print(f"Added: {car}")
        return True

    def view_inventory(self):
        """Prints the entire current inventory."""
        if not self.inventory:
            print("\nThe inventory is currently empty.")
            return

        print("\n--- Current Inventory ---")
        for i, car in enumerate(self.inventory):
            print(f"[{i+1}]: {car}")
        print("-" * 25)

    def search_cars(self, query):
        """Searches for cars matching the query in make or model."""
        query = query.lower()
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

    def remove_car(self, vin):
        """Removes a car from the inventory by its VIN (Simulates a sale)."""
        initial_count = len(self.inventory)
        # Filter the inventory to exclude the car with the matching VIN
        self.inventory = [car for car in self.inventory if car.vin != vin]

        if len(self.inventory) < initial_count:
            print(f"Car with VIN {vin} sold and removed from inventory.")
            return True
        else:
            print(f"Error: Car with VIN {vin} not found.")
            return False


# --- 3. User Interface and Main Loop ---
def get_user_input(prompt, data_type=str):
    """Utility function to get input and handle basic exceptions."""
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
    """Main function to run the application."""
    manager = DealerManager(DATA_FILE)

    while True:
        print("\n===== Car Dealer App =====")
        print("1. Add New Car")
        print("2. View All Cars")
        print("3. Search Cars (by Make/Model)")
        print("4. Sell/Remove Car (by VIN)")
        print("5. Save & Exit")
        print("6. Exit without Saving")
        
        choice = get_user_input("Enter your choice (1-6): ", int)

        if choice == 1:
            # Add Car Logic
            print("\n--- Enter Car Details ---")
            make = get_user_input("Make (e.g., Toyota): ")
            model = get_user_input("Model (e.g., Camry): ")
            year = get_user_input("Year (e.g., 2020): ", int)
            price = get_user_input("Price (e.g., 25000.50): ", float)
            vin = get_user_input("VIN (Unique Identifier): ")
            
            new_car = Car(make, model, year, price, vin)
            manager.add_car(new_car)

        elif choice == 2:
            # View All Cars Logic
            manager.view_inventory()

        elif choice == 3:
            # Search Cars Logic
            query = get_user_input("Enter search query (Make or Model): ")
            manager.search_cars(query)

        elif choice == 4:
            # Sell/Remove Car Logic
            vin_to_remove = get_user_input("Enter VIN of the car to remove (sell): ")
            manager.remove_car(vin_to_remove)

        elif choice == 5:
            # Save and Exit Logic
            manager.save_data()
            print("Application closed. Goodbye!")
            break

        elif choice == 6:
            # Exit without Saving Logic
            print("Exiting application without saving changes. Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main()