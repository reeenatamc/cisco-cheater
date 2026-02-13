# Test settings - use SQLite instead of PostgreSQL for testing
from cheater.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
