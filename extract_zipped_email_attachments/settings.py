import yaml

import os

CUR_DIR = os.path.dirname(__file__)
with open(os.path.join(CUR_DIR, 'config.yml')) as f:
    config = yaml.load(f)
with open(os.path.join(CUR_DIR, 'auth.yml')) as f:
    auth = yaml.load(f)
