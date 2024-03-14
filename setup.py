#!/usr/bin/env python3
from setuptools import setup
from os.path import abspath, dirname, join, isfile, isdir
from os import walk

# Define package information
SKILL_CLAZZ = "DictationSkill"  # Make sure it matches __init__.py class name
VERSION = "0.0.1"
URL = "https://github.com/OVOSHatchery/ovos-skill-dictation"
AUTHOR = "OpenVoiceOS"
EMAIL = "jarbasai@mailfence.com"
LICENSE = "Apache2.0"
DESCRIPTION = SKILL_CLAZZ # TODO

PYPI_NAME = URL.split("/")[-1]  # pip install PYPI_NAME

# Construct entry point for plugin
SKILL_ID = f"{PYPI_NAME.lower()}.{AUTHOR.lower()}"
SKILL_PKG = PYPI_NAME.lower().replace('-', '_')
PLUGIN_ENTRY_POINT = f"{SKILL_ID}={SKILL_PKG}:{SKILL_CLAZZ}"


# Function to parse requirements from file
def get_requirements(requirements_filename: str = "requirements.txt"):
    requirements_file = join(abspath(dirname(__file__)), requirements_filename)
    if isfile(requirements_file):
        with open(requirements_file, 'r', encoding='utf-8') as r:
            requirements = r.readlines()
        requirements = [r.strip() for r in requirements if r.strip() and not r.strip().startswith("#")]
        if 'MYCROFT_LOOSE_REQUIREMENTS' in os.environ:
            print('USING LOOSE REQUIREMENTS!')
            requirements = [r.replace('==', '>=').replace('~=', '>=') for r in requirements]
        return requirements
    return []


# Function to find resource files
def find_resource_files():
    resource_base_dirs = ("locale", "ui", "vocab", "dialog", "regex", "res")
    base_dir = abspath(dirname(__file__))
    package_data = ["*.json"]
    for res in resource_base_dirs:
        if isdir(join(base_dir, res)):
            for (directory, _, files) in walk(join(base_dir, res)):
                if files:
                    package_data.append(join(directory.replace(base_dir, "").lstrip('/'), '*'))
    return package_data


# Setup configuration
setup(
    name=PYPI_NAME,
    version=VERSION,
    description=DESCRIPTION,
    url=URL,
    author=AUTHOR,
    author_email=EMAIL,
    license=LICENSE,
    package_dir={SKILL_PKG: ""},
    package_data={SKILL_PKG: find_resource_files()},
    packages=[SKILL_PKG],
    include_package_data=True,
    install_requires=get_requirements(),
    keywords='ovos skill plugin',
    entry_points={'ovos.plugin.skill': PLUGIN_ENTRY_POINT}
)
