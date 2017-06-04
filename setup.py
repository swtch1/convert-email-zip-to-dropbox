from setuptools import find_packages, setup

with open('requirements.txt', 'r') as f:
    INSTALL_REQUIRES = [line.replace('\n', '') for line in f.readlines()]

setup(
    name='extract_zipped_email_attachments',
    author='Joshua Thornton',
    author_email='thornton.joshua@gmail.com',
    version='0.1',
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES
)