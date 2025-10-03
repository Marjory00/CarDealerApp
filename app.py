# app.py

from flask import Flask, render_template, request, redirect, url_for
from dealer_manager import DealerManager
from car import Car

# Initialize Flask application
app = Flask(__name__)

# Initialize the Dealer Manager
manager = DealerManager()

@app.route('/')
def index():
    """Renders the main inventory page."""
    # Pass the entire inventory list to the HTML template
    return render_template('index.html', inventory=manager.inventory)

@app.route('/add', methods=['GET', 'POST'])
def add_car_route():
    """Handles displaying the form and processing new car submissions."""
    form_data = {}  # Dictionary to hold data to re-populate the form on error
    error_message = None

    if request.method == 'POST':
        # Get all form data
        form_data = request.form.to_dict()
        make = form_data.get('make')
        model = form_data.get('model')
        vin = form_data.get('vin').upper()

        try:
            # Use try/except for safer type conversion from web form data
            year = int(form_data.get('year'))
            price = float(form_data.get('price'))
            
            new_car = Car(make, model, year, price, vin)
            
            if manager.add_car(new_car):
                manager.save_data() # Save immediately after adding
                return redirect(url_for('index'))
            else:
                # If manager.add_car returns False (e.g., VIN duplicate/invalid)
                # Note: The error is generated within dealer_manager.py's add_car method
                error_message = f"Error adding car. Check VIN and ensure VIN '{vin}' is unique and valid (17 chars)."

        except ValueError:
            error_message = "Invalid input for Year or Price. Please check that they are numeric."
        except Exception as e:
            # Catch other potential errors during Car creation
            error_message = f"An unexpected error occurred: {e}"

    # Renders the form on GET request OR on POST error
    # Pass both the error message and the form data back
    return render_template('add_car.html', error=error_message, form_data=form_data)

@app.route('/sell/<vin>')
def sell_car_route(vin):
    """Handles selling/removing a car by VIN."""
    if manager.remove_car(vin):
        manager.save_data()
    # Redirect back to the inventory page
    return redirect(url_for('index'))

@app.route('/edit/<vin>', methods=['GET', 'POST'])
def edit_car_route(vin):
    """Handles displaying the edit form and processing updates for a specific car."""
    car = manager.find_car_by_vin(vin)
    
    if not car:
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            # Safely retrieve and convert updated data
            new_year = int(request.form.get('year'))
            new_price = float(request.form.get('price'))
            
            manager.edit_car(vin, new_price=new_price, new_year=new_year)
            manager.save_data()
            
            return redirect(url_for('index'))

        except ValueError:
            error_message = "Invalid input for Year or Price. Please check format."
            return render_template('edit_car.html', car=car, error=error_message)

    # Renders the form on GET request, passing the current car object
    return render_template('edit_car.html', car=car)


if __name__ == '__main__':
    # Flask will run on http://127.0.0.1:5000/
    app.run(debug=True)