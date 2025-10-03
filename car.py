# car.py

from datetime import datetime

class Car:
    """
    Represents a single vehicle in the dealer's inventory.
    This class enforces data integrity using internal validation.
    """
    
    def __init__(self, make, model, year, price, vin):
        """Initializes a new Car object with basic input validation."""
        
        # Strip whitespace and normalize case
        self.make = make.strip()
        self.model = model.strip()
        self.vin = vin.strip().upper() # VIN is the unique identifier, stored uppercase

        # --- Internal Validation ---
        
        # 1. VIN Format Check (Crucial for uniqueness)
        if len(self.vin) != 17 or not self.vin.isalnum():
             raise ValueError("VIN must be a 17-character alphanumeric code.")

        # 2. Year Range Check
        current_year = datetime.now().year
        try:
            year_val = int(year)
            if year_val < 1900 or year_val > (current_year + 1):
                raise ValueError(f"Year {year_val} is outside a reasonable range (1900 to {current_year + 1}).")
            self.year = year_val
        except ValueError:
             # Re-raise the error with context if conversion fails
             raise ValueError("Year must be a valid integer.")


        # 3. Price Positive Check
        try:
            price_val = float(price)
            if price_val <= 0:
                raise ValueError("Price must be a positive number.")
            self.price = price_val
        except ValueError:
             # Re-raise the error with context if conversion fails
             raise ValueError("Price must be a valid numeric value.")
        
        # --- End Validation ---

    def to_dict(self):
        """Returns a dictionary representation of the car for saving to JSON."""
        return {
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'price': self.price,
            'vin': self.vin
        }

    def __str__(self):
        """Provides a user-friendly string representation (useful for debugging/CLI)."""
        return (f"VIN: {self.vin} | {self.year} {self.make} {self.model} "
                f"| Price: ${self.price:,.2f}")