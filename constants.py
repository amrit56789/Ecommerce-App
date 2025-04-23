# Role constants
ROLE_ADMIN = "admin"
ROLE_SELLER = "seller"
ROLE_USER = "user"
ALL_ROLES = [ROLE_ADMIN, ROLE_SELLER, ROLE_USER]

# Gender constants
GENDER_MALE = "male"
GENDER_FEMALE = "female"
GENDER_OTHER = "other"
GENDER_CHOICES = [GENDER_MALE, GENDER_FEMALE, GENDER_OTHER]

# Default admin user credentials
DEFAULT_ADMIN_EMAIL = "admin@admin.com"
DEFAULT_ADMIN_PASSWORD = "admin123"

OTP_EXPIRY_MINUTES = 10


# API Endpoint Constants
BASE_URL = '/auth'

REGISTER = f'{BASE_URL}/register'
LOGIN = f'{BASE_URL}/login'
FORGOT_PASSWORD = f'{BASE_URL}/send-email-code'
VERIFY_OTP = f'{BASE_URL}/verify-email-code'
RESET_PASSWORD = f'{BASE_URL}/reset-password'


# User API Endpoint Constants
USER_BASE_URL = '/user'

GET_USER_PROFILE = f'{USER_BASE_URL}/me'
UPDATE_PROFILE = f'{USER_BASE_URL}/update-profile'
UPDATE_PROFILE_PIC = f'{USER_BASE_URL}/update-profile-pic'
DELETE_PROFILE_PIC = f'{USER_BASE_URL}/delete-profile-pic'