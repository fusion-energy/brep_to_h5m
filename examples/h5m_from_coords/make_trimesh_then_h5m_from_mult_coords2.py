import numpy as np
import trimesh

from typing import Tuple

import gmsh
import numpy as np
import trimesh
from pymoab import core, types
import numpy as np
import trimesh

def fix_normals(vertices, triangles):

    mesh = trimesh.Trimesh(
        vertices=vertices,
        faces=triangles
    )

    mesh.fix_normals()


    triangles = mesh.faces

    return triangles


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

triangles= fix_normals(vertices=vertices,triangles=triangles )





def _define_moab_core_and_tags() -> Tuple[core.Core, dict]:
    """Creates a MOAB Core instance which can be built up by adding sets of
    triangles to the instance

    Returns:
        (pymoab Core): A pymoab.core.Core() instance
        (pymoab tag_handle): A pymoab.core.tag_get_handle() instance
    """

    # create pymoab instance
    moab_core = core.Core()

    tags = dict()

    sense_tag_name = "GEOM_SENSE_2"
    sense_tag_size = 2
    tags["surf_sense"] = moab_core.tag_get_handle(
        sense_tag_name,
        sense_tag_size,
        types.MB_TYPE_HANDLE,
        types.MB_TAG_SPARSE,
        create_if_missing=True,
    )

    tags["category"] = moab_core.tag_get_handle(
        types.CATEGORY_TAG_NAME,
        types.CATEGORY_TAG_SIZE,
        types.MB_TYPE_OPAQUE,
        types.MB_TAG_SPARSE,
        create_if_missing=True,
    )

    tags["name"] = moab_core.tag_get_handle(
        types.NAME_TAG_NAME,
        types.NAME_TAG_SIZE,
        types.MB_TYPE_OPAQUE,
        types.MB_TAG_SPARSE,
        create_if_missing=True,
    )

    tags["geom_dimension"] = moab_core.tag_get_handle(
        types.GEOM_DIMENSION_TAG_NAME,
        1,
        types.MB_TYPE_INTEGER,
        types.MB_TAG_DENSE,
        create_if_missing=True,
    )

    # Global ID is a default tag, just need the name to retrieve
    tags["global_id"] = moab_core.tag_get_handle(types.GLOBAL_ID_TAG_NAME)

    return moab_core, tags


moab_core, tags = _define_moab_core_and_tags()

def prepare_moab_core(
    moab_core,
    surface_id = 1,
    volume_id = 1,
):

    surface_set = moab_core.create_meshset()
    volume_set = moab_core.create_meshset()

    # recent versions of MOAB handle this automatically
    # but best to go ahead and do it manually
    moab_core.tag_set_data(tags["global_id"], volume_set, volume_id)

    moab_core.tag_set_data(tags["global_id"], surface_set, surface_id)

    # set geom IDs
    moab_core.tag_set_data(tags["geom_dimension"], volume_set, 3)
    moab_core.tag_set_data(tags["geom_dimension"], surface_set, 2)

    # set category tag values
    moab_core.tag_set_data(tags["category"], volume_set, "Volume")
    moab_core.tag_set_data(tags["category"], surface_set, "Surface")

    # establish parent-child relationship
    moab_core.add_parent_child(volume_set, surface_set)

    # set surface sense
    sense_data = [volume_set, np.uint64(0)]
    moab_core.tag_set_data(tags["surf_sense"], surface_set, sense_data)

    return moab_core, surface_set, volume_set


def add_vertices_to_moab_core(moab_core,vertices, surface_set):

    moab_verts = moab_core.create_vertices(vertices)

    moab_core.add_entity(surface_set, moab_verts)
    return moab_core, moab_verts


def add_triangles_to_moab_core(triangles, moab_verts, volume_set):
    for triangle in triangles:

        tri = (
                moab_verts[int(triangle[0])],
                moab_verts[int(triangle[1])],
                moab_verts[int(triangle[2])]
            )

        moab_triangle = moab_core.create_element(types.MBTRI, tri)
        moab_core.add_entity(surface_set, moab_triangle)

    group_set = moab_core.create_meshset()

    moab_core.tag_set_data(tags["category"], group_set, "Group")

    moab_core.tag_set_data(tags["name"], group_set, "mat:dag_material_tag")

    moab_core.tag_set_data(tags["geom_dimension"], group_set, 4)

    moab_core.add_entity(group_set, volume_set)

    return moab_core


moab_core, surface_set, volume_set=prepare_moab_core(moab_core)

moab_core, moab_verts = add_vertices_to_moab_core(moab_core,vertices, surface_set)

moab_core = add_triangles_to_moab_core(triangles, moab_verts, volume_set)



all_sets = moab_core.get_entities_by_handle(0)

file_set = moab_core.create_meshset()

moab_core.add_entities(file_set, all_sets)

moab_core.write_file("dagmc_from_coords.h5m")
