from django.core.management.utils import get_random_secret_key

# simple key generation
print(get_random_secret_key())

# Also valid:
# import secrets
# print(secrets.token_hex(100))
