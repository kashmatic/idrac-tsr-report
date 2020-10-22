
#!/usr/bin/env python3
"""
Setup tool for package tsr
"""

from setuptools import setup, find_packages

setup(
    name="tsr",
    version="1.0.0",
    include_package_data=True,
    install_requires=[
        'requests',
        'paramiko',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    packages=find_packages(),
    scripts=[
        'bin/tsr'
    ]
)
