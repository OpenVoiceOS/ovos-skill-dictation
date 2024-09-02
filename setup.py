#!/usr/bin/env python3
from setuptools import setup
from os.path import abspath, dirname, join, isfile, isdir
from os import walk
import os

# Define package information
SKILL_CLAZZ = "DictationSkill"  # Make sure it matches __init__.py class name
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


def get_version():
    """ Find the version of this skill"""
    version_file = join(dirname(__file__), 'version.py')
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if int(alpha):
        version += f"a{alpha}"
    return version

# Setup configuration
setup(
    name=PYPI_NAME,
    version=get_version(),
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
