from distutils.core import setup

setup(
    name = 'django-popularity',
    version = "0.1",
    description = 'A generic view- and popularity tracking pluggable for Django.',
    author = 'Mathijs de Bruin',
    author_email = 'drbob@dokterbob.net',
    url = 'http://github.com/dokterbob/django-popularity',
    packages = ['popularity', 'popularity.templatetags',],
    include_package_data = True,
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
)
