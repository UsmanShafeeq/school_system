from django.utils import timezone
from django.core.exceptions import ValidationError
def generate_student_roll_no():
    # Get the current date and time
    current_date = timezone.now()
    
    # Extract the last two digits of the current year
    current_year = str(current_date.year)[-2:]
    
    # Initialize the roll number prefix with the current year
    base_serial_number = f"{current_year}"
    
    # Check if any students have a roll number starting with the current year
    if Student.objects.filter(roll_no__startswith=base_serial_number).exists():
        # If students exist, calculate the next serial suffix based on the count
        serial_suffix = Student.objects.filter(roll_no__startswith=base_serial_number).count() + 1
    else:
        # If no students exist, start the suffix at 1
        serial_suffix = 1
    
    # Create the initial roll number with zero-padded suffix
    roll_no = f"{base_serial_number}{str(serial_suffix).zfill(4)}"
    
    # Ensure the roll number is unique
    while Student.objects.filter(roll_no=roll_no).exists():
        serial_suffix += 1  # Increment the serial suffix
        roll_no = f"{base_serial_number}{str(serial_suffix).zfill(4)}"  # Generate a new roll number
    
    return roll_no  # Return the generated roll number


def validate_cnic(value):
    """
    Validate the CNIC (Computerized National Identity Card) number.

    The CNIC must consist of 13 digits, and if the input does not contain hyphens,
    it will be formatted to the standard CNIC format.

    Args:
        value (str): The CNIC value to validate.

    Returns:
        str: The formatted CNIC if valid, otherwise raises a ValidationError.
    """
    # Check if the value is not empty
    if value:
        # Remove any hyphens from the CNIC
        cleaned = value.replace('-', '')  

        # Check if it's composed of digits and has a length of 13
        if not cleaned.isdigit() or len(cleaned) != 13:
            raise ValidationError('CNIC must have 13 digits.')

        # If the original value doesn't have hyphens, format it to include them
        if '-' not in value:
            value = f"{cleaned[:5]}-{cleaned[5:12]}-{cleaned[12]}"

    return value  # Return the formatted or original valid CNIC
