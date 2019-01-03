from setuptools import setup

with open("README.md", "r") as fh:
  long_description = fh.read()

setup(
  name = 'django-unrest',
  packages = ['unrest'],
  version = '0.0.1',
  description = 'A collection of tools for django',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author = 'Chris Cauley',
  author_email = 'chris@lablackey.com',
  url = 'https://github.com/chriscauley/django-unrest',
  keywords = ['utils','django'],
  license = 'GPL',
  include_package_data = True,
)
