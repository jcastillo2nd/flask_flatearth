"""
Flask-FlatEarth
---------------

A static content generator based on flask, built with Frozen-Flask in mind.
"""
from setuptools import setup


setup(name='Flask-FlatEarth',
      version='0.1',
      url='https://github.com/jcastillo2nd/flask_flatearth',
      license='MIT',
      author='Javier Castillo II',
      autor_email='jcastillo.webservices@gmail.com',
      description='A static content generator based on Flask',
      long_description=__doc__,
      packages=['flask_flatearth',
                'flask_flatearth.ext',
                'flask_flatearth.ext.topics',
                'flask_flatearth.markdown'],
      zip_safe=False,
      include_package_data=True,
      platforms='any',
      install_requires=['Flask',
                        'markdown'],
      classifiers=[
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ]
)

