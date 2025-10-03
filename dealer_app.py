import json
import os
import sys # Import sys for clean exits (used in the final version of the CLI)

# --- Configuration ---
# Define the name of the file used for persistent storage
DATA_FILE = 'cars.json'

# --- 1. Car Class (Object-Oriented Approach) ---
class Car:
    """
    Represents a single vehicle in the dealer's inventory.
    This class serves as the data model for the application.
    """
    
    def __init__(self, make, model, year, price, vin):
        """Initializes a new Car object."""
        self.make = make.strip()
        self.model = model.strip()
        # Ensure year and price are stored in their correct numerical types
        self.year = int(year)       # Store year as integer
        self.price = float(price)   # Store price as float
        self.vin = vin.strip().upper() # Store VIN as uppercase unique identifier

    def to_dict(self):
        """
        Returns a dictionary representation of the car for saving to JSON.
        This is necessary because JSON cannot directly serialize class instances.
        """
        return {
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'price': self.price,
            'vin': self.vin
        }

    def __str__(self):
        """
        Provides a user-friendly string representation of the car for display.
        Formats the price with commas and two decimal places.
        """
        return (f"VIN: {self.vin} | {self.year} {self.make} {self.model} "
                f"| Price: ${self.price:,.2f}")


# --- 2. Dealer Manager Class (Handles Inventory & Data Persistence) ---
class DealerManager:
    """
    Manages the core inventory operations, including loading, saving,
    adding, removing, and searching for cars.
    """

    def __init__(self, file_path):
        """Initializes the manager and loads existing data."""
        self.file_path = file_path      # Path to the persistent data file (cars.json)
        self.inventory = []             # List to hold Car objects currently in memory
        self._load_data()               # Load data immediately upon initialization

    def _load_data(self):
        """Loads car data from the JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    # Recreate Car objects from the loaded dictionaries using **
                    for car_data in data:
                        self.inventory.append(Car(**car_data))
                print(f"Data loaded successfully from {self.file_path}.")
            except (IOError, json.JSONDecodeError):
                # Handle file not accessible or corrupted JSON format
                print("Could not read or parse data file. Starting with empty inventory.")
        else:
            print("Data file not found. Starting with empty inventory.")

    def save_data(self):
        """Saves the current inventory to the JSON file."""
        # Convert all Car objects back to dictionaries for JSON saving
        data = [car.to_dict() for car in self.inventory]
        try:
            with open(self.file_path, 'w') as f:
                # Use indent=4 for human-readable JSON formatting
                json.dump(data, f, indent=4)
            print(f"Inventory successfully saved to {self.file_path}.")
        except IOError:
            print("Error: Could not write to data file.")

    def add_car(self, car):
        """Adds a new Car object to the inventory after checking for duplicates."""
        # Check for duplicate VIN using a generator expression (efficient)
        if any(c.vin == car.vin for c in self.inventory):
            print(f"Error: Car with VIN {car.vin} already exists.")
            return False
        
        self.inventory.append(car)
        print(f"Added: {car.make} {car.model}")
        return True

    def view_inventory(self):
        """Prints the entire current inventory to the console."""
        if not self.inventory:
            print("\nThe inventory is currently empty.")
            return

        print("\n--- Current Inventory ---")
        # Enumerate provides both index (i) and value (car)
        for i, car in enumerate(self.inventory):
            print(f"[{i+1}]: {car}") # Display index starting from 1
        print("-" * 25)

    def search_cars(self, query):
        """Searches for cars matching the query in make or model (case-insensitive)."""
        query = query.lower().strip()
        # Use a list comprehension to efficiently filter the inventory
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
        vin = vin.strip().upper()

        # Rebuild the inventory list, excluding the car with the matching VIN
        self.inventory = [car for car in self.inventory if car.vin != vin]

        if len(self.inventory) < initial_count:
            print(f"Car with VIN {vin} sold and removed from inventory.")
            return True
        else:
            print(f"Error: Car with VIN {vin} not found.")
            return False


# --- 3. User Interface and Main Loop ---
def get_user_input(prompt, data_type=str):
    """Utility function to get input and handle basic type/empty exceptions."""
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input:
                print("Input cannot be empty.")
                continue
            # Cast the input to the required data type (str, int, float)
            return data_type(user_input)
        except ValueError:
            print(f"Invalid input. Please enter a valid {data_type.__name__}.")

def main():
    """Main function to run the CLI application loop."""
    # Initialize the manager, linking it to the data file
    manager = DealerManager(DATA_FILE)

    while True:
        # Display the main menu
        print("\n===== Car Dealer App =====")
        print("1. Add New Car")
        print("2. View All Cars")
        print("3. Search Cars (by Make/Model)")
        print("4. Sell/Remove Car (by VIN)")
        print("5. Save & Exit")
        print("6. Exit without Saving")
        
        choice = get_user_input("Enter your choice (1-6): ", int)

        if choice == 1:
            # Collect data and create the Car object
            print("\n--- Enter Car Details ---")
            make = get_user_input("Make (e.g., Toyota): ")
            model = get_user_input("Model (e.g., Camry): ")
            year = get_user_input("Year (e.g., 2020): ", int)
            price = get_user_input("Price (e.g., 25000.50): ", float)
            vin = get_user_input("VIN (Unique Identifier): ")
            
            new_car = Car(make, model, year, price, vin)
            manager.add_car(new_car)

        elif choice == 2:
            manager.view_inventory()

        elif choice == 3:
            query = get_user_input("Enter search query (Make or Model): ")
            manager.search_cars(query)

        elif choice == 4:
            vin_to_remove = get_user_input("Enter VIN of the car to remove (sell): ")
            manager.remove_car(vin_to_remove)

        elif choice == 5:
            # Save the current state and terminate the program
            manager.save_data()
            print("Application closed. Goodbye!")
            break

        elif choice == 6:
            # Terminate the program without saving recent changes
            print("Exiting application without saving changes. Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

# Standard Python entry point: run main() only if the script is executed directly
if __name__ == "__main__":
    main()