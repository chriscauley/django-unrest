from setuptools import setup, find_packages

setup(
  name = 'django-unrest',
  packages = find_packages(),
  version = '0.1.5',
  description = 'A collection of tools for django',
  long_description="",
  long_description_content_type="text/markdown",
  author = 'Chris Cauley',
  author_email = 'chris@lablackey.com',
  url = 'https://github.com/chriscauley/django-unrest',
  keywords = ['utils','django'],
  license = 'MIT',
  include_package_data = True,
  install_requires = [
    'social-auth-app-django>=4.0.0',
    'social-auth-core>=3.3.3'
  ]
)
