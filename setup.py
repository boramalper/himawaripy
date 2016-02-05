from distutils.core import setup

files = ["himawaripy/*.py"]

setup(
    name = "himawaripy",
    version = "1",
    description = "Put near-realtime picture of Earth as your desktop background",
    packages = ['himawaripy'],
    package_data = {'himawaripy' : files },
    scripts = ["start"],
)
