
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
    if request.method == 'POST':
        # Get data from the submitted form
        make = request.form.get('make')
        model = request.form.get('model')
        # Use try/except for safer type conversion from web form data
        try:
            year = int(request.form.get('year'))
            price = float(request.form.get('price'))
            vin = request.form.get('vin').upper()
            
            new_car = Car(make, model, year, price, vin)
            
            if manager.add_car(new_car):
                manager.save_data() # Save immediately after adding
                return redirect(url_for('index'))
            else:
                # If manager.add_car returns False (e.g., VIN duplicate/invalid)
                error_message = f"Error adding car. Check VIN: {vin}"
                return render_template('add_car.html', error=error_message)

        except ValueError:
            error_message = "Invalid input for Year or Price. Please check format."
            return render_template('add_car.html', error=error_message)

    # Renders the empty form on GET request
    return render_template('add_car.html')

@app.route('/sell/<vin>')
def sell_car_route(vin):
    """Handles selling/removing a car by VIN."""
    if manager.remove_car(vin):
        manager.save_data()
    # Redirect back to the inventory page
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Flask will run on http://127.0.0.1:5000/
    app.run(debug=True)