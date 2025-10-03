# car.py

from datetime import date
from typing import Dict, Any

class Car:
    """
    Represents a single car in the inventory, handling data validation 
    and dictionary serialization.
    """
    def __init__(self, make: str, model: str, year: int, price: float, vin: str, image_url: str = ""):
        """Initializes a new Car instance with validation."""
        self._validate_input(make, model, year, price, vin)
        
        # Strip whitespace and title-case strings for consistency
        self.make = make.strip().title()
        self.model = model.strip().title()
        self.year = year
        self.price = price
        self.vin = vin.strip().upper()
        # image_url stores the path to the car's local image file (or "N/A")
        self.image_url = image_url.strip() if image_url.strip() else "N/A"

    def _validate_input(self, make, model, year, price, vin):
        """Internal method to validate all required fields."""
        if not make or not model:
            raise ValueError("Make and model cannot be empty.")
        
        current_year = date.today().year
        # Year validation: must be a reasonable number
        if not (1900 <= year <= current_year + 1):
            raise ValueError(f"Year must be between 1900 and {current_year + 1}.")
            
        # Price validation: must be a positive number
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValueError("Price must be a positive number.")
            
        # VIN validation: must be 17 characters long
        if not vin or len(vin) != 17:
            raise ValueError("VIN must be 17 characters long and non-empty.")

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dictionary representation for JSON serialization."""
        return {
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "price": self.price,
            "vin": self.vin,
            "image_url": self.image_url
        }

    def __str__(self) -> str:
        """Returns a user-friendly string representation of the car."""
        return (
            f"VIN: {self.vin} | {self.year} {self.make} {self.model} | "
            f"Price: ${self.price:,.2f} | Image: {self.image_url}"
        )