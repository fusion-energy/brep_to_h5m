import trimesh

import numpy as np


# a list of xyz coordinates
vertices = np.array([
    [0, 0, 0],
    [1, 0, 0],
    [0, 1, 0],  
    [0, 0, 1],  
    ],
    dtype="float64",
)

# the index of the coordinate that make up the corner of a triangle
triangles = np.array([
        [0,1,2],
        [3,1,2],
        [0,2,3],
        [0,1,3]
    ]
)

mesh = trimesh.Trimesh(
    vertices=vertices,
    faces=triangles
)
print(mesh.faces)
mesh.fix_normals()
print(mesh.faces)

triangles = mesh.faces
