
# main.py

from dealer_manager import DealerManager
from car import Car
import sys # Used for clean exit

# --- Utility Functions for Input ---

def get_user_input(prompt, data_type=str):
    """Utility function to get input and handle basic type casting."""
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input and data_type is not None:
                print("Input cannot be empty.")
                continue
            
            # Allow empty input only if data_type is explicitly None (e.g., skip edits)
            if not user_input and data_type is None:
                return None 

            if data_type == float and user_input.lower() in ['s', 'skip']: # Allow 's' or 'skip' for float/int
                return None
            
            if data_type == int and user_input.lower() in ['s', 'skip']:
                return None

            return data_type(user_input)
        
        except ValueError:
            print(f"Invalid format. Please enter a valid {data_type.__name__}.")
        except Exception as e:
            print(f"An unexpected input error occurred: {e}")

# --- Core Application Loop ---

def run_edit_car_interface(manager):
    """Handles the user interaction for editing a car's details."""
    vin_to_edit = get_user_input("Enter VIN of the car to edit: ").upper()
    car = manager.find_car_by_vin(vin_to_edit)
    
    if not car:
        print(f"Car with VIN {vin_to_edit} not found.")
        return

    print(f"\n--- Editing Car: {car} ---")
    print("Leave input blank or type 's' to skip updating a field.")

    # Get New Price
    new_price = None
    while True:
        price_input = get_user_input(f"New Price (Current: ${car.price:,.2f}): ", data_type=None)
        if price_input is None:
            break
        try:
            new_price = float(price_input)
            if new_price <= 0:
                print("Price must be a positive number.")
                continue
            break
        except ValueError:
            print("Invalid price format.")

    # Get New Year
    new_year = None
    while True:
        year_input = get_user_input(f"New Year (Current: {car.year}): ", data_type=None)
        if year_input is None:
            break
        try:
            new_year = int(year_input)
            if new_year < 1900 or new_year > 2050: # Simple validation
                print("Year must be a realistic value (1900-2050).")
                continue
            break
        except ValueError:
            print("Invalid year format.")
            
    # Apply changes only if something was entered
    if new_price is not None or new_year is not None:
        manager.edit_car(vin_to_edit, new_price=new_price, new_year=new_year)
    else:
        print("No changes made.")


def main():
    """Main application loop and menu control."""
    manager = DealerManager()

    while True:
        print("\n===== Car Dealer App =====")
        print("1. Add New Car")
        print("2. View All Inventory")
        print("3. Search Cars (Make/Model)")
        print("4. Sell/Remove Car (by VIN)")
        print("5. Edit Car Details (by VIN)")
        print("6. Save & Exit")
        print("7. Exit without Saving")
        print("-" * 25)
        
        choice = get_user_input("Enter your choice (1-7): ", int)

        if choice == 1:
            print("\n--- Enter Car Details ---")
            make = get_user_input("Make: ")
            model = get_user_input("Model: ")
            
            # Loop for valid numeric input
            year = get_user_input("Year (e.g., 2022): ", int)
            price = get_user_input("Price (e.g., 35000.00): ", float)
            vin = get_user_input("VIN (17 characters): ").upper()
            
            # Create a Car object and pass it to the manager
            try:
                new_car = Car(make, model, year, price, vin)
                manager.add_car(new_car)
            except Exception as e:
                print(f"Could not create car object due to input error: {e}")

        elif choice == 2:
            manager.view_inventory()

        elif choice == 3:
            query = get_user_input("Enter search query (Make or Model): ")
            manager.search_cars(query)

        elif choice == 4:
            vin_to_remove = get_user_input("Enter VIN of the car to remove (sell): ").upper()
            manager.remove_car(vin_to_remove)

        elif choice == 5:
            run_edit_car_interface(manager)

        elif choice == 6:
            manager.save_data()
            print("Application closed. Goodbye!")
            sys.exit(0)

        elif choice == 7:
            print("Exiting application without saving changes. Goodbye!")
            sys.exit(0)
            
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    main()