from distutils.core import setup


def read_description():
    with open('README.rst', 'r') as f:
        return f.read()


setup(
    name='Inject',
    version='3.3.0',
    url='https://github.com/ivankorobkov/python-inject',
    license='Apache License 2.0',

    author='Ivan Korobkov',
    author_email='ivan.korobkov@gmail.com',

    description='Python dependency injection framework',
    long_description=read_description(),

    package_dir={'': 'src'},
    py_modules=['inject'],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules']
)
