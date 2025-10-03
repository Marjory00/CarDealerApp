# car.py

class Car:
    """Represents a single vehicle in the dealer's inventory."""
    
    def __init__(self, make, model, year, price, vin):
        """Initializes a new Car object."""
        self.make = make.strip()
        self.model = model.strip()
        # Ensure year and price are stored in their correct numerical types
        self.year = int(year)
        self.price = float(price)
        self.vin = vin.strip().upper() # VIN is the unique identifier, stored uppercase

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