from setuptools import find_packages, setup

setup(
    name='TicketFieldConfigPlugin', version='0.0.2',
    #packages=find_packages(exclude=['*.tests*']),
    packages=find_packages(),
    entry_points = {
        'trac.plugins': [
            'ticketfieldconfig = ticketfieldconfig',
            'jsontracadmin = jsontracadmin.jsontracadmin',
        ],
    },
)

