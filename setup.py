from setuptools import find_packages, setup

setup(
    name='SetFromConfigPlugin', version='0.0.1',
    #packages=find_packages(exclude=['*.tests*']),
    packages=find_packages(),
    entry_points = {
        'trac.plugins': [
            'setfromconfig = setfromconfig.setfromconfig',
        ],
    },
)

