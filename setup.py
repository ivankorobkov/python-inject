# encoding: utf-8
import sys

from setuptools import setup


def read_description():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()


setup(
    name='Inject',
    version='4.3.0',
    url='https://github.com/ivankorobkov/python-inject',
    license='Apache License 2.0',

    author='Ivan Korobkov',
    author_email='ivan.korobkov@gmail.com',

    description='Python dependency injection framework',
    long_description=read_description(),
    long_description_content_type="text/markdown",

    packages=['inject'],
    package_data={'inject': ['py.typed']},
    zip_safe=False,
    
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules']
)
