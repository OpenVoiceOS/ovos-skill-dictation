from setuptools import setup
from os import getenv, path, walk

SKILL_NAME = "skill-ovos-dictation"
SKILL_PKG = SKILL_NAME.replace("-", "_")
# skill_id=package_name:SkillClass
PLUGIN_ENTRY_POINT = f"{SKILL_NAME}.openvoiceos={SKILL_PKG}:DictationSkill"
BASE_PATH = path.abspath(path.dirname(__file__))



def find_resource_files():
    resource_base_dirs = ("locale", "vocab", "dialog", "regex", "sounds")  # Removed "ui"
    base_dir = BASE_PATH
    package_data = ["skill.json"]
    for res in resource_base_dirs:
        if path.isdir(path.join(base_dir, res)):
            for directory, _, files in walk(path.join(base_dir, res)):
                if files:
                    package_data.append(path.join(directory.replace(base_dir, "").lstrip("/"), "*"))
    #    print(package_data)
    return package_data


with open(path.join(BASE_PATH, "README.md"), "r") as f:
    long_description = f.read()

with open(path.join(BASE_PATH, "version.py"), "r", encoding="utf-8") as v:
    for line in v.readlines():
        if line.startswith("__version__"):
            if '"' in line:
                version = line.split('"')[1]
            else:
                version = line.split("'")[1]

setup(
    name=f"{SKILL_NAME}",
    version=version,
    url=f"https://github.com/OpenVoiceOS/{SKILL_NAME}",
    license="Apache2",
    author="JarbasAI",
    author_email="jarbasai@mailfence.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={SKILL_PKG: ""},
    packages=[SKILL_PKG],
    package_data={SKILL_PKG: find_resource_files()},
    include_package_data=True,
    entry_points={"ovos.plugin.skill": PLUGIN_ENTRY_POINT},
)
