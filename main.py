# main.py

from dealer_manager import DealerManager
from car import Car
import sys 

# --- Utility Functions for Input ---

def get_user_input(prompt, data_type=str):
    """
    Utility function to get input and handle basic type casting.
    Returns None if input is empty and data_type is None, or if 's'/'skip' is entered.
    """
    while True:
        try:
            user_input = input(prompt).strip()
            
            # Case 1: Allow skip for numeric inputs (used in edit/update)
            if user_input.lower() in ['s', 'skip']:
                 return None 

            # Case 2: Allow skip for prompts where any empty string is a valid skip/None value
            if not user_input and data_type is None:
                return None 
            
            # Case 3: Require non-empty input for standard string/required type prompts
            if not user_input and data_type is not None:
                print("Input cannot be empty.")
                continue
            
            # Case 4: Cast input to required type
            return data_type(user_input)
        
        except ValueError:
            print(f"Invalid format. Please enter a valid {data_type.__name__}.")
        except Exception as e:
            print(f"An unexpected input error occurred: {e}")


def view_inventory(manager):
    """Prints the entire current inventory to the console."""
    inventory = manager.get_inventory()
    if not inventory:
        print("\nThe inventory is currently empty.")
        return

    print("\n--- Current Inventory ---")
    # Inventory list comprehension is now in the manager, this just displays it
    for i, car in enumerate(inventory):
        print(f"[{i+1}]: {car}") # Car.__str__ is called here
    print("-" * 25)


# --- Core Application Loop ---

def run_edit_car_interface(manager):
    """Handles the user interaction for editing a car's details."""
    try:
        vin_to_edit = get_user_input("Enter VIN of the car to edit: ").upper()
        
        # Check if the car exists first
        car = manager.find_car_by_vin(vin_to_edit)
        if not car:
            print(f"Error: Car with VIN {vin_to_edit} not found.")
            return

        print(f"\n--- Editing Car: {car} ---")
        print("Leave input blank or type 's' to skip updating a field.")

        # Gather inputs, allowing None/skip
        new_price = get_user_input(f"New Price (Current: ${car.price:,.2f}): ", data_type=float)
        new_year = get_user_input(f"New Year (Current: {car.year}): ", data_type=int)

        # Apply changes only if something was entered
        if new_price is not None or new_year is not None:
            # The manager's edit_car method handles all validation
            if manager.edit_car(vin_to_edit, new_price=new_price, new_year=new_year):
                 print(f"Successfully updated car with VIN {vin_to_edit}.")
            # If edit_car fails, it will raise a ValueError that the outer try/except catches
        else:
            print("No changes made.")

    except ValueError as e:
        # Catch validation errors or 'car not found' from the DealerManager.edit_car
        print(f"Edit failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during the edit: {e}")


def main():
    """Main application loop and menu control. (UPDATED)"""
    manager = DealerManager()

    while True:
        # Display the main menu (Updated to include Sales History)
        print("\n===== Car Dealer App =====")
        print("1. Add New Car")
        print("2. View All Inventory")
        print("3. Search Cars (Make/Model)")
        print("4. Sell/Remove Car (by VIN)")
        print("5. Edit Car Details (by VIN)")
        print("6. View Sales History & Report") # NEW menu option
        print("7. Save & Exit")
        print("8. Exit without Saving")
        print("-" * 25)
        
        choice = get_user_input("Enter your choice (1-8): ", int)

        if choice == 1:
            print("\n--- Enter Car Details ---")
            
            try:
                # Get non-numeric inputs first
                make = get_user_input("Make: ")
                model = get_user_input("Model: ")
                vin = get_user_input("VIN (17 characters): ").upper()
                
                # Get numeric inputs (these will raise ValueError if invalid format)
                year = get_user_input("Year (e.g., 2022): ", int)
                price = get_user_input("Price (e.g., 35000.00): ", float)
                
                # Car validation happens here (Car.__init__ will raise ValueError)
                new_car = Car(make, model, year, price, vin)
                manager.add_car(new_car)
                
            except ValueError as e:
                # Catch validation errors from Car.__init__ or input conversion errors
                print(f"Could not create car object due to input error: {e}")

        elif choice == 2:
            view_inventory(manager) # Use local helper function

        elif choice == 3:
            query = get_user_input("Enter search query (Make or Model): ")
            results = manager.search_cars(query)
            if results:
                print(f"\n--- Search Results for '{query}' ---")
                for car in results:
                    print(car)
                print("-" * 35)
            else:
                 print(f"No results found for '{query}'.")

        elif choice == 4:
            vin_to_remove = get_user_input("Enter VIN of the car to remove (sell): ").upper()
            if manager.remove_car(vin_to_remove):
                # Save both files after a successful transaction
                manager.save_data()
                manager.save_sales_history()

        elif choice == 5:
            run_edit_car_interface(manager)
            manager.save_data() # Save inventory after successful edit

        elif choice == 6: # NEW: View Sales History
            manager.view_sales_history()
            
        elif choice == 7:
            # Save the current state and terminate the program
            manager.save_data()
            manager.save_sales_history() # MUST save sales history
            print("Application closed. Goodbye!")
            sys.exit(0)

        elif choice == 8:
            print("Exiting application without saving changes. Goodbye!")
            sys.exit(0)
            
        else:
            print("Invalid choice. Please enter a number between 1 and 8.")

if __name__ == "__main__":
    main()