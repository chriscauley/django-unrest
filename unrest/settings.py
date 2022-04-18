# usage: (in project settings file)
# from unrest.settings import get_secret_key
# SECRET_KEY = get_secret_key(BASE_DIR)

import os
from django.core.management.utils import get_random_secret_key

def get_secret_key(BASE_DIR):
    key_path = os.path.join(BASE_DIR, '.secret_key')
    if os.path.exists(key_path):
        with open(key_path, 'r') as f:
            SECRET_KEY = f.read()
    else:
        SECRET_KEY = get_random_secret_key()
        with open(key_path, 'w') as f:
            f.write(SECRET_KEY)
            print('wrote secret key to', key_path)

    return SECRET_KEY