from distutils.core import setup


setup(
      name='python-inject',
      version='3.0.0',
      url='https://github.com/ivan-korobkov/python-inject',
      license='Apache License 2.0',

      author='Ivan Korobkov',
      author_email='ivan.korobkov@gmail.com',

      description='Python dependency injection framework',
      long_description=open('README.rst', 'r').read(),

      package_dir={'': 'src'},
      py_modules=['inject'],

      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License 2.0',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules']
)
