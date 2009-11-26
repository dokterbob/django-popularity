from setuptools import setup, find_packages

setup(
    name = "django-popularity",
    version = "0.1",
    packages = find_packages(),
    author = "Mathijs de Bruin",
    author_email = "drbob@dokterbob.net",
    description = "Track the amount of views for objects, and generate (generic) popularity listings",
    url = "http://github.com/dokterbob/django-popularity",
    include_package_data = True,
    )
