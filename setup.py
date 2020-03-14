from setuptools import setup, find_packages


REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]

setup(
    name="pytestReleaseSpecs",
    packages=find_packages(),
    install_requires=REQUIREMENTS
    )
