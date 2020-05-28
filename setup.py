#!/usr/bin/env python

import setuptools

try:
    with open("README.md", "r") as f:
        long_description = f.read()
except:
    long_description=""

setuptools.setup(
        name="pimsgboard",
        version="0.0.1a1",
        author="Ian Taylor",
        author_email="ian@iantaylor.xyz",
        description="Message board application based on the Sense Hat",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/ianmtaylor1/pimsgboard",
        packages=setuptools.find_packages(),
        classifiers=[
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python :: 3.7"
        ],
        install_requires=[
            'sense-hat',
        ],
        include_package_data=True,
        entry_points={
            'console_scripts': [
                'pimsgboard = pimsgboard.main:main',
            ],
        }
)
