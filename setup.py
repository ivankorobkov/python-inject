from distutils.core import setup


setup(
      name='python-inject',
      version='2.0-beta',
      url='http://code.google.com/p/python-inject/',
      author='Ivan Korobkov',
      author_email='ivan.korobkov@gmail.com',
      description='Python dependency injection framework',
      license='MIT License',
      package_dir={'': 'src'},
      packages=['inject'],
      keywords=['injection', 'ioc', 'inversion of control',
                'dependency injection', 'loose coupling'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Libraries :: Python Modules'],
      long_description=open('README.rst', 'r').read()
)
