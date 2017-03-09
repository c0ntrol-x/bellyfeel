#!/usr/bin/env python
# -*- coding: utf-8 -*-


import ast
import os
from setuptools import setup, find_packages


local_file = lambda *f: \
    open(os.path.join(os.path.dirname(__file__), *f)).read()


class VersionFinder(ast.NodeVisitor):
    VARIABLE_NAME = 'version'

    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        try:
            if node.targets[0].id == self.VARIABLE_NAME:
                self.version = node.value.s
        except:
            pass


def read_version():
    finder = VersionFinder()
    finder.visit(ast.parse(local_file('bellyfeel', 'version.py')))
    return finder.version


def read_requirements():
    return local_file('requirements.txt').splitlines()


setup(
    name='bellyfeel',
    version=read_version(),
    description='Bellyfeel!',
    entry_points={
        'console_scripts': ['bellyfeel = bellyfeel.cli:main'],
    },
    author='D4v1ncy',
    author_email='d4v1ncy@protonmail.ch',
    packages=find_packages(exclude=['*tests*']),
    install_requires=read_requirements(),
    include_package_data=True,
    package_data={
        'bellyfeel': ' '.join([
            '*.cfg',
            '*.py',
            '*.rst',
            '*.txt',
            'COPYING',
            'bellyfeel/migrations',
            'bellyfeel/migrations/*',
            'bellyfeel/migrations/versions/*',
            'bellyfeel/static',
            'bellyfeel/static/*',
            'bellyfeel/static/dist',
            'bellyfeel/static/dist/*',
            'bellyfeel/templates',
            'bellyfeel/templates/*',
            'bellyfeel/templates/admin',
            'bellyfeel/templates/admin/*',
        ]),
    },
    zip_safe=False,
)
