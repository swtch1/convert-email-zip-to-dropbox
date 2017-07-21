import yaml

import os

from extract_zipped_email_attachments.logger import log

CUR_DIR = os.path.dirname(__file__)
log.debug('parsing config file')
with open(os.path.join(CUR_DIR, 'config.yml')) as f:
    config = yaml.load(f)
log.debug('parsing auth file')
with open(os.path.join(CUR_DIR, 'auth.yml')) as f:
    auth = yaml.load(f)
