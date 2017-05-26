import os

from extract_zipped_email_attachments.settings import config


def make_temp_download_dir():
    if not os.path.isdir(config['temp_download_dir']):
        os.mkdir(config['temp_download_dir'])
