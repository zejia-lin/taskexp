import re
import os
import logging
import io
from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext

ROOT_DIR = os.path.dirname(__file__)
logger = logging.getLogger(__name__)

def get_path(*filepath) -> str:
    return os.path.join(ROOT_DIR, *filepath)


def read_readme() -> str:
    """Read the README file if present."""
    p = get_path("README.md")
    if os.path.isfile(p):
        return io.open(get_path("README.md"), "r", encoding="utf-8").read()
    else:
        return ""


def find_version(filepath: str) -> str:
    with open(filepath) as fp:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                                  fp.read(), re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")


setup(
    name="taskexp",
    version=find_version(get_path("taskexp", "__init__.py")),
    author="Zejia Lin",
    description=("Parameterized loop for repeated experiement"),
    long_description=read_readme(),
    packages=find_packages(exclude=("test")),
    python_requires=">=3.8",
    install_requires=[],
)