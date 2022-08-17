# import os
# import tempfile
import imp
import warnings

import gmsh
import trimesh
# from vertices_to_h5m import vertices_to_h5m
# from brep_to_h5m import messh_brep


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

all_coords = []
stl_filenames = []
all_tris=[]
for dim_and_vol in volumes:
    vol_id = dim_and_vol[1]
    print("vol_id", vol_id)
    entities_in_volume = gmsh.model.getAdjacencies(3, vol_id)
    surfaces_in_volume = entities_in_volume[1]
    ps = gmsh.model.addPhysicalGroup(2, surfaces_in_volume)
    gmsh.model.setPhysicalName(2, ps, f"surfaces_on_volume_{vol_id}")

    nodeTagsOrg, coords=gmsh.model.mesh.getNodesForPhysicalGroup(dim=2,tag=vol_id)
    n=3
    coords= coords.tolist()
    nodeTags = []
    for tag in nodeTagsOrg:
        tag=tag-1
        nodeTags.append(int(tag))
    GroupednodeTags=[nodeTags[i:i+n] for i in range(0, len(nodeTags), n)]
    
    GroupednCoords=[coords[i:i+n] for i in range(0, len(coords), n)]
    # print('  nodeTags', nodeTags)
    # print('  GroupednodeTags', GroupednodeTags)
    # print('  coords', coords)
    new_trimesh_object=trimesh.Trimesh(vertices=coords,faces=GroupednodeTags)
    # new_trimesh_object.show()
    # trimesh.repair.fix_normals(new_trimesh_object) 

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

    # gmsh.model.removePhysicalGroups([])  # removes all groups
    all_coords = all_coords + GroupednCoords
    all_tris.append(GroupednodeTags)
    
gmsh.finalize()


print('all_tris',all_tris)
print('all_coords',all_coords)

# from vertices_to_h5m import vertices_to_h5m
# import numpy as np
# import os

# # These are the x,y,z coordinates of each vertex.
# # The first 4 are used in the first volume
# vertices = all_coords
# # These are the two sets triangle that connect individual vertices together to form a continious surfaces and also two closed volume.
# triangles = all_tris

# # This will produce a h5m file called two_volume_touching_edge.h5m ready for use with DAGMC enabled codes
# vertices_to_h5m(
#     vertices=vertices,
#     triangles=triangles,
#     material_tags=["mat1", "mat2"],
#     h5m_filename="two_volume_touching_edge.h5m",
# )

# os.system("mbconvert two_volume_touching_edge.h5m two_volume_touching_edge.vtk")

