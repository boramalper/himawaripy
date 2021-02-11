from setuptools import setup, find_packages
import platform

with open("README.md", "r", encoding='UTF-8') as f:
    long_description = f.read()

install_requires = ["appdirs", "pillow", "python-dateutil"]
sys = platform.system()
if sys == "Windows":
    install_requires.append("pypiwin32")

setup(
    name="himawaripy",
    version="2.2.0",
    url="https://labs.boramalper.org/himawaripy",
    author="Bora M. Alper",
    author_email="bora@boramalper.org",
    license="MIT",
    description="himawaripy is a Python 3 script that fetches near-realtime (10 minutes delayed) picture of Earth "
                "as its taken by Himawari 8 (ひまわり8号) and sets it as your desktop background.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    packages=find_packages(),
    entry_points={"console_scripts": ["himawaripy=himawaripy.__main__:main"]},
)
