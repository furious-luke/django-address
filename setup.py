import os
from setuptools import setup, find_packages

setup(
    name='django-address',
    version='0.1.3',
    author='Luke Hodkinson',
    author_email='furious.luke@gmail.com',
    maintainer='Luke Hodkinson',
    maintainer_email='furious.luke@gmail.com',
    url='https://github.com/furious-luke/django-address',
    description='A django application for describing addresses.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    license='BSD',

    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.txt', '*.js', '*.html', '*.*']},
    install_requires=['setuptools'],
    zip_safe=False,

)
