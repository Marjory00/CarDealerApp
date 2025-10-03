# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from dealer_manager import DealerManager
from car import Car

# Initialize Flask application
app = Flask(__name__)

# Set Secret Key for Flashing/Session Management
# NOTE: Use a complex, random key in production
app.secret_key = 'your_strong_secret_key' 

# Initialize the Dealer Manager (loads data from cars.json)
manager = DealerManager()

@app.route('/')
def index():
    """Renders the main inventory page, handling search/filtering."""
    
    # Retrieves the 'query' parameter from the URL, if present
    search_query = request.args.get('query', '').strip()
    
    if search_query:
        # Filter inventory if a search query is provided
        inventory_list = manager.search_cars(search_query)
    else:
        # Show full inventory otherwise
        inventory_list = manager.inventory
    
    return render_template('index.html', 
                           inventory=inventory_list, 
                           search_query=search_query)

@app.route('/add', methods=['GET', 'POST'])
def add_car_route():
    """Handles displaying the form and processing new car submissions."""
    form_data = {}  # Used to repopulate the form on error
    error_message = None

    if request.method == 'POST':
        form_data = request.form.to_dict()
        make = form_data.get('make')
        model = form_data.get('model')
        vin = form_data.get('vin', '').upper() # Default to empty string for safety

        try:
            # Safely attempt type conversion for numeric fields
            year = int(form_data.get('year'))
            price = float(form_data.get('price'))
            
            new_car = Car(make, model, year, price, vin)
            
            # Use the manager's logic for adding and validation
            if manager.add_car(new_car):
                manager.save_data()
                flash(f"Successfully added {make} {model}!", 'success')
                return redirect(url_for('index'))
            else:
                # If manager.add_car returns False (e.g., VIN duplicate/invalid)
                error_message = f"Error adding car. Check VIN and ensure VIN '{vin}' is unique and valid (17 chars)."

        except ValueError:
            error_message = "Invalid input for Year or Price. Please check that they are numeric."
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"

    # Renders the form on GET or on POST error (with repopulated data)
    return render_template('add_car.html', error=error_message, form_data=form_data)

@app.route('/sell/<vin>')
def sell_car_route(vin):
    """Handles selling/removing a car by VIN."""
    
    if manager.remove_car(vin):
        manager.save_data()
        flash(f"Vehicle with VIN {vin} sold and removed!", 'success')
    else:
        flash(f"Error: Could not find car with VIN {vin} to sell.", 'danger')
    
    return redirect(url_for('index'))

@app.route('/edit/<vin>', methods=['GET', 'POST'])
def edit_car_route(vin):
    """Handles displaying the edit form and processing updates."""
    car = manager.find_car_by_vin(vin)
    
    if not car:
        flash(f"Error: Car with VIN {vin} not found.", 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            # Safely retrieve and convert updated data
            new_year = int(request.form.get('year'))
            new_price = float(request.form.get('price'))
            
            # Use the manager method to apply updates (which includes validation)
            if manager.edit_car(vin, new_price=new_price, new_year=new_year):
                manager.save_data()
                flash(f"Details for VIN {vin} updated successfully!", 'success')
                return redirect(url_for('index'))
            else:
                # If edit_car returns False due to invalid data (e.g., negative price)
                # The console will show the error, but we need friendly UI feedback:
                error_message = "Update failed. Check year/price validity (e.g., must be positive)."
                return render_template('edit_car.html', car=car, error=error_message)


        except ValueError:
            error_message = "Invalid input format. Year and Price must be numeric."
            return render_template('edit_car.html', car=car, error=error_message)

    # Renders the form on GET request
    return render_template('edit_car.html', car=car)


if __name__ == '__main__':
    app.run(debug=True)