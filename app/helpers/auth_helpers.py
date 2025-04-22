import re

def validate_email(email):
    if not email:
        return False, 'Email is required'
    if '@' not in email or '.' not in email.split('@')[-1]:
        return False, 'Invalid email format'
    return True, ''

def validate_password(password):
    if not password:
        return False, 'Password is required'
    if len(password) < 6:
        return False, 'Password must be at least 6 characters'
    
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)

    if not (has_upper and has_digit and has_special):
        return False, 'Password must contain at least one uppercase letter, one number, and one special character'
    
    return True, ''