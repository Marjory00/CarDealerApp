# app.py (FINAL FIXED VERSION with datetime import)

from flask import Flask, render_template, request, redirect, url_for, flash
from dealer_manager import DealerManager
from car import Car
import operator
import datetime # FIX: Import datetime for getting the current year

# Initialize Flask application
app = Flask(__name__)

# Set Secret Key for Flashing/Session Management
app.secret_key = 'your_strong_secret_key' 

# Initialize the Dealer Manager
manager = DealerManager()

# Utility to calculate max valid year for car production
MAX_YEAR = datetime.date.today().year + 2

@app.route('/')
def index():
    """Renders the main inventory page, handling search/filtering and sorting."""
    
    # 1. Handle Search/Filtering
    search_query = request.args.get('query', '').strip()
    
    if search_query:
        inventory_list = manager.search_cars(search_query) 
    else:
        inventory_list = manager.get_inventory()
        
    # 2. Handle Sorting 
    sort_by = request.args.get('sort', 'vin')
    current_direction = request.args.get('direction', 'asc')
    reverse_sort = (current_direction == 'desc') 

    if inventory_list and hasattr(inventory_list[0], sort_by):
        try:
            # FIX: Only attempt sorting if there's at least one car
            inventory_list = sorted(inventory_list, 
                                    key=operator.attrgetter(sort_by), 
                                    reverse=reverse_sort)
        except AttributeError:
            pass # Ignore if an invalid attribute is somehow passed for sorting
        
    next_direction = 'asc' if current_direction == 'desc' else 'desc'
    
    return render_template('index.html', 
                           inventory=inventory_list, 
                           search_query=search_query,
                           current_sort=sort_by,
                           current_direction=current_direction,
                           next_direction=next_direction)

@app.route('/add', methods=['GET', 'POST'])
def add_car_route():
    """Handles displaying the form and processing new car submissions."""
    form_data = {}
    error_message = None

    if request.method == 'POST':
        form_data = request.form.to_dict()
        make = form_data.get('make')
        model = form_data.get('model')
        vin = form_data.get('vin', '').upper()
        image_url = form_data.get('image_url', '')

        try:
            year = int(form_data.get('year'))
            price = float(form_data.get('price'))
            
            # Basic Year validation (ensuring it's not too far in the future/past)
            if not 1900 <= year <= MAX_YEAR:
                 raise ValueError("Year is invalid.")
            
            new_car = Car(make, model, year, price, vin, image_url=image_url) 
            
            if manager.add_car(new_car):
                manager.save_data()
                flash(f"Successfully added {make} {model}!", 'success')
                return redirect(url_for('index'))
            else:
                error_message = f"Error adding car. Car with VIN '{vin}' already exists."
                raise ValueError("Duplicate VIN.")

        except ValueError as e:
            if "Duplicate VIN" in str(e):
                pass 
            else:
                error_message = f"Validation Error: {e}. Check that Year/Price are correct."
        except Exception as e:
            error_message = f"An unexpected system error occurred: {e}"

    # FIX: Pass MAX_YEAR to the template for HTML form validation
    return render_template('add_car.html', error=error_message, form_data=form_data, max_year=MAX_YEAR)

@app.route('/sell/<vin>', methods=['GET', 'POST'])
def sell_car_route(vin):
    """Handles selling/removing a car by VIN."""
    
    if manager.remove_car(vin):
        manager.save_data()
        manager.save_sales_history()
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
            new_image_url = request.form.get('image_url')

            # Basic server-side validation for year
            if not 1900 <= new_year <= MAX_YEAR:
                raise ValueError(f"Year must be between 1900 and {MAX_YEAR}.")

            if manager.edit_car(vin, new_price=new_price, new_year=new_year, new_image_url=new_image_url):
                manager.save_data()
                flash(f"Details for VIN {vin} updated successfully!", 'success')
                return redirect(url_for('index'))
            else:
                error_message = "Update failed. Check year/price/image URL validity."
                return render_template('edit_car.html', car=car, error=error_message, max_year=MAX_YEAR)

        except ValueError as e:
            error_message = f"Invalid input format: {e}. Year and Price must be numeric and valid."
            return render_template('edit_car.html', car=car, error=error_message, max_year=MAX_YEAR)

    # FIX: Pass MAX_YEAR to the template for HTML form validation
    return render_template('edit_car.html', car=car, max_year=MAX_YEAR)


@app.route('/sales')
def sales_history_route():
    """Renders the sales history and summary page."""
    
    sales_report = manager.get_sales_report()
    
    return render_template('sales.html', 
                           sales_report=sales_report)


@app.route('/car/<vin>')
def car_detail_route(vin):
    """Renders the individual car detail page."""
    car = manager.find_car_by_vin(vin)
    if not car:
        flash(f"Error: Car with VIN {vin} not found.", 'danger')
        return redirect(url_for('index'))
    return render_template('car_detail.html', car=car)


if __name__ == '__main__':
    app.run(debug=True)