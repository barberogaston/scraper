from setuptools import setup, find_packages

setup(
    name='scraper',
    version='0.0.1',
    author='R. Gastón Barbero',
    author_email='barberorodrigogaston@gmail.com',
    packages=find_packages(where='.'),
    install_requires=['scrapy']
)
