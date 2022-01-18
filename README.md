# brep_to_h5m

A Python package that converts Brep CAD geometry files to h5m geometry files compatible with DAGMC simulations.

The method uses gmsh to create a conformal mesh of the geometry and then exports separate volumes to STL files.
The [stl-to-h5m](github.com/fusion-energy/stl_to_h5m) package then converts the non overlapping STL files into a h5m geometry.

# Installation

Create a new enviroment, activate the enviroment, install MOAB, GMSH and this package

```
conda create --name my_env
conda activate my_env
conda install -c conda-forge moab
sudo apt install python3-gmsh
pip install git+https://github.com/fusion-energy/brep_to_h5m
```


# Usage

See the [examples](https://github.com/fusion-energy/brep_to_h5m/tree/main/examples) folder for a complete workflow from geometry creation to conversion to h5m and then use in and OpenMC simulation.

To make a Brep file with merged surfaces consider using the [Paramak](https://github.com/fusion-energy/paramak) as it has a ```export_brep``` method that merges the shared surfaces for Brep files.

Starting with a Brep file that has shared surfaces the following command should produce a DAGMC compatible h5m file.

```python
from brep_to_h5m import brep_to_h5m

brep_to_h5m(
    brep_filename='my_brep_file_with_merged_surfaces.brep',
    volumes_with_tags={
        1: 'material_for_volume_1',
        2: 'material_for_volume_2',
        3: 'material_for_volume_3',
        4: 'material_for_volume_4',
        5: 'material_for_volume_5',
        6: 'material_for_volume_6',
        7: 'material_for_volume_7',
        8: 'material_for_volume_8',
    },
    h5m_filename='dagmc.h5m',
    min_mesh_size= 30,
    max_mesh_size = 50,
    mesh_algorithm = 1,
)
```

The resulting ```dagmc.h5m``` file can now be used in neutronics simulation with [DAGMC](https://svalinn.github.io/DAGMC/) enabled transport codes.

# Acknowledgement

Many thanks to @makeclean for suggesting gmsh for meshing and Brep for the CAD file format. Also for showing the way forwards by starting [gmsh2dagmc](https://github.com/svalinn/gmsh2dagmc/tree/7934ff291af5e4aae680a895239159471994b025).
