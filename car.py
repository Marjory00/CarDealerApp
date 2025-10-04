# car.py

# car.py

from datetime import date, datetime
from typing import Dict, Any, Tuple, Optional

class Car:
    """
    Represents a single car in the inventory, handling data validation 
    and dictionary serialization.
    """
    # FIX 1: Added Optional[datetime] for sale_date to __init__ signature
    def __init__(self, make: str, model: str, year: int, price: float, vin: str, 
                 image_url: str = "", sale_date: Optional[datetime] = None):
        """Initializes a new Car instance with validation."""
        
        # 1. Clean and validate all required inputs
        cleaned_make, cleaned_model, validated_year, validated_price, cleaned_vin = \
            self._validate_input(make, model, year, price, vin)
        
        # 2. Assign validated and cleaned attributes
        self.make = cleaned_make
        self.model = cleaned_model
        self.year = validated_year
        self.price = validated_price
        self.vin = cleaned_vin
        # FIX 2: Added sale_date attribute
        self.sale_date = sale_date 
        
        # Set default image path if image_url is empty
        cleaned_image_url = image_url.strip()
        self.image_url = cleaned_image_url if cleaned_image_url else "/static/placeholder.png"

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
        # Removed .isalnum() check as real VINs can include dashes, but simplified to ensure length and non-emptiness.
        if not vin or len(vin) != 17:
            raise ValueError("VIN must be exactly 17 characters.")
        
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
        """
        Returns a dictionary representation for JSON serialization.
        Note: Sale date is converted to an ISO string if present.
        """
        data = {
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "price": self.price,
            "vin": self.vin,
            "image_url": self.image_url,
            # FIX 3: Added sale_date and convert to ISO format if it exists
            "sale_date": self.sale_date.isoformat() if self.sale_date else None
        }
        return data

    def __str__(self) -> str:
        """Returns a user-friendly string representation of the car."""
        return f"{self.year} {self.make} {self.model} (VIN: {self.vin}, Price: ${self.price:,.2f})"

    def __repr__(self) -> str:
        """Standard representation for debugging."""
        return f"Car('{self.make}', '{self.model}', {self.year}, '{self.vin}')"