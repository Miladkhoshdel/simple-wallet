"""Initialize on first run."""

import os
import random

def initialize_secret_key(secret_file):
    if os.path.isfile(secret_file):
        secret_key = open(secret_file).read().strip()
    else:
        try:
            secret_key = random_key()
            secret = open(secret_file, 'w')
            secret.write(secret_key)
            secret.close()
        except IOError:
            raise Exception('Secret file generation failed' % secret_file)
    return secret_key

def random_key():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return ''.join([random.SystemRandom().choice(chars) for i in range(50)])