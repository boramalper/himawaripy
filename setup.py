import os
import re

from setuptools import setup, find_packages

with open(os.path.join("himawaripy", "himawaripy.py"), "rt") as f:
  version = re.search("__version__ = \"([^\"]+)\"", f.read()).group(1)

with open("requirements.txt", "rt") as f:
  requirements = f.read().splitlines()

try:
  import pypandoc
  readme = pypandoc.convert("README.md", "rst")
except ImportError:
  with open("README.md", "rt") as f:
    readme = f.read()


setup(
    name='himawaripy',
    version=version,
    url='https://github.com/boramalper/himawaripy',
    author='Mert Bora Alper',
    author_email='bora@boramalper.org',
    license='MIT',
    description='Put near-realtime picture of Earth as your desktop background',
    long_description=readme,
    install_requires=requirements,
    packages=find_packages(),
    entry_points={'console_scripts': ['himawaripy=himawaripy.himawaripy:main']},
    download_url="https://github.com/boramalper/himawaripy/archive/%s.tar.gz" % (version),
    keywords=["download", "image", "earth", "wallpaper", "himawari"],
    classifiers=["Development Status :: 3 - Alpha",
                 "Environment :: Console",
                 "Intended Audience :: End Users/Desktop",
                 "License :: OSI Approved :: MIT License",
                 "Natural Language :: English",
                 "Operating System :: POSIX :: Linux",
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 3",
                 "Programming Language :: Python :: 3 :: Only",
                 "Topic :: Internet :: WWW/HTTP",
                 "Topic :: Multimedia :: Graphics",
                 "Topic :: Utilities"]
)
