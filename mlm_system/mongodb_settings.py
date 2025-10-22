"""
MongoDB specific settings for Railway deployment
"""
from .settings import *

# MongoDB configuration
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': os.getenv('MONGO_DB_NAME', 'mlm_system'),
        'CLIENT': {
            'host': os.getenv('MONGO_URL', 'mongodb://localhost:27017/'),
            'username': os.getenv('MONGO_USERNAME', ''),
            'password': os.getenv('MONGO_PASSWORD', ''),
            'authSource': os.getenv('MONGO_AUTH_SOURCE', 'admin'),
        }
    }
}

# MongoDB specific settings
MONGO_SETTINGS = {
    'AUTHENTICATION_SOURCE': 'admin',
    'AUTHENTICATION_MECHANISM': 'SCRAM-SHA-1',
    'SSL': True,
    'SSL_CERT_REQS': 0,
    'RETRY_WRITES': True,
    'MAX_POOL_SIZE': 10,
    'MIN_POOL_SIZE': 1,
    'MAX_IDLE_TIME_MS': 30000,
    'SERVER_SELECTION_TIMEOUT_MS': 5000,
    'CONNECT_TIMEOUT_MS': 10000,
    'SOCKET_TIMEOUT_MS': 20000,
}
