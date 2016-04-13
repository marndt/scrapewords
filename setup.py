from setuptools import setup, find_packages

setup(
    name='scrapewords',
    version='0.1',
    description='Utility to scrape words from supplied URLs',
    author='Mike Arndt',
    author_email='mike@fullbeaker.com',
    url='http://fullbeaker.com/',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'scrapewords = scrapewords.scrapewords:scrapewords',
        ],
    },
    install_requires=[
        'bs4',
        'requests'
    ],
)
