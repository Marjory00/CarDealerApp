# web_app.py (FIXED version for robust template loading)

from flask import Flask, render_template, request, redirect, url_for
from dealer_manager import DealerManager, DATA_FILE, SALES_FILE
from car import Car
import os # <-- IMPORT ADDED HERE

# --- FIX: Explicitly define the template folder path ---
# This ensures Flask finds the 'templates' directory even if the script 
# is executed from a different location.
basedir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(basedir, 'templates')

# Initialize Flask application with the explicit path
app = Flask(__name__, template_folder=template_dir) 
# --------------------------------------------------------

# Initialize the DealerManager (uses existing cars.json and sales.json)
manager = DealerManager(file_path=DATA_FILE, sales_file=SALES_FILE)

@app.route('/')
def index():
    """
    Renders the main landing page, including the platform overview and inventory list.
    This acts as the main page and inventory display.
    """
    inventory = manager.get_inventory()
    
    # Hardcoded featured models for the 'Models Display' section
    featured_models = [
        {"name": "Ford Mustang (Classic)", "engine": "V8", "status": "Iconic Muscle"},
        {"name": "Tesla Model 3 (Modern EV)", "engine": "Electric", "status": "Electric Future"},
        {"name": "Honda CR-V (Reliable SUV)", "engine": "I4", "status": "Family Favorite"},
    ]

    return render_template(
        'index.html', 
        inventory=inventory,
        total_cars=len(inventory),
        featured_models=featured_models
    )

@app.route('/info/<section>')
def info(section):
    """Renders the Contact, Services, or About sections."""
    data = {}
    if section == 'contact':
        data = {
            "title": "Contact Us",
            "content": ["Phone: (555) CAR-DEAL", "Email: info@python-dealer.com", "Address: 123 Code Street, Command City, USA"]
        }
    elif section == 'services':
        data = {
            "title": "Our Services",
            "content": ["Financing & Lease Programs", "Certified Pre-Owned Vehicle Inspection", "Full-Service Maintenance Department", "Vehicle Trade-Ins & Appraisals"]
        }
    elif section == 'about':
        data = {
            "title": "About Python Dealer App",
            "content": ["The Python Dealer App has been serving the command line community since 2023.", "We pride ourselves on data integrity and exceptional customer service.", "We are powered entirely by Python and JSON."]
        }
    else:
        return redirect(url_for('index'))
    
    return render_template('info.html', **data)

@app.route('/add_car', methods=['GET', 'POST'])
def add_car_web():
    """Simple form for adding a new car."""
    if request.method == 'POST':
        try:
            make = request.form['make']
            model = request.form['model']
            vin = request.form['vin'].upper()
            year = int(request.form['year'])
            price = float(request.form['price'])
            image_url = request.form['image_url']
            
            new_car = Car(make, model, year, price, vin, image_url=image_url)
            manager.add_car(new_car)
            manager.save_data()
            return redirect(url_for('index'))
        except (ValueError, TypeError) as e:
            return render_template('add_car.html', error=str(e))
        
    return render_template('add_car.html')

if __name__ == '__main__':
    print("Starting Flask Web App. Navigate to http://127.0.0.1:5000/")
    # You may need to remove debug=True in a production environment
    app.run(debug=True)