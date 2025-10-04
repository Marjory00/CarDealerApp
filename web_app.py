# web_app.py (FIXED)

from flask import Flask, render_template, request, redirect, url_for, flash
from dealer_manager import DealerManager, DATA_FILE, SALES_FILE
from car import Car
import os 
from typing import Optional
import datetime 

# --- ROBUST FIX: Explicitly define the template folder path ---
basedir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(basedir, 'templates')

# Initialize Flask application with the explicit path
app = Flask(__name__, template_folder=template_dir) 
app.secret_key = 'super_secret_dealer_key' 
# -------------------------------------------------------------

# Initialize the DealerManager
manager = DealerManager(file_path=DATA_FILE, sales_file=SALES_FILE)

# Calculate max year once for use in both add and edit forms
MAX_YEAR = datetime.datetime.now().year + 2 

# Hardcoded featured models for the 'Models Display' section
FEATURED_MODELS = [
    {"name": "Ford Mustang", "engine": "V8", "status": "Iconic Muscle"},
    {"name": "Tesla Model 3", "engine": "Electric", "status": "Electric Future"},
    {"name": "Honda CR-V", "engine": "I4", "status": "Family Favorite"},
]

# --- FIX 1: Add context processor for the footer (to inject 'now' variable) ---
@app.context_processor
def inject_current_year():
    """Injects the current datetime object into all templates for use in the footer."""
    return {'now': datetime.datetime.now()}
# -----------------------------------------------------------------------------

@app.route('/')
def index():
    """Landing Page / Inventory List."""
    inventory = manager.get_inventory()
    
    # Handle search query if present
    query = request.args.get('q', '').strip()
    search_results = []
    if query:
        search_results = manager.search_cars(query)
        inventory_display = search_results
    else:
        inventory_display = inventory

    return render_template(
        'index.html', 
        inventory=inventory_display,
        total_cars=len(inventory),
        featured_models=FEATURED_MODELS,
        search_query=query,
        is_search=bool(query)
    )

@app.route('/add', methods=['GET', 'POST'])
def add_car_web():
    """Handles the Add Car form."""
    # ... (No changes needed in this function's logic) ...
    if request.method == 'POST':
        try:
            # Extract data from form
            data = {key: request.form[key] for key in ['make', 'model', 'vin', 'year', 'price']}
            # Ensure price and year are castable to correct types
            data['year'] = int(data['year'])
            data['price'] = float(data['price'])
            # Use get() for optional image_url
            data['image_url'] = request.form.get('image_url', '')

            # Use **data for clean Car instantiation (relying on Car class for validation)
            new_car = Car(**data) 
            
            if not manager.add_car(new_car):
                flash(f"Error: Car with VIN {new_car.vin} already exists.", 'error')
                # Pass max_year on error
                return render_template('add.html', form_data=request.form, max_year=MAX_YEAR) 

            manager.save_data()
            flash(f"Successfully added {new_car.make} {new_car.model} to inventory!", 'success')
            return redirect(url_for('index'))
            
        except (ValueError, TypeError) as e:
            # Catch validation errors from Car or type casting errors
            flash(f"Input Error: Please check Year, Price, and VIN format. Details: {e}", 'error')
            # Pass max_year on error
            return render_template('add.html', form_data=request.form, max_year=MAX_YEAR)
        
    # GET request: Pass max_year
    return render_template('add.html', max_year=MAX_YEAR)

@app.route('/car/<vin>')
def car_detail(vin):
    """Displays detailed information for a single car."""
    car = manager.find_car_by_vin(vin)
    if not car:
        flash(f"Error: Car with VIN {vin} not found.", 'error')
        return redirect(url_for('index'))
    return render_template('detail.html', car=car)

@app.route('/edit/<vin>', methods=['GET', 'POST'])
def edit_car_web(vin):
    """Handles the Edit Car form."""
    # ... (No changes needed in this function's logic) ...
    car = manager.find_car_by_vin(vin)
    if not car:
        flash(f"Error: Car with VIN {vin} not found.", 'error')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        new_year: Optional[int] = None
        new_price: Optional[float] = None
        new_image_url: Optional[str] = None
        
        try:
            # 1. Handle Price
            price_input = request.form['price'].strip()
            if price_input and price_input != str(car.price):
                new_price = float(price_input)
            
            # 2. Handle Image URL
            image_input = request.form.get('image_url', '').strip()
            if image_input != car.image_url:
                # Pass the input string; manager handles empty string to placeholder.
                new_image_url = image_input 
            
            # 3. Handle Year 
            year_input = request.form['year'].strip()
            if year_input and year_input != str(car.year):
                new_year = int(year_input)

            # Only proceed if at least one field has been modified or explicitly set
            if new_price is not None or new_image_url is not None or new_year is not None:
                
                # Call the updated edit_car signature
                if manager.edit_car(vin, 
                                    new_price=new_price, 
                                    new_image_url=new_image_url,
                                    new_year=new_year):
                    
                    manager.save_data()
                    flash(f"Successfully updated details for {car.make} {car.model}.", 'success')
                    return redirect(url_for('car_detail', vin=vin))
                else:
                    flash("Error updating car. Check validation (Price must be positive, Year must be valid).", 'error')
            else:
                flash("No changes detected.", 'info')

        except ValueError as e:
            flash(f"Input Error: Price or Year must be valid numbers. Details: {e}", 'error')
            # Stay on the edit page, passing back the current car object
            return render_template('edit.html', car=car, max_year=MAX_YEAR) 
            
    # GET request: Pass max_year
    return render_template('edit.html', car=car, max_year=MAX_YEAR)

@app.route('/sell/<vin>', methods=['POST'])
def sell_car_web(vin):
    """Removes a car from inventory and logs the sale."""
    car = manager.find_car_by_vin(vin)
    if not car:
        flash(f"Error: Car with VIN {vin} not found.", 'error')
        return redirect(url_for('index'))
        
    if manager.remove_car(vin):
        manager.save_data()
        manager.save_sales_history()
        flash(f"SOLD! {car.make} {car.model} has been removed and logged to sales.", 'success')
    else:
        flash("Error during sale process.", 'error')
        
    return redirect(url_for('index'))

@app.route('/sales')
def sales_report():
    """Displays the sales history and summary report."""
    report = manager.get_sales_report()
    return render_template('sales.html', report=report)

if __name__ == '__main__':
    print("Starting Flask Web App. Navigate to http://127.0.0.1:5000/")
    app.run(debug=True)