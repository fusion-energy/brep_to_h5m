import os
import tempfile
import warnings

import gmsh
import trimesh


brep_filename = "single_cube.brep"
min_mesh_size = 5
max_mesh_size = 10
mesh_algorithm = 1
volumes_with_tags = {
    1: "vol1",
}


gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)
gmsh.model.add("made_with_brep_to_h5m_package")
volumes = gmsh.model.occ.importShapes(brep_filename)
gmsh.model.occ.synchronize()

vols_in_brep = len(volumes)
vols_provided_by_user = len(volumes_with_tags.keys())

if vols_in_brep != vols_provided_by_user:
    msg = f"{vols_in_brep} volumes found in Brep file but only {vols_provided_by_user} volumes provided in volumes_with_tags argument."
    warnings.warn(msg)

if vols_in_brep < vols_provided_by_user:
    msg = f"The Brep file contains {vols_in_brep} volumes but {vols_provided_by_user} volumes are provided in the volumes_with_tags argument. Please reduce the number of volumes in volumes_with_tags"
    raise ValueError(msg)

gmsh.option.setNumber("Mesh.Algorithm", mesh_algorithm)
gmsh.option.setNumber("Mesh.MeshSizeMin", min_mesh_size)
gmsh.option.setNumber("Mesh.MeshSizeMax", max_mesh_size)
gmsh.model.mesh.generate(2)

# todo add Physical group before meshing
n = 3

all_coords = gmsh.model.mesh.getNodes()[1]

print(all_coords)
types, element_ids, node_ids_in_volumes = gmsh.model.mesh.getElements(dim=2)

node_ids = node_ids_in_volumes[0]  # just volume 0

all_coords.reshape(int(len(all_coords) / 3), 3)
node_ids.reshape(int(len(node_id) / 3), 3)
