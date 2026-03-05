# core/validators.py
import re
from django.core.exceptions import ValidationError

def validate_lr_number(value: str):
    # Accepts formats: LR/209/12345  or  Nairobi/Block 123/456
    pattern = r'^[A-Za-z0-9\s\/\-\.]+$'
    if not re.match(pattern, value.strip()):
        raise ValidationError("Invalid LR Number format.")
    if len(value.strip()) < 5:
        raise ValidationError("LR Number too short.")

def validate_kenyan_price(value: int):
    if value < 10000:
        raise ValidationError("Price must be at least KES 10,000.")
    if value > 10_000_000_000:
        raise ValidationError("Price exceeds maximum allowed.")