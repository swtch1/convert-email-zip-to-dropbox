import anyconfig

import os

CUR_DIR = os.path.dirname(__file__)

config = anyconfig.load(os.path.join(CUR_DIR, 'config.yml'))
auth = anyconfig.load(os.path.join(CUR_DIR, 'auth.yml'))
