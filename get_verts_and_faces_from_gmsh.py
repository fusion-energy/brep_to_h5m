import os
import tempfile
import warnings

import gmsh
import trimesh
from brep_to_h5m import mesh_brep


# gmsh, volumes = mesh_brep(
#         brep_filename='test_two_cubes.brep',
#         min_mesh_size=5,
#         max_mesh_size=10,
#         mesh_algorithm=1,
#         volumes_with_tags={
#             1:'vol1',
#             2:'vol2',
#         },
#     )

brep_filename = "test_two_cubes.brep"
min_mesh_size = 5
max_mesh_size = 10
mesh_algorithm = 1
volumes_with_tags = {
    1: "vol1",
    2: "vol2",
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
# all_coords = gmsh.model.mesh.getNodes()[1]
# AllGroupedcoords = [list(all_coords)[i: i + n] for i in range(0, len(all_coords), n)]

all_coords = []
for node_id in range(1, 63):
    coords = gmsh.model.mesh.getNode(node_id)[0]
    # print(f'node id {node_id} {}')
    all_coords.append(coords)
AllGroupedcoords = all_coords

stl_filenames = []
for dim_and_vol in volumes:
    vol_id = dim_and_vol[1]
    print("vol_id", vol_id)
    entities_in_volume = gmsh.model.getAdjacencies(3, vol_id)
    surfaces_in_volume = entities_in_volume[1]
    ps = gmsh.model.addPhysicalGroup(2, surfaces_in_volume)
    gmsh.model.setPhysicalName(2, ps, f"surfaces_on_volume_{vol_id}")

    # element_ids is equivalent to face ids
    types, element_ids, node_ids = gmsh.model.mesh.getElements(dim=2, tag=vol_id)
    node_ids = node_ids[0]
    element_ids = element_ids[0]

    # for node_id in node_ids:
    #     print(f'node id {node_id} {gmsh.model.mesh.getNode(node_id)[0]}')

    nodeTags, coords = gmsh.model.mesh.getNodesForPhysicalGroup(dim=2, tag=vol_id)
    Groupedcoords = [list(coords)[i : i + n] for i in range(0, len(coords), n)]

    # GroupednodeTags = [list(nodeTags)[i : i + n] for i in range(0, len(nodeTags), n)]
    Groupednodes = [list(node_ids)[i : i + n] for i in range(0, len(node_ids), n)]
    # Groupedelements = [list(all_elements)[i : i + n] for i in range(0, len(coords), n)]
    print("  nodeTags", nodeTags)
    print("  coords", coords)
    # print("  GroupednodeTags", GroupednodeTags)
    print("  Groupedcoords", Groupedcoords)
    mesh = trimesh.Trimesh(vertices=AllGroupedcoords, faces=Groupednodes)
    # mesh.show()
    # e=gmsh.model.getEntitiesForPhysicalGroup(dim=2, tag=1)
    # print('e',e)
    # elementTags, elementNodeTags = gmsh.model.mesh.getElementsByType(3)
    # print('elementTags', elementTags)
    # print('elementNodeTags', elementNodeTags)
    # f=gmsh.model.mesh.getFaces(3,[nodeTags[0], nodeTags[1], nodeTags[2]])
    # print(   'face', f)
    # gmsh.model.mesh.getElementsByCoordinates(x=coords[0], y=coords[1],z=coords[2])?
    # gmsh.write(tmp_filename)
    # stl_filenames.append((vol_id, verts, faces))
    gmsh.model.removePhysicalGroups([])  # removes all groups
# gmsh.finalize()

# example
# import numpy as np
# import trimesh
# corners = np.array([
#         [0, 0, 0],
#         [0, 0, 1],
#         [0, 1, 0],
#         [0, 1, 1],
#         [1, 0, 0],
#         [1, 0, 1],
#         [1, 1, 0],
#         [1, 1, 1]
#     ])
# mesh = trimesh.Trimesh(
#         vertices=corners,
#         faces=[[0, 1, 2], [2, 3, 4], [4, 5, 6], [6, 7, 0]])
# mesh.show()
