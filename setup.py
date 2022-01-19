import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="brep_to_dagmc",
    version="develop",
    summary="Convert Brep files to h5m files, DAGMC geometry",
    author="fusion-energy",
    description="A Python package for converting Brep files to DAGMC h5m files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fusion-energy/brep_to_h5m",
    packages=setuptools.find_packages(),
    zip_safe=True,
    package_dir={"brep_to_h5m": "brep_to_h5m"},
    package_data={
        "brep_to_dagmc": [
            "requirements.txt",
            "README.md",
            "LICENSE",
        ]
    },
    classifiers=[
        "Natural Language :: English",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    tests_require=["pytest-cov"],
    install_requires=[
        "gmsh",
        "trimesh",
        "brep_part_finder",
        "networkx",
        # "pymoab", is needed but not available on pip
        # pymoab can be install with Conda
    ],
)
