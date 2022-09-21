[![N|Python](https://www.python.org/static/community_logos/python-powered-w-100x40.png)](https://www.python.org)



[![CI with install](https://github.com/fusion-energy/brep_to_h5m/actions/workflows/ci_with_install.yml/badge.svg)](https://github.com/fusion-energy/brep_to_h5m/actions/workflows/ci_with_install.yml)

[![anaconda-publish](https://github.com/fusion-energy/brep_to_h5m/actions/workflows/anaconda-publish.yml/badge.svg)](https://github.com/fusion-energy/brep_to_h5m/actions/workflows/anaconda-publish.yml)
[![Upload Python Package](https://github.com/fusion-energy/brep_to_h5m/actions/workflows/python-publish.yml/badge.svg)](https://github.com/fusion-energy/brep_to_h5m/actions/workflows/python-publish.yml)

[![conda-publish](https://anaconda.org/fusion-energy/brep_to_h5m/badges/version.svg)](https://anaconda.org/fusion-energy/brep_to_h5m)
[![PyPI](https://img.shields.io/pypi/v/brep-to-h5m?color=brightgreen&label=pypi&logo=grebrightgreenen&logoColor=green)](https://pypi.org/project/brep_to_h5m/)

# brep_to_h5m

A Python package that converts Brep CAD geometry files to h5m geometry files compatible with DAGMC simulations.

The method uses gmsh to create a conformal mesh of the geometry.
The mesh is then converted into a h5m file using either the [vertices-to-h5m](https://github.com/fusion-energy/vertices_to_h5m) (default) or [stl-to-h5m](https://github.com/fusion-energy/stl_to_h5m) package.

# Installation (Conda)

Create a new enviroment and activate the enviroment.

```bash
conda create --name my_env
conda activate my_env
```

Then install this package
```bash
conda install -c fusion-energy -c conda-forge brep_to_h5m
```

The above command should also install ```moab``` and ```gmsh```

# Installation (Conda + pip)

Create a new enviroment and activate the enviroment.

```bash
conda create --name my_env
conda activate my_env
```

Install dependancies that are not installed with pip ([MOAB](https://bitbucket.org/fathomteam/moab) and [GMSH](https://gmsh.info/))
```bash
conda install -c conda-forge moab
conda install -c conda-forge gmsh
conda install -c conda-forge python-gmsh
```

Then install this package
```bash
pip install brep_to_h5m
```


# Usage

See the [examples](https://github.com/fusion-energy/brep_to_h5m/tree/main/examples) folder for a complete workflow from geometry creation to conversion to h5m and then use in and OpenMC simulation.

To make a Brep file with merged surfaces consider using the [Paramak](https://github.com/fusion-energy/paramak) as it has a ```export_brep``` method that merges the shared surfaces for Brep files.

Starting with a Brep file that has shared surfaces the following command should produce a DAGMC compatible h5m file.

```python
from brep_to_h5m import brep_to_h5m

brep_to_h5m(
    brep_filename='my_brep_file_with_merged_surfaces.brep',
    material_tags=[
        'material_for_volume_1',
        'material_for_volume_2',
        'material_for_volume_3',
        'material_for_volume_4',
        'material_for_volume_5',
        'material_for_volume_6',
        'material_for_volume_7',
        'material_for_volume_8',
    ],
    h5m_filename='dagmc.h5m',
    min_mesh_size= 30,
    max_mesh_size = 50,
    mesh_algorithm = 1,
)
```

The resulting ```dagmc.h5m``` file can now be used in neutronics simulation with [DAGMC](https://svalinn.github.io/DAGMC/) enabled transport codes.

# Acknowledgement

Many thanks to @makeclean for suggesting gmsh for meshing and Brep for the CAD file format. Also for showing the way forwards by starting [gmsh2dagmc](https://github.com/svalinn/gmsh2dagmc/tree/7934ff291af5e4aae680a895239159471994b025).
