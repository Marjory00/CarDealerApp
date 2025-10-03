
# car.py

class Car:
    """
    Represents a single vehicle in the dealer's inventory.
    """
    
    def __init__(self, make, model, year, price, vin):
        """Initializes a new Car object, casting year and price to numbers."""
        self.make = make.strip().title()
        self.model = model.strip().title()
        # Basic validation and type casting
        self.year = int(year)
        self.price = float(price)
        self.vin = vin.strip().upper() # VINs are typically uppercase

    def to_dict(self):
        """
        Returns a dictionary representation of the car for saving to JSON.
        This is necessary because JSON cannot directly serialize class instances.
        """
        return {
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'price': self.price,
            'vin': self.vin
        }

    def __str__(self):
        """
        Provides a clean, user-friendly string representation of the car
        for printing inventory lists.
        """
        # Formats the price with commas (e.g., $25,000.00)
        return (f"VIN: {self.vin} | {self.year} {self.make} {self.model} "
                f"| Price: ${self.price:,.2f}")