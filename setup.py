#!/usr/bin/fades

# Copyright 2020 Facundo Batista
# For further info, check  https://github.com/facundobatista/simplecalc

import setuptools  # fades

with open("README.rst", "rt", encoding='utf8') as fh:
    long_description = fh.read()

with open("requirements.txt", "rt", encoding='utf8') as fh:
    requirements = fh.read().split('\n')

setuptools.setup(
    name="pysimplecalc",
    version="1",
    author="Facundo Batista",
    author_email="facundo@taniquetil.com.ar",
    description="A simple calculator, able to parse quite complex expressions",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/facundobatista/simplecalc",
    packages=setuptools.find_packages(),
    package_data={'': ["LICENSE", "requirements.txt"]},
    classifiers=[
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        'console_scripts': ["simplecalc = simplecalc:main"],
    },
    python_requires='>=3',
    install_requires=requirements,
)
