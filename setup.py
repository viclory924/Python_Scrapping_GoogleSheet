from setuptools import setup, find_packages

setup(
    name         = 'appartment',
    version      = '1.0',
    packages     = find_packages(),
    package_data = {'appartment': ['spiders/*.json']},
    scripts      = ['bin/hello.py'],
    entry_points = {'scrapy': ['settings = appartment.settings']},
)