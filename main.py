# main.py

from dealer_manager import DealerManager
from car import Car
import sys 
import os 
from typing import Optional, Any

# --- Utility Functions for Input ---
def get_user_input(prompt: str, data_type: type = str) -> Optional[Any]:
    """
    Utility function to get input and handle basic type casting.
    Allows 's' or 'skip' to return None for numeric/optional inputs.
    """
    while True:
        try:
            user_input = input(prompt).strip()
            
            # Case 1: Allow skip for numeric/optional inputs
            if user_input.lower() in ['s', 'skip']:
                 return None 

            # Case 2: Allow empty string for optional string inputs (like image_url)
            if not user_input and data_type is str and "optional" in prompt.lower():
                 return ""

            # Case 3: Require non-empty input for standard/required type prompts
            if not user_input and data_type is not None:
                print("Input cannot be empty.")
                continue
            
            # Case 4: Cast input to required type
            return data_type(user_input)
        
        except ValueError:
            print(f"Invalid format. Please enter a valid {data_type.__name__}.")
        except Exception as e:
            print(f"An unexpected input error occurred: {e}")


def view_inventory(manager: DealerManager):
    """Prints the entire current inventory to the console."""
    inventory = manager.get_inventory()
    if not inventory:
        print("\nThe inventory is currently empty.")
        return

    print("\n--- Current Inventory (Detailed) ---")
    for i, car in enumerate(inventory):
        print(f"[{i+1}]: {car}")
    print("-" * 25)


def view_car_image(manager: DealerManager):
    """Prompts for a VIN and attempts to open the local image file."""
    print("\n--- View Car Image ---")
    vin_to_view = get_user_input("Enter VIN of the car to view image for: ").upper()
    
    car = manager.find_car_by_vin(vin_to_view) 
    
    if not car:
        print(f"Error: Car with VIN {vin_to_view} not found.")
        return

    file_path = car.image_url

    if not file_path or file_path.lower() in ["n/a", "none", ""]:
        print(f"Error: Car {car.make} {car.model} does not have an image path saved.")
        return
        
    if os.path.exists(file_path):
        try:
            # Use platform-specific commands to open the file in the default viewer
            if sys.platform.startswith('win'):
                os.startfile(file_path)
            elif sys.platform.startswith('darwin'): # macOS
                os.system(f"open \"{file_path}\"")
            else: # Linux/other POSIX systems
                os.system(f"xdg-open \"{file_path}\"")
                
            print(f"Attempting to open image: {file_path}")
            print("Check your default image viewer.")
        except Exception as e:
            print(f"Error opening image viewer: {e}")
            print("Please check your file associations.")
    else:
        print(f"Error: Local file not found at path: {file_path}")
        print("Ensure the 'car_images' folder and files exist in your project root.")


# --- Presentation/Information Functions ---

def display_model_samples():
    """Displays hardcoded information about featured car models (Model Display)."""
    print("\n===============================")
    print("🚗 FEATURED MODEL SHOWCASE 🚗")
    print("===============================")
    print("1. **Ford Mustang (Classic Muscle)**")
    print("   Engine: V8 | Horsepower: 320+ hp | Status: Iconic")
    print("   Availability: Check inventory for VIN69FORDMUSTG0003C")
    print("\n2. **Tesla Model 3 (Modern EV)**")
    print("   Range: 333 mi (Est.) | 0-60 mph: 3.1s | Status: Electric Future")
    print("   Availability: Check inventory for VIN22TESLM30000004D")
    print("\n3. **Honda CR-V (Reliable SUV)**")
    print("   Fuel Economy: 30 MPG Comb. | Seating: 5 | Status: Family Favorite")
    print("   Availability: Check inventory for VIN24HONDACRV0002B")
    print("===============================")

def display_info_submenu():
    """Handles the About, Contact, and Services menu (Information Display)."""
    while True:
        print("\n--- Dealership Information ---")
        print("1. Contact Details")
        print("2. Services Offered")
        print("3. About Us")
        print("4. Back to Main Menu")
        print("-" * 25)

        info_choice = get_user_input("Enter your choice (1-4): ", int)

        if info_choice == 1:
            print("\n--- Contact Details ---")
            print("Phone: (555) CAR-DEAL")
            print("Email: info@python-dealer.com")
            print("Address: 123 Code Street, Command City, USA")
        
        elif info_choice == 2:
            print("\n--- Services Offered ---")
            print("-> Financing & Lease Programs")
            print("-> Certified Pre-Owned Vehicle Inspection")
            print("-> Full-Service Maintenance Department")
            print("-> Vehicle Trade-Ins & Appraisals")

        elif info_choice == 3:
            print("\n--- About Us ---")
            print("The Python Dealer App has been serving the command line community since 2023.")
            print("We pride ourselves on data integrity and exceptional customer service.")
            print("We are powered entirely by Python and JSON.")

        elif info_choice == 4:
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")


def display_welcome_screen(manager: DealerManager):
    """
    Displays a rich landing page with a platform overview and a preview 
    of the inventory and featured models.
    """
    inventory = manager.get_inventory()
    
    print("\n=======================================================")
    print("             🚗 WELCOME TO THE PYTHON DEALER APP 🐍       ")
    print("=======================================================")
    
    # --- About the Platform Section ---
    print("\n--- PLATFORM OVERVIEW ---")
    print("This is your comprehensive Command-Line Inventory and Sales Manager.")
    print("We provide robust data validation, sales tracking, and local image previews.")
    print(f"Total Cars in Stock: {len(inventory)}")
    print("-" * 55)

    # --- Models and Inventory Preview Section ---
    print("--- FEATURED MODELS & INVENTORY PREVIEW ---")
    
    # Display featured models (simulates image display with text info)
    display_model_samples()
    
    print("\n--- QUICK INVENTORY SUMMARY (First 3 Cars) ---")
    if inventory:
        for i, car in enumerate(inventory[:3]):
            print(f"  [{i+1}]: {car.year} {car.make} {car.model} | ${car.price:,.0f}")
        
        if len(inventory) > 3:
            print(f"  ... and {len(inventory) - 3} more cars available.")
    else:
        print("  Inventory is empty. Use Option 1 to add a car.")
    print("-" * 55)


# --- Core Application Loop Handlers ---

def run_edit_car_interface(manager: DealerManager):
    """Handles the user interaction for editing a car's details."""
    try:
        vin_to_edit = get_user_input("Enter VIN of the car to edit: ").upper()
        
        car = manager.find_car_by_vin(vin_to_edit)
        if not car:
            print(f"Error: Car with VIN {vin_to_edit} not found.")
            return

        print(f"\n--- Editing Car: {car} ---")
        print("Type 's' or 'skip' to keep the current value.")

        new_price = get_user_input(f"New Price (Current: ${car.price:,.2f}): ", data_type=float)
        new_year = get_user_input(f"New Year (Current: {car.year}): ", data_type=int)

        if new_price is not None or new_year is not None:
            # Attempt the edit, which includes re-validation
            if manager.edit_car(vin_to_edit, new_price=new_price, new_year=new_year):
                 print(f"Successfully updated car with VIN {vin_to_edit}.")
                 # Check save status after successful edit for robustness
                 if not manager.save_data():
                    print("⚠️ WARNING: Inventory save failed after edit. Data may be lost.")
        else:
            print("No changes made.")

    except ValueError as e:
        print(f"Edit failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during the edit: {e}")


def main():
    """Main application loop and menu control."""
    manager = DealerManager()

    while True:
        
        # Display the rich Welcome Screen on every menu return
        display_welcome_screen(manager)

        # Display the operational main menu 
        print("\n===== MAIN OPERATIONS MENU =====")
        print("1. Add New Car")
        print("2. View ALL Inventory (Detailed List)")
        print("3. Search Cars (Make/Model)")
        print("4. Sell/Remove Car (by VIN)")
        print("5. Edit Car Details (by VIN)")
        print("6. View Sales History & Report")
        print("7. View Car Image (Local)")
        print("8. More Information (Contact/Services/About)")
        print("9. Save & Exit")
        print("10. Exit without Saving")
        print("-" * 30)
        
        choice = get_user_input("Enter your choice (1-10): ", int)

        if choice == 1:
            print("\n--- Enter Car Details ---")
            try:
                make = get_user_input("Make: ")
                model = get_user_input("Model: ")
                vin = get_user_input("VIN (17 characters): ").upper()
                year = get_user_input("Year (e.g., 2022): ", int)
                price = get_user_input("Price (e.g., 35000.00): ", float)
                image_url = get_user_input("Image URL (optional, e.g., car_images/car.jpg): ", data_type=str)

                new_car = Car(make, model, year, price, vin, image_url=image_url) 
                manager.add_car(new_car)
            except ValueError as e:
                print(f"Could not create car object due to input error: {e}")

        elif choice == 2:
            view_inventory(manager)

        elif choice == 3:
            query = get_user_input("Enter search query (Make or Model): ")
            results = manager.search_cars(query)
            count = len(results)
            
            if results:
                print(f"\n==============================")
                print(f"--- Search Results for '{query}' ({count} cars) ---")
                print("==============================")
                for car in results:
                    print(car)
                print("==============================")
            else:
                 print(f"No results found for '{query}'.")

        elif choice == 4:
            vin_to_remove = get_user_input("Enter VIN of the car to remove (sell): ").upper()
            if manager.remove_car(vin_to_remove):
                # Save check after successful sale
                inventory_ok = manager.save_data()
                sales_ok = manager.save_sales_history()
                
                if not inventory_ok or not sales_ok:
                    print("⚠️ WARNING: One or both files failed to save after sale. Data loss possible.")

        elif choice == 5:
            run_edit_car_interface(manager)

        elif choice == 6: 
            manager.view_sales_history()

        elif choice == 7:
            view_car_image(manager)

        elif choice == 8:
            display_info_submenu()
            
        elif choice == 9: # Save & Exit
            print("\nAttempting to save data...")
            inventory_saved = manager.save_data()
            sales_saved = manager.save_sales_history()
            
            if inventory_saved and sales_saved:
                print("Application closed. Goodbye! 👋")
                sys.exit(0)
            else:
                # Critical save failure before exit with user confirmation
                print("\n🚨 CRITICAL ERROR: Could not save all data.")
                confirm = get_user_input("Exit anyway? (y/n): ", str)
                if confirm and confirm.lower() == 'y':
                    sys.exit(0)
                else:
                    print("Returning to main menu.")

        elif choice == 10: # Exit without Saving
            print("Exiting application without saving changes. Goodbye! 🚪")
            sys.exit(0)
            
        else:
            print("Invalid choice. Please enter a number between 1 and 10.")

if __name__ == "__main__":
    main()