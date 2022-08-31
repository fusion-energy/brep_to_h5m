import os
from vertices_to_h5m import vertices_to_h5m

import gmsh
import trimesh
import io
import plotly.graph_objects as go
import numpy as np

def deserialize(filename):
    with open(filename, 'r') as file:
        mesh_str = file.read()
    mesh_ply_file_obj = io.BytesIO(mesh_str)
    mesh = trimesh.Trimesh(**trimesh.exchange.ply.load_ply(mesh_ply_file_obj))
    return mesh


brep_filename = "test_two_cubes.brep"
# brep_filename = "one_cube.brep"
brep_filename = "test_two_sep_cubes.brep"
min_mesh_size = 2
max_mesh_size = 3
mesh_algorithm = 1


gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)
# gmsh.model.add("made_with_brep_to_h5m_package")
volumes = gmsh.model.occ.importShapes(brep_filename)
gmsh.model.occ.synchronize()

gmsh.option.setNumber("Mesh.Algorithm", mesh_algorithm)
gmsh.option.setNumber("Mesh.MeshSizeMin", min_mesh_size)
gmsh.option.setNumber("Mesh.MeshSizeMax", max_mesh_size)
gmsh.model.mesh.generate(2)

all_coords = []
all_coords_by_vol = []
all_tris = []
n = 3

# for dim_and_vol in volumes:
    # vol_id = dim_and_vol[1]
    # print("vol_id", vol_id)
    # entities_in_volume = gmsh.model.getAdjacencies(3, vol_id)
    # surfaces_in_volume = entities_in_volume[1]
    # ps = gmsh.model.addPhysicalGroup(2, surfaces_in_volume)
    # print("surfaces_in_volume", surfaces_in_volume)
    # gmsh.model.setPhysicalName(2, ps, f"surfaces_on_volume_{vol_id}")

# for dim_and_vol in volumes:
    # vol_id = dim_and_vol[1]
    # nodeTagsOrg, coords = gmsh.model.mesh.getNodesForPhysicalGroup(dim=2, tag=vol_id)

gmsh.write("t20.msh")
trimesh_object = trimesh.load("t20.msh", process=False) #trimesh.interfaces.gmsh.load_gmsh
trimesh_object.faces
all_coords = trimesh_object.vertices
all_tris = trimesh_object.faces
trimesh_object.triangles # gives list of coordinates of each triangle
# merge_verticeslooks useful
#     coords = coords.tolist()
#     nodeTags = []
#     for tag in nodeTagsOrg:
#         tag = tag -1
#         nodeTags.append(int(tag))
#     GroupednodeTags = [nodeTags[i : i + n] for i in range(0, len(nodeTags), n)]

#     GroupednCoords = [coords[i : i + n] for i in range(0, len(coords), n)]

#     all_coords = all_coords + GroupednCoords
#     all_coords_by_vol.append(GroupednCoords)

#     for i, vert in enumerate(GroupednodeTags):
#         print(i, "GroupednodeTags", vert)
#     print()
#     all_tris.append(GroupednodeTags)

# a, b, c = gmsh.model.mesh.getNodes()  # retruns 36 coordinates
# all_coords = [b[i : i + n] for i in range(0, len(b), n)]

# x,y,z = [], [],[]
# for i, co in enumerate(all_coords):
#     print(i, co)
#     x.append(co[0])
#     y.append(co[1])
#     z.append(co[2])

# fig = go.Figure(data=[go.Scatter3d(x=x, y=y, z=z,
#                                    mode='markers')])
# fig.show()


# new_trimesh_object = trimesh.Trimesh(vertices=all_coords, faces=all_tris[0])
# new_trimesh_object.show()

# # This will produce a h5m file called two_volume_touching_face.h5m ready for use with DAGMC enabled codes
vertices_to_h5m(
    vertices=all_coords,
    triangles=all_tris,
    material_tags=["mat1"],
    h5m_filename="two_volume_touching_face.h5m",
)
# os.system("mbconvert two_volume_touching_face.h5m two_volume_touching_face.vtk")
