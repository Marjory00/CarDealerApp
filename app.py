# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from dealer_manager import DealerManager
from car import Car
import operator # Used for efficient sorting by attribute

# Initialize Flask application
app = Flask(__name__)

# Set Secret Key for Flashing/Session Management
# NOTE: Use a complex, random key in production
app.secret_key = 'your_strong_secret_key' 

# Initialize the Dealer Manager (loads data from cars.json and sales.json)
manager = DealerManager()

@app.route('/')
def index():
    """Renders the main inventory page, handling search/filtering and sorting."""
    
    # 1. Handle Search/Filtering
    search_query = request.args.get('query', '').strip()
    
    if search_query:
        # Filter inventory if a search query is provided
        inventory_list = manager.search_cars(search_query)
    else:
        # Show full inventory otherwise
        inventory_list = manager.inventory

    # 2. Handle Sorting (NEW)
    # Get the column to sort by (e.g., 'make', 'price')
    sort_by = request.args.get('sort', 'vin')
    # Determine sort direction (default is False=Ascending; Toggle for Descending)
    current_direction = request.args.get('direction', 'asc')
    reverse_sort = (current_direction == 'desc') # True if we want descending

    # Only sort if the list is not empty and the attribute exists on the Car object
    if inventory_list and hasattr(inventory_list[0], sort_by):
        # Use operator.attrgetter for fast, reliable sorting by attribute
        inventory_list = sorted(inventory_list, 
                                key=operator.attrgetter(sort_by), 
                                reverse=reverse_sort)
        
    # Determine the direction for the NEXT click (Toggling)
    next_direction = 'asc' if current_direction == 'desc' else 'desc'
    
    return render_template('index.html', 
                           inventory=inventory_list, 
                           search_query=search_query,
                           current_sort=sort_by,             # Pass the current sort column
                           current_direction=current_direction, # Pass the current direction
                           next_direction=next_direction)     # Pass the next direction for the template links

@app.route('/add', methods=['GET', 'POST'])
def add_car_route():
    """Handles displaying the form and processing new car submissions."""
    form_data = {}  # Used to repopulate the form on error
    error_message = None

    if request.method == 'POST':
        form_data = request.form.to_dict()
        make = form_data.get('make')
        model = form_data.get('model')
        vin = form_data.get('vin', '').upper()

        try:
            year = int(form_data.get('year'))
            price = float(form_data.get('price'))
            
            new_car = Car(make, model, year, price, vin)
            
            if manager.add_car(new_car):
                manager.save_data()
                flash(f"Successfully added {make} {model}!", 'success')
                return redirect(url_for('index'))
            else:
                error_message = f"Error adding car. Check VIN and ensure VIN '{vin}' is unique and valid (17 chars)."

        except ValueError:
            error_message = "Invalid input for Year or Price. Please check that they are numeric."
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"

    return render_template('add_car.html', error=error_message, form_data=form_data)

@app.route('/sell/<vin>')
def sell_car_route(vin):
    """Handles selling/removing a car by VIN."""
    
    if manager.remove_car(vin):
        # FIX: Ensure both data files are saved after a sale
        manager.save_data()          # Saves inventory (cars.json)
        manager.save_sales_history() # Saves sales record (sales.json)
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
            new_year = int(request.form.get('year'))
            new_price = float(request.form.get('price'))
            
            if manager.edit_car(vin, new_price=new_price, new_year=new_year):
                manager.save_data()
                flash(f"Details for VIN {vin} updated successfully!", 'success')
                return redirect(url_for('index'))
            else:
                error_message = "Update failed. Check year/price validity (e.g., must be positive)."
                return render_template('edit_car.html', car=car, error=error_message)

        except ValueError:
            error_message = "Invalid input format. Year and Price must be numeric."
            return render_template('edit_car.html', car=car, error=error_message)

    return render_template('edit_car.html', car=car)


@app.route('/sales')
def sales_history_route():
    """Renders the sales history and summary page."""
    
    history = manager.sales_history
    metrics = manager.calculate_sales_metrics()
    
    return render_template('sales.html', 
                           sales_history=history, 
                           metrics=metrics)


if __name__ == '__main__':
    app.run(debug=True)