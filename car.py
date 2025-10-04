# car.py


from datetime import date
from typing import Dict, Any, Tuple

class Car:
    """
    Represents a single car in the inventory, handling data validation 
    and dictionary serialization.
    """
    def __init__(self, make: str, model: str, year: int, price: float, vin: str, image_url: str = ""):
        """Initializes a new Car instance with validation."""
        
        # 1. Clean and validate all inputs, assigning the cleaned/validated values
        # FIX: _validate_input now returns all five cleaned attributes (str, str, int, float, str)
        cleaned_make, cleaned_model, validated_year, validated_price, cleaned_vin = \
            self._validate_input(make, model, year, price, vin)
        
        # 2. Assign validated and cleaned attributes
        self.make = cleaned_make
        self.model = cleaned_model
        self.year = validated_year
        self.price = validated_price
        self.vin = cleaned_vin
        self.image_url = image_url.strip() if image_url.strip() else "/static/placeholder.png" # Default image path

    def _validate_input(self, make: str, model: str, year: Any, price: Any, vin: str) -> Tuple[str, str, int, float, str]:
        """Internal method to validate and clean all required fields and return them."""
        
        # 0. Clean string inputs first
        make = str(make).strip()
        model = str(model).strip()
        vin = str(vin).strip()
        
        # 1. Make/Model Validation and Cleaning
        if not make or not model:
            raise ValueError("Make and model cannot be empty.")
        
        cleaned_make = make.title()
        cleaned_model = model.title()
        
        # 2. VIN Validation and Cleaning
        if not vin or len(vin) != 17 or not vin.isalnum():
            raise ValueError("VIN must be exactly 17 alphanumeric characters.")
        
        cleaned_vin = vin.upper()
        
        # 3. Year Validation
        try:
            validated_year = int(year)
        except (TypeError, ValueError):
            raise ValueError("Year must be a valid integer.")
            
        current_year = date.today().year
        # Allow 2 years into the future (e.g., in 2025, allow up to 2027)
        if not (1900 <= validated_year <= current_year + 2):
            raise ValueError(f"Year must be between 1900 and {current_year + 2}.")
            
        # 4. Price Validation
        try:
            # Ensure price is cast to float and is positive
            validated_price = float(price)
            if validated_price <= 0:
                raise ValueError("Price must be a positive number.")
        except (TypeError, ValueError):
            raise ValueError("Price must be a valid number.")
            
        # Return all validated and cleaned attributes
        return cleaned_make, cleaned_model, validated_year, validated_price, cleaned_vin 

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
        return f"{self.year} {self.make} {self.model} (VIN: {self.vin}, Price: ${self.price:,.2f})"