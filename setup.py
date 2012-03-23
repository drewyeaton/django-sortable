#!/usr/bin/env python

from setuptools import setup

LONG_DESCRIPTION = '''A flexible way to handle sorting within a complex Django application.'''

CLASSIFIERS = [
                'Development Status :: 4 - Beta',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: GNU General Public License (GPL)',
                'Natural Language :: English',
                'Operating System :: OS Independent',
                'Environment :: Web Environment',
                'Framework :: Django',
                'Programming Language :: Python',
                'Topic :: Software Development :: Libraries :: Python Modules' 
              ]

KEYWORDS = 'sorting sortable queryset pagination django'

setup(name='django-sortable',
    version='0.1.1',
    description='Flexible sorting for Django applications',
    long_description=LONG_DESCRIPTION,
    author='Drew Yeaton',
    author_email='xeeton@gmail.com',
    url='http://github.com/drewyeaton/django-sortable',
    packages=['django_sortable'],    
    platforms=['Platform Independent'],
    license='GPLv3',
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    requires = ['django'],
)