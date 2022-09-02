import os
from vertices_to_h5m import vertices_to_h5m

import gmsh
import trimesh
import plotly.graph_objects as go
import numpy as np


# brep_filename = "test_two_cubes.brep"
brep_filename = "test_two_sep_cubes.brep"
# brep_filename = "one_cube.brep"

min_mesh_size = 2
max_mesh_size = 3
mesh_algorithm = 1


gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)
volumes = gmsh.model.occ.importShapes(brep_filename)
gmsh.model.occ.synchronize()

gmsh.option.setNumber("Mesh.Algorithm", mesh_algorithm)
gmsh.option.setNumber("Mesh.MeshSizeMin", min_mesh_size)
gmsh.option.setNumber("Mesh.MeshSizeMax", max_mesh_size)

all_coords = []
all_coords_by_vol = []
all_tris = []
n = 3

for dim_and_vol in volumes:
    vol_id = dim_and_vol[1]
    print("vol_id", vol_id)
    entities_in_volume = gmsh.model.getAdjacencies(3, vol_id)
    surfaces_in_volume = entities_in_volume[1]
    ps = gmsh.model.addPhysicalGroup(2, surfaces_in_volume)
    print("surfaces_in_volume", surfaces_in_volume)
    gmsh.model.setPhysicalName(2, ps, f"surfaces_on_volume_{vol_id}")

gmsh.model.mesh.generate(2)

nodes_in_each_pg = []
groups = gmsh.model.getPhysicalGroups()
for group in groups:
    dim = group[0]
    tag = group[1]

    surfaces = gmsh.model.getEntitiesForPhysicalGroup(dim, tag)

    nodes_in_all_surfaces = []
    for surface in surfaces:
        elementTypes, elementTags, nodeTags = gmsh.model.mesh.getElements(2, surface)
        nodeTags = nodeTags[0].tolist()
        shifted_node_tags = []
        for nodeTag in nodeTags:
            shifted_node_tags.append(nodeTag - 1)
        grouped_node_tags = [
            shifted_node_tags[i : i + n] for i in range(0, len(shifted_node_tags), n)
        ]
        # grouped_node_tags = [nodeTags[i : i + n] for i in range(0, len(nodeTags), n)]
        nodes_in_all_surfaces += grouped_node_tags
    nodes_in_each_pg.append(nodes_in_all_surfaces)

all_nodes, all_coords, _ = gmsh.model.mesh.getNodes()

GroupedCoords = [all_coords[i : i + n].tolist() for i in range(0, len(all_coords), n)]


vertices_to_h5m(
    vertices=GroupedCoords,
    triangles=nodes_in_each_pg,
    material_tags=["mat1", "mat2"],
    h5m_filename="two_volume_touching_face3.h5m",
)
