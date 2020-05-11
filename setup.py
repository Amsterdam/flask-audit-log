import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

import flask_audit_log


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


install_requirements = [
    'flask',
    'datapunt-audit-log'
]

test_requirements = [
    'pytest',
    'pytest-cov'
]

extra_requirements = {
    'dev': test_requirements + ['twine', 'bump2version'],
}

setup(
    name='datapunt-flask-audit-log',
    version=flask_audit_log.__version__,
    license='Mozilla Public License 2.0',

    author='Datapunt Amsterdam',
    author_email='datapunt@amsterdam.nl',

    description='A simple Flask app to enable audit logging',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/Amsterdam/auditlog',

    packages=find_packages(),
    install_requires=install_requirements,

    cmdclass={'test': PyTest},
    tests_require=test_requirements,

    extras_require=extra_requirements,

    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Framework :: Flask :: 1.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: System :: Logging'
    ],
)
