from setuptools import setup, find_packages

setup(
    name='himawaripy',
    version='1.0',
    url='https://github.com/boramalper/himawaripy',
    author='Mert Bora Alper',
    author_email='bora@boramalper.org',
    license='MIT',
    description='Put near-realtime picture of Earth as your desktop background',
    long_description='himawaripy is a Python 3 script that fetches near-realtime (10 minutes delayed) picture of Earth as its taken by Himawari 8 (ひまわり8号) and sets it as your desktop background.',
    install_requires=["pillow",],
    packages=find_packages(),
    scripts={"himawaripy.py","utils.py",},
    entry_points={'console_scripts': ['himawaripy=himawaripy:main',],},
)
